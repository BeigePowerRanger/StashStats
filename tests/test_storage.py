import json
from pathlib import Path
import pytest

from stashstats.storage import (
    get_user_data_dir,
    get_user_storage_path,
    save_user_json,
    load_user_json,
    delete_user_file,
    list_user_files,
    get_user_db_path,
)


class TestMultiUserStorage:
    def test_get_user_data_dir(self, tmp_path):
        user_dir = get_user_data_dir("user123", base_dir=tmp_path)
        assert user_dir == tmp_path / "user123"
        assert user_dir.exists()
        assert user_dir.is_dir()

    def test_get_user_storage_path(self, tmp_path):
        filepath = get_user_storage_path("user123", "stash.json", base_dir=tmp_path)
        assert filepath == tmp_path / "user123" / "stash.json"
        assert filepath.parent.exists()

    def test_save_and_load_user_json(self, tmp_path):
        data = {"user": "alice", "items": [{"id": 1, "name": "Yarn A"}]}
        saved_path = save_user_json("alice", "stash.json", data, base_dir=tmp_path)
        assert saved_path == tmp_path / "alice" / "stash.json"
        assert saved_path.exists()

        loaded_data = load_user_json("alice", "stash.json", base_dir=tmp_path)
        assert loaded_data == data

    def test_load_user_json_missing_default(self, tmp_path):
        loaded_data = load_user_json("nonexistent", "missing.json", default={"empty": True}, base_dir=tmp_path)
        assert loaded_data == {"empty": True}

    def test_user_data_isolation(self, tmp_path):
        alice_data = {"user": "alice", "count": 10}
        bob_data = {"user": "bob", "count": 20}

        save_user_json("alice", "profile.json", alice_data, base_dir=tmp_path)
        save_user_json("bob", "profile.json", bob_data, base_dir=tmp_path)

        assert load_user_json("alice", "profile.json", base_dir=tmp_path) == alice_data
        assert load_user_json("bob", "profile.json", base_dir=tmp_path) == bob_data
        assert (tmp_path / "alice" / "profile.json").exists()
        assert (tmp_path / "bob" / "profile.json").exists()

    def test_delete_user_file(self, tmp_path):
        save_user_json("alice", "temp.json", {"temp": True}, base_dir=tmp_path)
        assert (tmp_path / "alice" / "temp.json").exists()

        deleted = delete_user_file("alice", "temp.json", base_dir=tmp_path)
        assert deleted is True
        assert not (tmp_path / "alice" / "temp.json").exists()

        deleted_again = delete_user_file("alice", "temp.json", base_dir=tmp_path)
        assert deleted_again is False

    def test_list_user_files(self, tmp_path):
        save_user_json("alice", "file1.json", {"f": 1}, base_dir=tmp_path)
        save_user_json("alice", "file2.json", {"f": 2}, base_dir=tmp_path)

        files = list_user_files("alice", base_dir=tmp_path)
        assert sorted(files) == ["file1.json", "file2.json"]

    def test_get_user_db_path(self, tmp_path):
        db_path = get_user_db_path("alice", db_name="reference.db", base_dir=tmp_path)
        assert db_path == tmp_path / "alice" / "reference.db"
        assert db_path.parent.exists()
