import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jarvis.logging.logger import configure, get_logger  # noqa: E402


def test_configure_creates_json_log(tmp_path):
    log_file = tmp_path / "jarvis.log"
    configure(log_file=str(log_file))
    logger = get_logger("test")
    logger.info("hello", foo="bar")
    contents = log_file.read_text().strip().splitlines()
    assert contents, "log file should contain at least one line"
    data = json.loads(contents[0])
    assert data["event"] == "hello"
    assert data["foo"] == "bar"


def test_remote_sink_is_optional(tmp_path):
    log_file = tmp_path / "jarvis.log"
    configure(log_file=str(log_file), remote_url="https://localhost:1")
    logger = get_logger("test")
    logger.info("remote test")
    assert log_file.exists()


def test_reject_insecure_remote_url(tmp_path):
    """``remote_url`` must use HTTPS for security."""
    log_file = tmp_path / "jarvis.log"
    with pytest.raises(ValueError):
        configure(log_file=str(log_file), remote_url="http://insecure")
