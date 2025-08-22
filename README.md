# Jarvis AI
[![CI](https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/actions/workflows/ci.yml/badge.svg)](https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/actions/workflows/ci.yml)

A privacy-first modular AI development assistant with comprehensive deployment and distribution capabilities.

> **Deprecated:** The legacy Streamlit application in `legacy/` has reached feature parity with V2 and is no longer maintained.
> See `docs/migration_checklist.md` for mapping of legacy components.

## 🚀 Quick Start

### Install from PyPI

```bash
pip install "jarvis-ai[ui]"
jarvis run
```

### Docker

```bash
docker compose up -d
```

The included `docker-compose.yml` launches four services:

- `app-api` – main Jarvis API
- `memory-service` – Redis instance for conversation memory
- `vector-db` – Qdrant vector database
- `ollama` – local model runtime

Each service exposes a basic health check so `docker compose` can wait
for dependencies before starting `app-api`.

### One-Click Installer

```bash
curl -sSL https://raw.githubusercontent.com/jimmyjdejesus-cmyk/Jarvis_AI/main/scripts/installers/install-unix.sh | bash
```

### Configuration

```bash
jarvis config --init
jarvis config --validate
jarvis config --show
```

desktop build and configuration wizard:
Configuration profiles live under `config/profiles`. Select a profile by
setting the `CONFIG_PROFILE` environment variable (defaults to
`development`). Any setting can be overridden by environment variables
using double underscores for nesting. For example:

```bash
export JARVIS__ORCH__MIN_NOVELTY=0.25
```

### Desktop App Packaging

Use [PyInstaller](https://pyinstaller.org/) to create a standalone
desktop build and configuration wizard:

```bash
pip install pyinstaller
pyinstaller desktop_app.py --onefile --distpath dist
pyinstaller setup_api_keys.py --onefile --distpath dist/config_wizard
```

Packaged binaries will be placed in the `dist/` directory.

### Troubleshooting

- **Docker services fail health checks** – ensure required ports are
  free and rerun `docker compose up`.
- **Missing configuration** – run the config wizard in `dist/config_wizard`
  or create a `.env` file with required keys.
- **PyInstaller build is large** – use the `--exclude-module` flag to
  omit optional dependencies when packaging.

## 📈 Graphviz

Some features use the [`graphviz`](https://pypi.org/project/graphviz/) package to render diagrams.
Install the Graphviz system binaries to enable visualization:

```bash
# Debian/Ubuntu
sudo apt-get install graphviz

# macOS
brew install graphviz
```

If Graphviz is not installed, these features will be skipped or fall back to text-based output.

## 🗂️ Logging

Jarvis uses [structlog](https://www.structlog.org/) for structured logging.

```python
from jarvis.logging import configure, get_logger

configure()  # writes to logs/jarvis.log
logger = get_logger()
logger.info("startup complete")
```

Pass a ``remote_url`` to ``configure`` to forward log events to an HTTP service.

### Viewing Logs

A Grafana Loki stack is provided for local development:

```bash
docker compose -f docker-compose.logging.yml up -d
```

Then open [http://localhost:3000](http://localhost:3000) and add Loki at `http://loki:3100` as a data source to explore logs.

## 📋 Features

- Modular agent framework
- Lang ecosystem integration (LangChain, LangGraph, LangSmith)
- YAML configuration with environment overrides
- Docker support and one-click installers

## 🔧 Development

```bash
git clone https://github.com/jimmyjdejesus-cmyk/Jarvis_AI.git
cd Jarvis_AI
pip install -e .[dev]
pytest
```

## 📄 License

MIT

