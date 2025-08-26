"""Simple CLI to issue runtime commands to an orchestrator instance.

This utility demonstrates operator intervention by allowing pause, restart,
and merge commands to be sent to a running :class:`OrchestratorAgent`.

The CLI spawns a demo orchestrator when executed directly. In a real system it
would connect to an already running orchestrator via IPC or network RPC.
"""

from __future__ import annotations

import argparse

from .agents import MetaAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrator runtime controls")
    sub = parser.add_subparsers(dest="command", required=True)

    pause_p = sub.add_parser("pause", help="Pause a team")
    pause_p.add_argument("team")

    restart_p = sub.add_parser("restart", help="Restart a team")
    restart_p.add_argument("team")

    merge_p = sub.add_parser("merge", help="Merge one team into another")
    merge_p.add_argument("source")
    merge_p.add_argument("target")

    args = parser.parse_args()

    # For demonstration we spin up a temporary orchestrator
    meta = MetaAgent()
    orch = meta.spawn_orchestrator("demo objective")

    if args.command == "pause":
        orch.pause_team(args.team)
    elif args.command == "restart":
        orch.restart_team(args.team)
    else:
        orch.merge_teams(args.source, args.target)

    # Print lineage to show effect
    print("Lineage:", orch.get_lineage())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

