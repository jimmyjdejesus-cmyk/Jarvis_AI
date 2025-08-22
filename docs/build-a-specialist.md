# Build a Specialist

Create a new specialist by subclassing `BaseSpecialist` and registering it with the orchestrator.

```python
from jarvis_ai.specialists import BaseSpecialist

class MySpecialist(BaseSpecialist):
    def handle(self, task: str) -> str:
        return f"Handled {task}!"
```

Add your specialist to the registry:
```bash
jarvis register MySpecialist
```
