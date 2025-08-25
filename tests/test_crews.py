import os
import sys
import asyncio

sys.path.append(os.getcwd())

from jarvis.orchestration.crews import CodeAuditCrew, ResearchCrew
from jarvis.orchestration.orchestrator import DynamicOrchestrator


def test_crew_presets_swappable():
    async def run():
        state = {}
        audit = DynamicOrchestrator(CodeAuditCrew())
        research = DynamicOrchestrator(ResearchCrew())

        res_audit = await audit.run(state.copy())
        res_research = await research.run(state.copy())

        assert res_audit["crew"] == "code_audit"
        assert res_research["crew"] == "research"

    asyncio.run(run())
