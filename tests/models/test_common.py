import pytest
from pydantic import ValidationError

from stashstats.models.common import Paginator, Photo


class TestPhoto:
    def test_valid_urls(self):
        photo = Photo(
            id=123,
            square_url="https://images4-b.ravelrycache.com/uploads/test/sq.jpg",
            small_url="http://images4.ravelry.com/sm.jpg",
            medium_url="https://example.com/med.jpg",
            thumbnail_url="https://example.com/thumb.jpg",
        )
        assert photo.square_url == "https://images4-b.ravelrycache.com/uploads/test/sq.jpg"
        assert photo.small_url == "http://images4.ravelry.com/sm.jpg"
        assert photo.medium_url == "https://example.com/med.jpg"
        assert photo.thumbnail_url == "https://example.com/thumb.jpg"
        assert photo.medium2_url is None
        assert photo.small2_url is None

    def test_empty_and_none_urls(self):
        photo = Photo(
            id=456,
            square_url="",
            small_url="   ",
            medium_url=None,
        )
        assert photo.square_url is None
        assert photo.small_url is None
        assert photo.medium_url is None

    def test_invalid_url(self):
        with pytest.raises(ValidationError):
            Photo(id=789, square_url="not-a-valid-url")

        with pytest.raises(ValidationError):
            Photo(id=789, medium_url="ftp://invalid-scheme.com/img.jpg")
