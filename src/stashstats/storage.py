"""Multi-user data storage and isolated filesystem management."""

import io
import json
import logging
import os
from pathlib import Path
from typing import Any

from minio import Minio

logger = logging.getLogger("stashstats.storage")

DEFAULT_DATA_DIR = Path("data")
DEFAULT_MINIO_BUCKET = os.getenv("MINIO_BUCKET", "stashstats-pdfs")


def get_minio_client() -> Minio:
    """Initialize and return a MinIO client from environment variables.

    Returns:
        Configured Minio client instance.
    """
    endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "stashstats")
    secret_key = os.getenv("MINIO_SECRET_KEY", "stashstats123")
    secure = os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "yes")
    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
    )

def get_user_data_dir(user_id: str | int, base_dir: Path | str = DEFAULT_DATA_DIR) -> Path:
    """Retrieve and ensure existence of user-isolated data directory.

    Args:
        user_id: Unique user identifier or username.
        base_dir: Root storage base directory (defaults to 'data').

    Returns:
        Path to the user's isolated directory.
    """
    user_dir = Path(base_dir) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_storage_path(user_id: str | int, filename: str, base_dir: Path | str = DEFAULT_DATA_DIR) -> Path:
    """Retrieve full path for a file stored under a specific user directory.

    Args:
        user_id: Unique user identifier or username.
        filename: Name of the target file.
        base_dir: Root storage base directory.

    Returns:
        Path object pointing to the file.
    """
    user_dir = get_user_data_dir(user_id, base_dir=base_dir)
    return user_dir / filename


def save_user_json(
    user_id: str | int,
    filename: str,
    data: Any,
    base_dir: Path | str = DEFAULT_DATA_DIR,
    indent: int = 2,
) -> Path:
    """Serialize and save data to a user-isolated JSON file.

    Args:
        user_id: Unique user identifier or username.
        filename: Destination JSON filename.
        data: Serializable data structure.
        base_dir: Root storage base directory.
        indent: JSON indentation formatting.

    Returns:
        Path to the written JSON file.
    """
    filepath = get_user_storage_path(user_id, filename, base_dir=base_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)
    logger.debug(f"[STORAGE WRITE] user_id={user_id} file={filepath}")
    return filepath


def load_user_json(
    user_id: str | int,
    filename: str,
    default: Any = None,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> Any:
    """Load deserialized data from a user-isolated JSON file.

    Args:
        user_id: Unique user identifier or username.
        filename: Target JSON filename.
        default: Fallback value if the file does not exist or is invalid.
        base_dir: Root storage base directory.

    Returns:
        Loaded JSON data or the specified default value.
    """
    filepath = get_user_storage_path(user_id, filename, base_dir=base_dir)
    if not filepath.exists():
        logger.debug(f"[STORAGE MISS] user_id={user_id} file={filepath}")
        return default

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"[STORAGE READ] user_id={user_id} file={filepath}")
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"[STORAGE ERROR] Failed reading {filepath}: {e}")
        return default


