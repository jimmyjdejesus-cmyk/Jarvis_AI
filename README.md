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
docker compose --profile dev up -d
```

The included `docker-compose.yml` launches five services:

- `api` – main Jarvis API
- `orchestrator` – coordination service with crash recovery
- `memory-service` – Redis instance for conversation memory
- `vector-db` – Qdrant vector database
- `ollama` – local model runtime (dev/local-prod profiles)

Each service exposes a basic health check so `docker compose` can wait
for dependencies before starting `api`.

Services are grouped using Docker Compose profiles. Use `dev`, `local-prod`,
or `hybrid` (cloud LLMs) depending on your environment:

```bash
docker compose --profile hybrid up -d
```

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

### Remote Model Setup

The MCP client can route requests to remote services such as OpenAI and
Anthropic. Provide API credentials via environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

Keys may be stored in a local `.env` file or managed through the
`setup_api_keys.py` helper. When no keys are present the system falls back
to local models.

### Deep Research Mode

The command-line interface exposes a **deep research** mode that leverages
the multi-agent orchestrator. Enable it with the `--deep` flag on the
`research` command:

```bash
python jarvis_cli.py research "scaling microservices" --deep
```

In this mode the orchestrator spawns specialist agents and synthesizes
their findings into a comprehensive answer.

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


## 🧭 Workflow Visualizer and Dead-End Shelf

Jarvis now exposes its internal reasoning through a Streamlit DAG panel and a
dead-end shelf for pruned branches. The DAG view supports DOT/JSON/PNG export
while the shelf allows operators to override pruned paths when necessary.

![Workflow DAG](docs/images/dag_panel.png)
![Dead-End Shelf](docs/images/dead_end_shelf.png)

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

