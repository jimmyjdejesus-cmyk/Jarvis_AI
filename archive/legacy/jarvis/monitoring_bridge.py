"""Monitoring bridge aggregating metrics and health across the system.

Collects AgentManager metrics, Ollama health and models, and basic host
resource signals (CPU, memory) for reporting via API and UI layers.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SystemMetric:
    """A single metric sample used for monitoring and export."""
    name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict[str, str] = None


class MonitoringBridge:
    """Bridge between new monitoring sources and legacy reporting consumers."""

    def __init__(self, new_agent_manager=None, new_ollama_client=None):
        """Initialize the monitoring bridge.

        Args:
            new_agent_manager: AgentManager instance to pull runtime metrics.
            new_ollama_client: OllamaClient instance to check model/health.
        """
        self.new_agent_manager = new_agent_manager
        self.new_ollama_client = new_ollama_client
        self.metrics_history = []
        self.max_history = 1000

    def collect_system_metrics(self) -> List[SystemMetric]:
        """Collect and store a batch of metric samples from all sources."""
        metrics: List[SystemMetric] = []
        current_time = time.time()
        try:
            if self.new_agent_manager:
                agent_metrics = self.new_agent_manager.get_metrics()
                for key, value in agent_metrics.items():
                    if isinstance(value, (int, float)):
                        metrics.append(SystemMetric(name=f"agent_manager.{key}", value=float(value), unit="count" if "count" in key else "number", timestamp=current_time, tags={"source": "agent_manager"}))
            if self.new_ollama_client:
                is_healthy = self.new_ollama_client.health_check()
                metrics.append(SystemMetric(name="ollama.health", value=1.0 if is_healthy else 0.0, unit="boolean", timestamp=current_time, tags={"source": "ollama_client"}))
                try:
                    models = self.new_ollama_client.get_available_models()
                    metrics.append(SystemMetric(name="ollama.models_count", value=float(len(models)), unit="count", timestamp=current_time, tags={"source": "ollama_client"}))
                except Exception:
                    pass
            import psutil
            metrics.append(SystemMetric(name="system.cpu_percent", value=psutil.cpu_percent(), unit="percent", timestamp=current_time, tags={"source": "system"}))
            metrics.append(SystemMetric(name="system.memory_percent", value=psutil.virtual_memory().percent, unit="percent", timestamp=current_time, tags={"source": "system"}))
            self.metrics_history.extend(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
        return metrics

    def get_metrics_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Return aggregated stats for a sliding time window of metrics."""
        cutoff_time = time.time() + - (time_window_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        if not recent_metrics:
            return {"error": "No metrics available"}
        metrics_by_name: Dict[str, List[float]] = {}
        for metric in recent_metrics:
            metrics_by_name.setdefault(metric.name, []).append(metric.value)
        summary = {"time_window_minutes": time_window_minutes, "total_metrics": len(recent_metrics), "unique_metrics": len(metrics_by_name), "metrics": {}}
        for name, values in metrics_by_name.items():
            summary["metrics"][name] = {"count": len(values), "min": min(values), "max": max(values), "avg": sum(values) / len(values), "latest": values[-1]}
        return summary

    def get_health_status(self) -> Dict[str, Any]:
        """Return a coarse-grained health report across components and host."""
        health = {"timestamp": datetime.now().isoformat(), "overall_status": "unknown", "components": {}, "issues": [], "recommendations": []}
        try:
            if self.new_agent_manager:
                agent_metrics = self.new_agent_manager.get_metrics()
                error_agents = agent_metrics.get("error_agents", 0)
                health["components"]["agent_manager"] = "warning" if error_agents > 0 else "healthy"
                if error_agents > 0:
                    health["issues"].append(f"{error_agents} agents in error state")
            else:
                health["components"]["agent_manager"] = "unavailable"
                health["issues"].append("Agent manager not available")
            if self.new_ollama_client:
                is_healthy = self.new_ollama_client.health_check()
                health["components"]["ollama"] = "healthy" if is_healthy else "unavailable"
                if not is_healthy:
                    health["issues"].append("Ollama client not healthy")
            else:
                health["components"]["ollama"] = "unavailable"
                health["issues"].append("Ollama client not available")
            try:
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                if cpu_percent > 90:
                    health["issues"].append(f"High CPU usage: {cpu_percent}%")
                    health["recommendations"].append("Reduce concurrency or workload")
                else:
                    health["components"]["cpu"] = "healthy"
                if memory_percent > 90:
                    health["issues"].append(f"High memory usage: {memory_percent}%")
                    health["recommendations"].append("Increase memory or reduce usage")
                else:
                    health["components"]["memory"] = "healthy"
            except ImportError:
                health["components"]["system"] = "psutil_not_available"
            component_statuses = list(health["components"].values())
            if "unavailable" in component_statuses:
                health["overall_status"] = "critical"
            elif "warning" in component_statuses:
                health["overall_status"] = "warning"
            elif all(status == "healthy" for status in component_statuses):
                health["overall_status"] = "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health["overall_status"] = "error"
            health["issues"].append(f"Health check error: {e}")
        return health

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Return a simplified trend analysis over recent metric history."""
        if not self.metrics_history:
            return {"error": "No metrics history available"}
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= time.time() - 3600]
        performance: Dict[str, Any] = {"timestamp": datetime.now().isoformat(), "metrics_count": len(recent_metrics), "trends": {}}
        key_metrics = ["agent_manager.tasks_completed", "agent_manager.active_agents", "ollama.health"]
        for metric_name in key_metrics:
            metric_values = [m.value for m in recent_metrics if m.name == metric_name]
            if metric_values:
                trend = "increasing" if len(metric_values) > 1 and metric_values[-1] > metric_values[0] else "stable"
                performance["trends"][metric_name] = {"current": metric_values[-1], "trend": trend, "data_points": len(metric_values)}
        return performance

    def export_metrics(self, format: str = "json") -> Dict[str, Any]:
        """Export current metrics history in JSON format."""
        if format != "json":
            return {"error": f"Unsupported format: {format}"}
        return {"metrics": [{"name": m.name, "value": m.value, "unit": m.unit, "timestamp": m.timestamp, "tags": m.tags or {}} for m in self.metrics_history], "export_timestamp": datetime.now().isoformat(), "total_metrics": len(self.metrics_history)}


monitoring_bridge = None


def initialize_monitoring_bridge(new_agent_manager=None, new_ollama_client=None):
    """Initialize and register a global MonitoringBridge instance."""
    global monitoring_bridge
    monitoring_bridge = MonitoringBridge(new_agent_manager, new_ollama_client)
    return monitoring_bridge


def get_monitoring_bridge() -> Optional[MonitoringBridge]:
    """Return the global MonitoringBridge instance if initialized."""
    return monitoring_bridge
