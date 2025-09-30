"""Security bridge to apply runtime validations and audits across agent actions.

This module centralizes lightweight security checks (status, suspicious actions,
sensitive data hints) and provides audit and statistics utilities for higher
layers (API, monitoring, UI).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityBridge:
    """Bridge between new security checks and legacy security contexts."""

    def __init__(self, new_agent_manager=None):
        """Initialize the security bridge.

        Args:
            new_agent_manager: AgentManager instance to introspect agent status.
        """
        self.new_agent_manager = new_agent_manager
        self.security_events = []

    def validate_agent_action(self, agent_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an agent action using basic runtime checks.

        Args:
            agent_id: The target agent identifier.
            action: A human-readable action verb (e.g. "read", "delete").
            context: Additional action context for inspection.

        Returns:
            A validation result dict including validity, reasons, and checks.
        """
        try:
            if not self.new_agent_manager:
                return {"valid": True, "reason": "No new security system available"}

            agent = self.new_agent_manager.get_agent(agent_id)
            if not agent:
                return {"valid": False, "reason": "Agent not found"}

            security_result = {
                "valid": True,
                "agent_id": agent_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "checks": [],
            }

            status = self.new_agent_manager.get_agent_status(agent_id)
            if status and status.value == "error":
                security_result["valid"] = False
                security_result["reason"] = "Agent in error state"
                security_result["checks"].append("agent_status_check")

            suspicious_actions = ["delete", "remove", "destroy", "overwrite"]
            if any(suspicious in action.lower() for suspicious in suspicious_actions):
                security_result["checks"].append("suspicious_action_check")

            sensitive_keys = ["password", "secret", "key", "token", "credential"]
            if any(key in str(context).lower() for key in sensitive_keys):
                security_result["checks"].append("sensitive_data_check")

            self.security_events.append(security_result)
            return security_result

        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {"valid": False, "reason": f"Security validation error: {e}", "agent_id": agent_id, "action": action}

    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return recent security event records."""
        return self.security_events[-limit:]

    def get_security_stats(self) -> Dict[str, Any]:
        """Return aggregate security counters and rates."""
        total_events = len(self.security_events)
        valid_actions = sum(1 for event in self.security_events if event.get("valid", False))
        invalid_actions = total_events - valid_actions
        return {
            "total_events": total_events,
            "valid_actions": valid_actions,
            "invalid_actions": invalid_actions,
            "security_rate": valid_actions / total_events if total_events > 0 else 1.0,
            "bridge_available": self.new_agent_manager is not None,
        }

    def run_security_audit(self) -> Dict[str, Any]:
        """Run a summary audit across agent health and recent events.

        Returns:
            Audit report containing checks, issues, recommendations, and a score.
        """
        audit_result = {"timestamp": datetime.now().isoformat(), "checks": [], "issues": [], "recommendations": []}
        try:
            if not self.new_agent_manager:
                audit_result["issues"].append("New security system not available")
                audit_result["recommendations"].append("Initialize new agent manager")
            else:
                audit_result["checks"].append("agent_manager_available")

            if self.new_agent_manager:
                agents = list(self.new_agent_manager.agents.keys())
                error_agents = []
                for agent_id in agents:
                    status = self.new_agent_manager.get_agent_status(agent_id)
                    if status and status.value == "error":
                        error_agents.append(agent_id)
                if error_agents:
                    audit_result["issues"].append(f"Agents in error state: {error_agents}")
                    audit_result["recommendations"].append("Investigate and fix error agents")
                else:
                    audit_result["checks"].append("all_agents_healthy")

            recent = self.get_security_events(50)
            invalid = [e for e in recent if not e.get("valid", True)]
            if invalid:
                audit_result["issues"].append(f"Recent invalid actions: {len(invalid)}")
                audit_result["recommendations"].append("Review and investigate invalid actions")
            else:
                audit_result["checks"].append("no_recent_invalid_actions")

            total_checks = len(audit_result["checks"])
            total_issues = len(audit_result["issues"])
            score = (total_checks - total_issues) / max(total_checks, 1)
            audit_result["security_score"] = score
            audit_result["status"] = "good" if score > 0.8 else "warning" if score > 0.5 else "critical"

        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            audit_result["issues"].append(f"Audit error: {e}")
            audit_result["status"] = "error"
        return audit_result


security_bridge = None


def initialize_security_bridge(new_agent_manager=None):
    """Initialize and register a global SecurityBridge instance."""
    global security_bridge
    security_bridge = SecurityBridge(new_agent_manager)
    return security_bridge


def get_security_bridge() -> Optional[SecurityBridge]:
    """Return the global SecurityBridge instance if initialized."""
    return security_bridge
