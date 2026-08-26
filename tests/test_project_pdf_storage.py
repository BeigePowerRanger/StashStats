"""Tests for MinIO project PDF storage utilities and PDF serve route."""

import io
from unittest.mock import MagicMock, patch

import pytest

from stashstats.storage import (
    delete_project_pdf,
    get_project_pdf_bytes,
    list_project_pdfs,
    sanitise_pdf_filename,
    save_project_pdf,
)


# ---------------------------------------------------------------------------
# Helpers & Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PDF_BYTES = b"%PDF-1.4 sample content"
DEFAULT_BUCKET = "stashstats-pdfs"


@pytest.fixture
def mock_minio_client():
    """Return a mock Minio client with bucket_exists returning True by default."""
    client = MagicMock()
    client.bucket_exists.return_value = True
    return client


# ---------------------------------------------------------------------------
# TestSanitisePdfFilename
# ---------------------------------------------------------------------------

class TestSanitisePdfFilename:
    def test_strips_path_separators(self):
        assert "/" not in sanitise_pdf_filename("../../evil/path.pdf")
        assert "\\" not in sanitise_pdf_filename("..\\evil\\path.pdf")

    def test_replaces_spaces(self):
        result = sanitise_pdf_filename("my pattern.pdf")
        assert " " not in result
        assert "my_pattern.pdf" == result

    def test_strips_null_bytes(self):
        result = sanitise_pdf_filename("file\x00name.pdf")
        assert "\x00" not in result

    def test_preserves_legal_characters(self):
        assert sanitise_pdf_filename("pattern-v2.0.pdf") == "pattern-v2.0.pdf"

    def test_empty_string_fallback(self):
        result = sanitise_pdf_filename("")
        assert result  # non-empty fallback


# ---------------------------------------------------------------------------
# TestSaveProjectPdf
# ---------------------------------------------------------------------------

class TestSaveProjectPdf:
    def test_saves_bytes_to_correct_object_key(self, mock_minio_client):
        result = save_project_pdf(
            "alice",
            "proj123",
            "pattern.pdf",
            SAMPLE_PDF_BYTES,
            bucket="custom-bucket",
            client=mock_minio_client,
        )
        expected_key = "alice/projects/pdfs/proj123/pattern.pdf"
        assert result == expected_key
        mock_minio_client.put_object.assert_called_once()
        args, kwargs = mock_minio_client.put_object.call_args
        bucket_arg = kwargs.get("bucket_name") or (args[0] if len(args) > 0 else None)
        object_arg = kwargs.get("object_name") or (args[1] if len(args) > 1 else None)
        assert bucket_arg == "custom-bucket"
        assert object_arg == expected_key

    def test_creates_bucket_if_not_exists(self, mock_minio_client):
        mock_minio_client.bucket_exists.return_value = False
        save_project_pdf(
            "alice",
            "proj123",
            "pattern.pdf",
            SAMPLE_PDF_BYTES,
            bucket="new-bucket",
            client=mock_minio_client,
        )
        mock_minio_client.bucket_exists.assert_called_once_with("new-bucket")
        mock_minio_client.make_bucket.assert_called_once_with("new-bucket")
        mock_minio_client.put_object.assert_called_once()

    def test_does_not_create_bucket_if_already_exists(self, mock_minio_client):
        mock_minio_client.bucket_exists.return_value = True
        save_project_pdf(
            "alice",
            "proj123",
            "pattern.pdf",
            SAMPLE_PDF_BYTES,
            bucket="existing-bucket",
            client=mock_minio_client,
        )
        mock_minio_client.bucket_exists.assert_called_once_with("existing-bucket")
        mock_minio_client.make_bucket.assert_not_called()
        mock_minio_client.put_object.assert_called_once()

    def test_sanitises_filename(self, mock_minio_client):
        result = save_project_pdf(
            "alice",
            "proj123",
            "my pattern.pdf",
            SAMPLE_PDF_BYTES,
            client=mock_minio_client,
        )
        expected_key = "alice/projects/pdfs/proj123/my_pattern.pdf"
        assert result == expected_key
        args, kwargs = mock_minio_client.put_object.call_args
        object_arg = kwargs.get("object_name") or (args[1] if len(args) > 1 else None)
        assert object_arg == expected_key

    def test_uses_default_bucket_when_omitted(self, mock_minio_client):
        save_project_pdf(
            "alice",
            "proj123",
            "pattern.pdf",
            SAMPLE_PDF_BYTES,
            client=mock_minio_client,
        )
        args, kwargs = mock_minio_client.put_object.call_args
        bucket_arg = kwargs.get("bucket_name") or (args[0] if len(args) > 0 else None)
        assert bucket_arg == DEFAULT_BUCKET


