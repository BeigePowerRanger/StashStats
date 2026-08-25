"""Multi-user data storage and isolated filesystem management."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("stashstats.storage")

DEFAULT_DATA_DIR = Path("data")


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
    # Strip null bytes
    cleaned = filename.replace("\x00", "")
    # Strip any path component (keep only basename portion)
    cleaned = cleaned.replace("/", "").replace("\\", "")
    # Replace spaces with underscores
    cleaned = cleaned.replace(" ", "_")
    return cleaned or "upload.pdf"


def _get_project_pdf_dir(
    user_id: str | int,
    project_id: str | int,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> Path:
    """Return (and create) the user+project PDF directory.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        base_dir: Root storage base directory.

    Returns:
        Path to `<base_dir>/<user_id>/projects/pdfs/<project_id>/`.
    """
    pdf_dir = Path(base_dir) / str(user_id) / "projects" / "pdfs" / str(project_id)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir


def save_project_pdf(
    user_id: str | int,
    project_id: str | int,
    filename: str,
    content: bytes,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> Path:
    """Save PDF bytes to the user+project PDF directory.

    Sanitises the filename before writing.  Overwrites any existing file with
    the same sanitised name.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        filename: Original filename (will be sanitised).
        content: Raw PDF bytes.
        base_dir: Root storage base directory.

    Returns:
        Path to the written file.
    """
    safe_name = sanitise_pdf_filename(filename)
    pdf_dir = _get_project_pdf_dir(user_id, project_id, base_dir=base_dir)
    filepath = pdf_dir / safe_name
    filepath.write_bytes(content)
    logger.debug(f"[PDF WRITE] user_id={user_id} project_id={project_id} file={filepath}")
    return filepath


def list_project_pdfs(
    user_id: str | int,
    project_id: str | int,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> list[str]:
    """List PDF filenames attached to a project, sorted alphabetically.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        base_dir: Root storage base directory.

    Returns:
        Sorted list of PDF filenames.  Empty list when no files exist.
    """
    pdf_dir = Path(base_dir) / str(user_id) / "projects" / "pdfs" / str(project_id)
    if not pdf_dir.exists():
        return []
    return sorted(p.name for p in pdf_dir.iterdir() if p.is_file())


def delete_project_pdf(
    user_id: str | int,
    project_id: str | int,
    filename: str,
    base_dir: Path | str = DEFAULT_DATA_DIR,
) -> bool:
    """Delete a named PDF from the user+project PDF directory.

    Args:
        user_id: Unique user identifier.
        project_id: Unique project identifier.
        filename: Exact filename to delete (not re-sanitised).
        base_dir: Root storage base directory.

    Returns:
        True if the file was deleted, False if it did not exist.
    """
    pdf_dir = Path(base_dir) / str(user_id) / "projects" / "pdfs" / str(project_id)
    filepath = pdf_dir / filename
    if filepath.exists():
        filepath.unlink()
        logger.debug(f"[PDF DELETE] user_id={user_id} project_id={project_id} file={filepath}")
        return True
    return False
