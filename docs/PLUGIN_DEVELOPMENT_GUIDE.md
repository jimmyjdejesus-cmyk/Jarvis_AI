# Jarvis SDK Plugin Development Tutorial

The `jarvis_sdk` package (version 0.1.1) makes it easy to build and share
plugins for the Jarvis AI system. This tutorial covers creating plugins,
auto-registration, and the included examples for tools and agents.

## Installing

Install the repository in editable mode so the SDK and sample plugins are
available:

```bash
pip install -e .
```

## Scaffolding a Plugin

Use the SDK's scaffolding utility to generate a plugin module:

```python
from jarvis_sdk import create_plugin

create_plugin(
    "jarvis/plugins", "my_plugin", plugin_type="tool", description="Demo plugin"
)
```

The command above creates `jarvis/plugins/my_plugin.py` populated with a
registered stub ready for implementation.

## Plugin Types

The SDK exposes specialised decorators for the most common plugin categories:

- `jarvis_sdk.jarvis_tool` – register a simple callable as a tool
- `jarvis_sdk.jarvis_agent` – register a class implementing an agent

For advanced scenarios, `jarvis_sdk.jarvis_plugin` allows registration under a
custom `plugin_type` value.

### Tool Example

```python
from jarvis_sdk import jarvis_tool

@jarvis_tool(description="Say hello")
def greet(name: str = "world") -> str:
    return f"Hello {name}!"
```

### Agent Example

```python
from jarvis_sdk import jarvis_agent

@jarvis_agent(description="Evaluate math")
class MathAgent:
    def run(self, expression: str) -> str:
        return str(eval(expression))
```

## Discovery and Auto‑registration

Plugin modules are listed in `jarvis/plugins/manifest.json` and imported when
`jarvis.plugins` is loaded. Importing the package automatically registers all
listed plugins with the global registry, as well as the dedicated agent and tool
registries.

To load the bundled examples and view what is registered:

```python
import jarvis.plugins  # triggers discovery
from jarvis_sdk import agent_registry, tool_registry

print(agent_registry.all())
print(tool_registry.all())
```

## Next Steps

Extend the examples or scaffold new plugins to integrate custom functionality
into Jarvis.
