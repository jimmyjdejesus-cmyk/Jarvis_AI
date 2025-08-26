from __future__ import annotations

"""Generate documentation for registered tools without importing heavy packages."""

import json
import importlib.util
import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Prepare package structure for jarvis.tools
jarvis_pkg = types.ModuleType("jarvis")
jarvis_pkg.__path__ = [str(PROJECT_ROOT / "jarvis")]
sys.modules.setdefault("jarvis", jarvis_pkg)
tools_pkg = types.ModuleType("jarvis.tools")
tools_pkg.__path__ = [str(PROJECT_ROOT / "jarvis/tools")]
sys.modules.setdefault("jarvis.tools", tools_pkg)


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def main(output: str = "docs/tool_docs.json") -> None:
    registry_mod = _load_module(
        "jarvis.tools.registry", PROJECT_ROOT / "jarvis/tools/registry.py"
    )
    registry = registry_mod.registry

    # Load tool modules so they register themselves
    tools_dir = PROJECT_ROOT / "jarvis/tools"
    for file in tools_dir.glob("*.py"):
        if file.name in {"__init__.py", "registry.py"}:
            continue
        _load_module(f"jarvis.tools.{file.stem}", file)

    data = registry.json_export()
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