# ---------------------------------------------------------------------------
# TestListProjectPdfs
# ---------------------------------------------------------------------------

class TestListProjectPdfs:
    def test_returns_empty_when_no_objects(self, mock_minio_client):
        mock_minio_client.list_objects.return_value = []
        result = list_project_pdfs(
            "alice",
            "noproj",
            bucket="test-bucket",
            client=mock_minio_client,
        )
        assert result == []
        mock_minio_client.list_objects.assert_called_once_with(
            "test-bucket",
            prefix="alice/projects/pdfs/noproj/",
            recursive=True,
        )

    def test_returns_filenames_sorted(self, mock_minio_client):
        obj_b = MagicMock()
        obj_b.object_name = "alice/projects/pdfs/proj1/b.pdf"
        obj_a = MagicMock()
        obj_a.object_name = "alice/projects/pdfs/proj1/a.pdf"
        mock_minio_client.list_objects.return_value = [obj_b, obj_a]

        result = list_project_pdfs(
            "alice",
            "proj1",
            client=mock_minio_client,
        )
        assert result == ["a.pdf", "b.pdf"]

    def test_isolates_by_user_and_project_prefix(self, mock_minio_client):
        mock_minio_client.list_objects.return_value = []
        list_project_pdfs("bob", "proj42", client=mock_minio_client)
        mock_minio_client.list_objects.assert_called_once_with(
            DEFAULT_BUCKET,
            prefix="bob/projects/pdfs/proj42/",
            recursive=True,
        )

    def test_handles_client_exception_gracefully(self, mock_minio_client):
        mock_minio_client.list_objects.side_effect = Exception("MinIO error")
        result = list_project_pdfs("alice", "proj1", client=mock_minio_client)
        assert result == []


# ---------------------------------------------------------------------------
# TestDeleteProjectPdf
# ---------------------------------------------------------------------------

class TestDeleteProjectPdf:
    def test_deletes_object_successfully(self, mock_minio_client):
        result = delete_project_pdf(
            "alice",
            "proj1",
            "delete_me.pdf",
            bucket="custom-bucket",
            client=mock_minio_client,
        )
        assert result is True
        mock_minio_client.remove_object.assert_called_once_with(
            "custom-bucket",
            "alice/projects/pdfs/proj1/delete_me.pdf",
        )

    def test_uses_correct_object_key_and_default_bucket(self, mock_minio_client):
        result = delete_project_pdf(
            "bob",
            "proj99",
            "pattern.pdf",
            client=mock_minio_client,
        )
        assert result is True
        mock_minio_client.remove_object.assert_called_once_with(
            DEFAULT_BUCKET,
            "bob/projects/pdfs/proj99/pattern.pdf",
        )

    def test_returns_false_when_remove_fails(self, mock_minio_client):
        mock_minio_client.remove_object.side_effect = Exception("Object not found")
        result = delete_project_pdf(
            "alice",
            "proj1",
            "ghost.pdf",
            client=mock_minio_client,
        )
        assert result is False


# ---------------------------------------------------------------------------
# TestGetProjectPdfBytes
# ---------------------------------------------------------------------------

