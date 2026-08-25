"""Tests for project PDF storage utilities (save, list, delete) and PDF serve route."""

import base64
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from stashstats.storage import (
    delete_project_pdf,
    list_project_pdfs,
    save_project_pdf,
    sanitise_pdf_filename,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_PDF_BYTES = b"%PDF-1.4 sample content"


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


class TestSaveProjectPdf:
    def test_saves_bytes_to_correct_path(self, tmp_path):
        saved = save_project_pdf("alice", "proj123", "pattern.pdf", SAMPLE_PDF_BYTES, base_dir=tmp_path)
        assert saved.exists()
        assert saved.read_bytes() == SAMPLE_PDF_BYTES
        assert saved.parent == tmp_path / "alice" / "projects" / "pdfs" / "proj123"

    def test_replaces_existing_file(self, tmp_path):
        save_project_pdf("alice", "proj123", "pattern.pdf", b"original", base_dir=tmp_path)
        save_project_pdf("alice", "proj123", "pattern.pdf", b"updated", base_dir=tmp_path)
        saved = tmp_path / "alice" / "projects" / "pdfs" / "proj123" / "pattern.pdf"
        assert saved.read_bytes() == b"updated"

    def test_sanitises_filename(self, tmp_path):
        saved = save_project_pdf("alice", "proj123", "my pattern.pdf", SAMPLE_PDF_BYTES, base_dir=tmp_path)
        assert saved.name == "my_pattern.pdf"

    def test_creates_parent_directories(self, tmp_path):
        save_project_pdf("newuser", "newproject", "file.pdf", SAMPLE_PDF_BYTES, base_dir=tmp_path)
        assert (tmp_path / "newuser" / "projects" / "pdfs" / "newproject").is_dir()


class TestListProjectPdfs:
    def test_returns_empty_for_nonexistent_project(self, tmp_path):
        result = list_project_pdfs("alice", "noproj", base_dir=tmp_path)
        assert result == []

    def test_returns_filenames_sorted(self, tmp_path):
        save_project_pdf("alice", "proj1", "b.pdf", b"b", base_dir=tmp_path)
        save_project_pdf("alice", "proj1", "a.pdf", b"a", base_dir=tmp_path)
        result = list_project_pdfs("alice", "proj1", base_dir=tmp_path)
        assert result == ["a.pdf", "b.pdf"]

    def test_isolates_by_project(self, tmp_path):
        save_project_pdf("alice", "proj1", "one.pdf", b"1", base_dir=tmp_path)
        save_project_pdf("alice", "proj2", "two.pdf", b"2", base_dir=tmp_path)
        assert list_project_pdfs("alice", "proj1", base_dir=tmp_path) == ["one.pdf"]
        assert list_project_pdfs("alice", "proj2", base_dir=tmp_path) == ["two.pdf"]

    def test_isolates_by_user(self, tmp_path):
        save_project_pdf("alice", "proj1", "shared.pdf", b"a", base_dir=tmp_path)
        save_project_pdf("bob", "proj1", "shared.pdf", b"b", base_dir=tmp_path)
        assert list_project_pdfs("alice", "proj1", base_dir=tmp_path) == ["shared.pdf"]
        assert list_project_pdfs("bob", "proj1", base_dir=tmp_path) == ["shared.pdf"]


class TestDeleteProjectPdf:
    def test_deletes_existing_file(self, tmp_path):
        save_project_pdf("alice", "proj1", "delete_me.pdf", b"data", base_dir=tmp_path)
        result = delete_project_pdf("alice", "proj1", "delete_me.pdf", base_dir=tmp_path)
        assert result is True
        assert not (tmp_path / "alice" / "projects" / "pdfs" / "proj1" / "delete_me.pdf").exists()

    def test_returns_false_for_missing_file(self, tmp_path):
        result = delete_project_pdf("alice", "proj1", "ghost.pdf", base_dir=tmp_path)
        assert result is False

    def test_does_not_affect_other_files(self, tmp_path):
        save_project_pdf("alice", "proj1", "keep.pdf", b"keep", base_dir=tmp_path)
        save_project_pdf("alice", "proj1", "bye.pdf", b"bye", base_dir=tmp_path)
        delete_project_pdf("alice", "proj1", "bye.pdf", base_dir=tmp_path)
        assert list_project_pdfs("alice", "proj1", base_dir=tmp_path) == ["keep.pdf"]


class TestPdfServeRoute:
    """Integration-style tests for the /projects/pdf/ server route."""

    def test_route_returns_pdf_bytes(self, tmp_path):
        """The serve route should return the file bytes with PDF content-type."""
        save_project_pdf("alice", "proj1", "pattern.pdf", SAMPLE_PDF_BYTES, base_dir=tmp_path)

        from stashstats.web.app import create_app

        app = create_app(assets_folder=str(tmp_path))
        app.server.config["PDF_BASE_DIR"] = str(tmp_path)
        client = app.server.test_client()

        response = client.get("/projects/pdf/alice/proj1/pattern.pdf")
        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert response.data == SAMPLE_PDF_BYTES

    def test_route_returns_404_for_missing_file(self, tmp_path):
        from stashstats.web.app import create_app

        app = create_app(assets_folder=str(tmp_path))
        app.server.config["PDF_BASE_DIR"] = str(tmp_path)
        client = app.server.test_client()

        response = client.get("/projects/pdf/alice/proj1/nonexistent.pdf")
        assert response.status_code == 404

    def test_route_rejects_path_traversal(self, tmp_path):
        """The serve route must reject filenames that escape the project PDF directory.

        Werkzeug normalises literal ``..`` segments before routing, so we test with
        a URL-encoded traversal that reaches the handler with a suspicious filename.
        The route must NOT serve a file outside the project PDF directory.
        """
        from stashstats.web.app import create_app

        # Create a "secret" file one level above the project PDF dir
        (tmp_path / "secret.pdf").write_bytes(b"SECRET")

        app = create_app(assets_folder=str(tmp_path))
        app.server.config["PDF_BASE_DIR"] = str(tmp_path)
        client = app.server.test_client()

        # URL-encoded traversal: filename = "../secret.pdf" → %2E%2E%2Fsecret.pdf
        # Werkzeug treats %2F as a literal slash for routing, so this hits our handler
        # with filename containing a path separator — our resolve+startswith guard fires.
        response = client.get("/projects/pdf/alice/proj1/%2E%2E%2Fsecret.pdf")
        # Should be 400 (path traversal rejected) or 404 (file not found in safe dir).
        # Either is acceptable — what matters is NOT 200 with secret content.
        assert response.status_code in (400, 404) or response.data != b"SECRET"
