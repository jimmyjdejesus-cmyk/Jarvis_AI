"""Pruning manager with safety and reliability features.

Provides two-phase pruning (dry-run and commit), snapshot/rollback,
HITL prompts, and policy guardrails. It also includes the PruningEvaluator
service for scoring and emitting prune recommendations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional

from memory_service import PathRecord, PathSignature, record_path
from .message_bus import MessageBus # Assuming MessageBus is in a .message_bus module


@dataclass
class PruneRecord:
    """Audit record for prune/merge actions."""

    team: str
    actor: str
    reason: str
    timestamp: str


@dataclass
class Scores:
    """Container for pruning score signals."""

    novelty: float
    growth: float
    cost: float


class PruningEvaluator:
    """Score teams and emit prune suggestions.

    This is a lightweight in-process service that scores exploration teams
    and emits pruning recommendations via the MessageBus.
    """

    def __init__(
        self,
        bus: MessageBus,
        scope: str = "global",
        config: Optional[Dict[str, float]] = None,
    ) -> None:
        self.bus = bus
        self.scope = scope
        self.config = {
            "min_novelty": 0.25,
            "min_growth": 0.0,
            "max_cost_per_gain": 3.0,
        }
        if config:
            self.config.update(config)

        # Store simple per-team history for delta calculations
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        # Track teams that have been suggested for pruning so orchestrators can
        # skip them on subsequent runs. This provides a lightweight form of
        # dead-end detection without requiring a separate pruning service.
        self._suggested: set[str] = set()

    async def score(self, team_id: str, output: Dict[str, Any]) -> Scores:
        """Calculate pruning scores for a team's latest output."""
        history = self._history.setdefault(team_id, [])

        # Novelty: simple token overlap with last output
        novelty = 1.0
        if history:
            prev_text = history[-1].get("text", "")
            cur_text = output.get("text", "")
            prev_tokens = set(prev_text.split())
            cur_tokens = set(cur_text.split())
            union = prev_tokens | cur_tokens
            if union:
                novelty = 1 - (len(prev_tokens & cur_tokens) / len(union))

        # Growth: difference in quality metric
        prev_quality = history[-1].get("quality", 0.0) if history else 0.0
        quality = output.get("quality", 0.0)
        growth = quality - prev_quality

        # Cost per gain: avoid division by zero
        cost = output.get("cost", 0.0)
        cost_per_gain = cost / growth if growth > 0 else float("inf")

        history.append(output)
        return Scores(novelty=novelty, growth=growth, cost=cost_per_gain)

    async def evaluate(self, team_id: str, output: Dict[str, Any]) -> Scores:
        """Score output and record if pruning is suggested."""
        scores = await self.score(team_id, output)
        cfg = self.config
        if (
            scores.novelty < cfg["min_novelty"]
            or scores.growth < cfg["min_growth"]
            or scores.cost > cfg["max_cost_per_gain"]
        ):
            # Mark team for pruning and emit an event for observers.
            self._suggested.add(team_id)
            await self.bus.publish(
                "orchestrator.prune_suggested",
                {
                    "team_id": team_id,
                    "scores": scores.__dict__,
                    "reason": "thresholds_not_met",
                },
                scope=self.scope,
            )
        return scores

    def should_prune(self, team_id: str) -> bool:
        """Return ``True`` if ``team_id`` has been suggested for pruning."""
        return team_id in self._suggested

    def clear_suggestion(self, team_id: str) -> None:
        """Remove ``team_id`` from the suggested set after actioning."""
        self._suggested.discard(team_id)

    async def merge_state(
        self,
        from_team: str,
        into_team: str,
        artifacts: List[str],
        signature: PathSignature | None = None,
    ) -> None:
        """Emit merge event and optionally record negative path."""
        await self.bus.publish(
            "orchestrator.team_merged",
            {
                "from_team": from_team,
                "into_team": into_team,
                "merged_artifacts": artifacts,
            },
            scope=self.scope,
        )
        if signature is not None:
            record_path(
                PathRecord(
                    actor="orchestrator",
                    target="project",
                    kind="negative",
                    signature=signature,
                )
            )

    async def mark_dead_end(self, team_id: str, signature: PathSignature) -> None:
        """Publish dead-end marker and record negative path."""
        await self.bus.publish(
            "orchestrator.path_dead_end",
            {"team_id": team_id, "path_signature": signature.hash or ""},
            scope=self.scope,
        )
        record_path(
            PathRecord(
                actor="orchestrator",
                target="project",
                kind="negative",
                signature=signature,
            )
        )


@dataclass
class PruningManager:
    """Manage safe, reversible team pruning operations."""

    state_store: Dict[str, Any]
    snapshots_dir: str = "snapshots"
    active_teams: List[str] = field(default_factory=list)
    lineage: List[PruneRecord] = field(default_factory=list)
    bq_approved: bool = False
    
    # PruningEvaluator instance for scoring
    evaluator: Optional[PruningEvaluator] = None

    def __post_init__(self) -> None:
        os.makedirs(self.snapshots_dir, exist_ok=True)
        if not self.active_teams:
            self.active_teams = list(self.state_store.keys())

    # ----------------- Guardrails -----------------
    def _check_guardrails(self, team: str, context: Optional[Dict[str, Any]] = None) -> None:
        context = context or {}
        if team == "Security" and context.get("round") == "adversarial":
            raise ValueError("Cannot prune Security team during adversarial rounds.")
        if len(self.active_teams) <= 2 and not self.bq_approved:
            raise ValueError("At least two teams must remain active until BQ approval.")

    # ----------------- Two Phase Prune -----------------
    def dry_run(self, team: str, reason: str, actor: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate prune without changing state."""
        self._check_guardrails(team, context)
        return {
            "team": team,
            "reason": reason,
            "actor": actor,
            "snapshot_required": True,
        }

    def commit(self, team: str, reason: str, actor: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute prune after a successful dry run."""
        plan = self.dry_run(team, reason, actor, context)
        snapshot = self.snapshot_before_prune(team)
        state = self.state_store.pop(team, None)
        if team in self.active_teams:
            self.active_teams.remove(team)
        record = PruneRecord(team, actor, reason, datetime.utcnow().isoformat())
        self.lineage.append(record)
        return {"plan": plan, "snapshot": snapshot, "state": state}

    # ----------------- Snapshot / Rollback -----------------
    def _snapshot_path(self, team: str) -> str:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return os.path.join(self.snapshots_dir, f"{team}_{ts}.json")

    def snapshot_before_prune(self, team: str) -> str:
        path = self._snapshot_path(team)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.state_store.get(team), fh)
        return path

    def rollback(self, snapshot_path: str, team: str) -> Dict[str, Any]:
        with open(snapshot_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.state_store[team] = data
        if team not in self.active_teams:
            self.active_teams.append(team)
        return data

    # ----------------- HITL -----------------
    def generate_hitl_prompt(self, team: str, reason: str, score: Optional[float] = None, override_minutes: int = 10) -> str:
        detail = f"Prune Team {team}? Reason: {reason}"
        if score is not None:
            detail += f" ({score})"
        return f"{detail}. Override {override_minutes}m / Merge / Cancel"

    # ----------------- Lineage -----------------
    def audit_log(self) -> List[Dict[str, Any]]:
        return [record.__dict__ for record in self.lineage]