class TestGetProjectPdfBytes:
    def test_returns_bytes_when_object_exists(self, mock_minio_client):
        mock_response = MagicMock()
        mock_response.read.return_value = SAMPLE_PDF_BYTES
        mock_minio_client.get_object.return_value = mock_response

        result = get_project_pdf_bytes(
            "alice",
            "proj1",
            "pattern.pdf",
            bucket="custom-bucket",
            client=mock_minio_client,
        )
        assert result == SAMPLE_PDF_BYTES
        mock_minio_client.get_object.assert_called_once_with(
            "custom-bucket",
            "alice/projects/pdfs/proj1/pattern.pdf",
        )
        assert mock_response.close.called or mock_response.release_conn.called or mock_response.__exit__.called

    def test_uses_default_bucket(self, mock_minio_client):
        mock_response = MagicMock()
        mock_response.read.return_value = SAMPLE_PDF_BYTES
        mock_minio_client.get_object.return_value = mock_response

        result = get_project_pdf_bytes(
            "alice",
            "proj1",
            "pattern.pdf",
            client=mock_minio_client,
        )
        assert result == SAMPLE_PDF_BYTES
        mock_minio_client.get_object.assert_called_once_with(
            DEFAULT_BUCKET,
            "alice/projects/pdfs/proj1/pattern.pdf",
        )

    def test_returns_none_when_object_not_found(self, mock_minio_client):
        mock_minio_client.get_object.side_effect = Exception("NoSuchKey")
        result = get_project_pdf_bytes(
            "alice",
            "proj1",
            "nonexistent.pdf",
            client=mock_minio_client,
        )
        assert result is None

    def test_releases_connection_even_on_read_failure(self, mock_minio_client):
        mock_response = MagicMock()
        mock_response.read.side_effect = Exception("Stream read failure")
        mock_minio_client.get_object.return_value = mock_response

        result = get_project_pdf_bytes(
            "alice",
            "proj1",
            "corrupt.pdf",
            client=mock_minio_client,
        )
        assert result is None
        assert mock_response.close.called or mock_response.release_conn.called or mock_response.__exit__.called


# ---------------------------------------------------------------------------
# TestPdfServeRoute
# ---------------------------------------------------------------------------

class TestPdfServeRoute:
    """Integration-style tests for the /projects/pdf/ server route with mocked storage backend."""

    @patch("stashstats.storage.get_project_pdf_bytes")
    def test_route_returns_pdf_bytes_when_pdf_exists(self, mock_get_bytes, tmp_path):
        """The serve route should return 200 with application/pdf and bytes when PDF exists."""
        mock_get_bytes.return_value = SAMPLE_PDF_BYTES

        from stashstats.web.app import create_app

        app = create_app(assets_folder=str(tmp_path))
        client = app.server.test_client()

        response = client.get("/projects/pdf/alice/proj1/pattern.pdf")
        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data == SAMPLE_PDF_BYTES
        mock_get_bytes.assert_called_once_with("alice", "proj1", "pattern.pdf")

    @patch("stashstats.storage.get_project_pdf_bytes")
    def test_route_returns_404_when_pdf_not_found(self, mock_get_bytes, tmp_path):
        """The serve route should return 404 when get_project_pdf_bytes returns None."""
        mock_get_bytes.return_value = None

        from stashstats.web.app import create_app

        app = create_app(assets_folder=str(tmp_path))
        client = app.server.test_client()

        response = client.get("/projects/pdf/alice/proj1/nonexistent.pdf")
        assert response.status_code == 404
        mock_get_bytes.assert_called_once_with("alice", "proj1", "nonexistent.pdf")

    @patch("stashstats.storage.get_project_pdf_bytes")
    def test_route_returns_400_on_path_traversal_or_invalid_segments(self, mock_get_bytes, tmp_path):
        """The serve route must reject path traversal or invalid path segments with 400."""
        from stashstats.web.app import create_app

        app = create_app(assets_folder=str(tmp_path))
        client = app.server.test_client()

        # URL-encoded path traversal attempt
        response = client.get("/projects/pdf/alice/proj1/%2E%2E%2Fsecret.pdf")
        assert response.status_code == 400
        mock_get_bytes.assert_not_called()
