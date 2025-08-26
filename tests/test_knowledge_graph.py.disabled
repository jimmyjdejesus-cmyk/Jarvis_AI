import pytest

from jarvis.ecosystem.meta_intelligence import MetaIntelligenceCore


@pytest.mark.asyncio
async def test_knowledge_graph_populated():
    core = MetaIntelligenceCore()
    files = core.meta_agent.knowledge_graph.get_files()
    assert files, "Knowledge graph should contain repository files"
