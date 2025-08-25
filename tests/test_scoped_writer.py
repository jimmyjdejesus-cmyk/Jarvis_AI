import zipfile
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.logging.scoped_writer import ScopedLogWriter


def test_log_rotation_and_search(tmp_path: Path) -> None:
    writer = ScopedLogWriter("proj", run_id="run1", base_dir=tmp_path, max_bytes=50, backups=1)
    for i in range(10):
        writer.log_project(f"entry {i}")
    # After multiple writes, rotation should occur
    rotated = writer.project_log.with_suffix(".md.1")
    assert rotated.exists()
    # Search should find a line in rotated logs
    results = writer.search("entry 0")
    assert any("entry 0" in line for line in results)


def test_export_run(tmp_path: Path) -> None:
    writer = ScopedLogWriter("proj", run_id="run2", base_dir=tmp_path)
    writer.log_project("hello")
    archive = writer.export_run()
    assert archive.exists()
    with zipfile.ZipFile(archive) as zf:
        assert "agent_project.md" in zf.namelist()