def delete_user_file(
    user_id: str | int,
    filename: str,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> bool:
    """Delete a user-isolated file if it exists.

    Args:
        user_id: Unique user identifier or username.
        filename: Name of file to delete.
        base_dir: Root storage base directory.

    Returns:
        True if deleted, False if file did not exist.
    """
    filepath = get_user_storage_path(user_id, filename, base_dir=base_dir)
    if filepath.exists():
        filepath.unlink()
        logger.debug(f"[STORAGE DELETE] user_id={user_id} file={filepath}")
        return True
    return False


def list_user_files(
    user_id: str | int,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> list[str]:
    """List all filenames present in a user's isolated directory.

    Args:
        user_id: Unique user identifier or username.
        base_dir: Root storage base directory.

    Returns:
        List of filenames contained in the user directory.
    """
    user_dir = get_user_data_dir(user_id, base_dir=base_dir)
    return [p.name for p in user_dir.iterdir() if p.is_file()]


def get_user_db_path(
    user_id: str | int,
    db_name: str = "user.db",
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> Path:
    """Retrieve path for a user's isolated SQLite database file.

    Args:
        user_id: Unique user identifier or username.
        db_name: Database filename.
        base_dir: Root storage base directory.

    Returns:
        Path to the database file within the user directory.
    """
    return get_user_storage_path(user_id, db_name, base_dir=base_dir)


# ---------------------------------------------------------------------------
# Project PDF storage utilities
# ---------------------------------------------------------------------------

def sanitise_pdf_filename(filename: str) -> str:
    """Sanitise an uploaded PDF filename for safe filesystem storage.

    Removes path separators, null bytes, and replaces spaces with underscores.
    Returns a non-empty string — falls back to 'upload.pdf' when the result is empty.

    Args:
        filename: Raw filename supplied by the client.

    Returns:
        Sanitised filename string safe for use as a filesystem basename.
    """
    cleaned = filename.replace("\x00", "")
    safe_name = Path(cleaned.replace("\\", "/")).name
    safe_name = safe_name.replace(" ", "_")
    if safe_name in ("", ".", ".."):
        return "upload.pdf"
    return safe_name


def save_project_pdf(
    user_id: str | int,
    project_id: str | int,
    filename: str,
    content: bytes,
    base_dir: Path | str | None = None,
    bucket: str = DEFAULT_MINIO_BUCKET,
    client: Minio | None = None,
) -> str:
    """Save PDF bytes to MinIO object storage.

    Sanitises the filename before writing. Overwrites any existing object with
    the same sanitised name.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        filename: Original filename (will be sanitised).
        content: Raw PDF bytes.
        base_dir: Unused legacy base directory argument for backwards compatibility.
        bucket: MinIO bucket name (defaults to DEFAULT_MINIO_BUCKET).
        client: Optional Minio client instance.

    Returns:
        Object name / key in MinIO.
    """
    safe_name = sanitise_pdf_filename(filename)
    object_name = f"{user_id}/projects/pdfs/{project_id}/{safe_name}"
    try:
        if client is None:
            client = get_minio_client()
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        client.put_object(
            bucket,
            object_name,
            io.BytesIO(content),
            len(content),
            content_type="application/pdf",
        )
        logger.debug(f"[PDF WRITE] user_id={user_id} project_id={project_id} object={object_name}")
        return object_name
    except Exception as e:
        logger.error(f"[PDF WRITE ERROR] user_id={user_id} project_id={project_id} object={object_name}: {e}")
        raise


def list_project_pdfs(
    user_id: str | int,
    project_id: str | int,
    base_dir: Path | str | None = None,
    bucket: str = DEFAULT_MINIO_BUCKET,
    client: Minio | None = None,
) -> list[str]:
    """List PDF filenames attached to a project, sorted alphabetically.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        base_dir: Unused legacy base directory argument for backwards compatibility.
        bucket: MinIO bucket name (defaults to DEFAULT_MINIO_BUCKET).
        client: Optional Minio client instance.

    Returns:
        Sorted list of PDF filenames. Empty list when no files exist or on error.
    """
    if client is None:
        client = get_minio_client()
    prefix = f"{user_id}/projects/pdfs/{project_id}/"
    try:
        if not client.bucket_exists(bucket):
            return []
        objects = client.list_objects(bucket, prefix=prefix, recursive=True)
        filenames = [
            os.path.basename(obj.object_name)
            for obj in objects
            if os.path.basename(obj.object_name)
        ]
        return sorted(filenames)
    except Exception as e:
        logger.warning(f"[PDF LIST ERROR] user_id={user_id} project_id={project_id}: {e}")
        return []


def delete_project_pdf(
    user_id: str | int,
    project_id: str | int,
    filename: str,
    base_dir: Path | str | None = None,
    bucket: str = DEFAULT_MINIO_BUCKET,
    client: Minio | None = None,
) -> bool:
    """Delete a named PDF from the user+project MinIO storage.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        filename: Exact filename to delete.
        base_dir: Unused legacy base directory argument for backwards compatibility.
        bucket: MinIO bucket name (defaults to DEFAULT_MINIO_BUCKET).
        client: Optional Minio client instance.

    Returns:
        True if the file was deleted, False if it did not exist or on error.
    """
    if client is None:
        client = get_minio_client()
    safe_name = sanitise_pdf_filename(filename)
    object_name = f"{user_id}/projects/pdfs/{project_id}/{safe_name}"
    try:
        client.stat_object(bucket, object_name)
        client.remove_object(bucket, object_name)
        logger.debug(f"[PDF DELETE] user_id={user_id} project_id={project_id} object={object_name}")
        return True
    except Exception as e:
        logger.warning(f"[PDF DELETE ERROR] user_id={user_id} project_id={project_id} object={object_name}: {e}")
        return False


def get_project_pdf_bytes(
    user_id: str | int,
    project_id: str | int,
    filename: str,
    base_dir: Path | str | None = None,
    bucket: str = DEFAULT_MINIO_BUCKET,
    client: Minio | None = None,
) -> bytes | None:
    """Retrieve raw PDF bytes from MinIO for a user and project.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        filename: Exact filename to retrieve.
        base_dir: Unused legacy base directory argument for backwards compatibility.
        bucket: MinIO bucket name (defaults to DEFAULT_MINIO_BUCKET).
        client: Optional Minio client instance.

    Returns:
        Raw bytes if object exists and was read successfully, otherwise None.
    """
    if client is None:
        client = get_minio_client()
    safe_name = sanitise_pdf_filename(filename)
    object_name = f"{user_id}/projects/pdfs/{project_id}/{safe_name}"
    response = None
    try:
        response = client.get_object(bucket, object_name)
        return response.read()
    except Exception as e:
        logger.warning(f"[PDF GET ERROR] user_id={user_id} project_id={project_id} object={object_name}: {e}")
        return None
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass
            try:
                response.release_conn()
            except Exception:
                pass
