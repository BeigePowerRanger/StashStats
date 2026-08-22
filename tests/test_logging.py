import logging
from pathlib import Path
from stashstats.logging import setup_logging

def test_setup_logging_creates_file(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    logger = setup_logging(log_level="DEBUG", log_file=log_file)
    logger.debug("Test debug message")
    logger.info("Test info message")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test debug message" in content
    assert "Test info message" in content
