import json, os, time, uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

class SessionManager:
    """Handles per-session chat storage on disk.

    Each session is a directory in data/sessions/<session_id> with:
      - session.json (metadata)
      - log.jsonl (one JSON per line with inputs/outputs/steps)
    """
    def __init__(self, base_dir: str = "data/sessions") -> None:
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def create(self, name: Optional[str] = None) -> str:
        sid = str(uuid.uuid4())[:8]
        sess_dir = self.base / sid
        sess_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "id": sid,
            "name": name or f"session-{sid}",
            "created_at": int(time.time()),
            "runs": 0,
        }
        (sess_dir / "session.json").write_text(json.dumps(meta, indent=2))
        (sess_dir / "log.jsonl").write_text("")  # touch
        return sid

    def list_sessions(self) -> List[Dict[str, Any]]:
        out = []
        for d in sorted(self.base.glob("*/session.json")):
            try:
                meta = json.loads(d.read_text())
                meta["path"] = str(d.parent)
                out.append(meta)
            except Exception:
                continue
        return out

    def load_meta(self, session_id: str) -> Dict[str, Any]:
        p = self.base / session_id / "session.json"
        return json.loads(p.read_text())

    def append_run(self, session_id: str, record: Dict[str, Any]) -> None:
        sess = self.base / session_id
        log = sess / "log.jsonl"
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        # bump runs
        meta_p = sess / "session.json"
        meta = json.loads(meta_p.read_text())
        meta["runs"] = meta.get("runs", 0) + 1
        meta_p.write_text(json.dumps(meta, indent=2))

    def read_runs(self, session_id: str) -> List[Dict[str, Any]]:
        sess = self.base / session_id
        log = sess / "log.jsonl"
        if not log.exists():
            return []
        lines = log.read_text(encoding="utf-8").splitlines()
        return [json.loads(x) for x in lines if x.strip()]
