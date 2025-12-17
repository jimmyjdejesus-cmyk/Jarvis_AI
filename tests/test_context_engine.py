# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



from jarvis_core.config import AppConfig, PersonaConfig
from jarvis_core.context.engine import ContextEngine


def test_context_includes_persona_and_messages(tmp_path):
    doc = tmp_path / "note.txt"
    doc.write_text("Important background knowledge.")
    config = AppConfig(
        personas={
            "generalist": PersonaConfig(
                name="generalist",
                description="",
                system_prompt="Stay factual.",
                max_context_window=512,
            )
        },
        allowed_personas=["generalist"],
    )
    config.context_pipeline.extra_documents_dir = tmp_path
    engine = ContextEngine(config)
    context = engine.build_context(
        persona=config.personas["generalist"],
        messages=[{"role": "user", "content": "Hello"}],
        external_context=["External research"],
    )
    assert "## Persona" in context
    assert "External research" in context
    assert "Important background knowledge" in context
