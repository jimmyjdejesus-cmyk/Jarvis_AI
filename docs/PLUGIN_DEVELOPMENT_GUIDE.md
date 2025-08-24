# Jarvis SDK Plugin Development Tutorial

The `jarvis_sdk` package (version 0.1.0) makes it easy to build and share
plugins for the Jarvis AI system.  This tutorial covers creating plugins,
auto-registration, and the included examples for tools, specialists, and critics.

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

create_plugin("jarvis/plugins", "my_plugin", plugin_type="tool", description="Demo plugin")
```

The command above creates `jarvis/plugins/my_plugin.py` populated with a
registered stub ready for implementation.

## Plugin Types

`jarvis_sdk.jarvis_plugin` registers callables or classes under a plugin type.
The SDK ships with three common categories:

- **tool** – a simple callable used as a tool
- **specialist** – a class offering a specialised capability
- **critic** – a callable that reviews or validates data

### Tool Example

```python
from jarvis_sdk import jarvis_plugin

@jarvis_plugin(plugin_type="tool", description="Say hello")
def greet(name: str = "world") -> str:
    return f"Hello {name}!"
```

### Specialist Example

```python
from jarvis_sdk import jarvis_plugin

@jarvis_plugin(plugin_type="specialist", description="Evaluate math")
class MathSpecialist:
    def run(self, expression: str) -> str:
        return str(eval(expression))
```

### Critic Example

```python
from jarvis_sdk import jarvis_plugin

@jarvis_plugin(plugin_type="critic", description="Check text length")
def length_checker(text: str, max_length: int = 100) -> str:
    if len(text) > max_length:
        return f"Text too long by {len(text) - max_length} characters."
    return "Text length OK."
```

## Discovery and Auto‑registration

Plugin modules are listed in `jarvis/plugins/manifest.json` and imported when
`jarvis.plugins` is loaded. Importing the package automatically registers all
listed plugins with the SDK registry.

To load the bundled examples and view what is registered:

```python
import jarvis.plugins  # triggers discovery
from jarvis_sdk import registry

print(registry.all())
```

## Next Steps

Extend the examples or scaffold new plugins to integrate custom functionality
into Jarvis.
