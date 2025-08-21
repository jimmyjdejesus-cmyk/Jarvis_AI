# Jarvis AI
[![CI](https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/actions/workflows/ci.yml/badge.svg)](https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/actions/workflows/ci.yml)

A privacy-first modular AI development assistant with comprehensive deployment and distribution capabilities.

## 🚀 Quick Start

### Install from PyPI

```bash
pip install jarvis-ai
jarvis run
```

### Docker

```bash
docker compose up -d
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

