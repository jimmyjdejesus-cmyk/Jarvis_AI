import json
import importlib.util
from pathlib import Path

logger_path = (
    Path(__file__).resolve().parent.parent / "jarvis" / "logging" / "logger.py"
)
spec = importlib.util.spec_from_file_location(
    "jarvis.logging.logger",
    logger_path,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
configure = module.configure
get_logger = module.get_logger

from jarvis.logging.logger import configure, get_logger
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
    configure(log_file=str(log_file), remote_url="http://localhost:1")
    logger = get_logger("test")
    logger.info("remote test")
    assert log_file.exists()
