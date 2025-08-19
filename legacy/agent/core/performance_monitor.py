"""
Performance Monitoring and Metrics Collection for Jarvis AI
Provides comprehensive performance monitoring, metrics collection, and optimization insights.
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import os
from agent.core.error_handling import get_logger
from agent.core.config_manager import get_config


@dataclass
class PerformanceMetric:
    """Single performance metric data point."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


@dataclass
class OperationStats:
    """Statistics for a specific operation."""
    operation_name: str
    total_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    error_count: int = 0
    success_count: int = 0
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def avg_duration(self) -> float:
        return self.total_duration / max(self.total_calls, 1)
    
    @property
    def success_rate(self) -> float:
        return self.success_count / max(self.total_calls, 1)
    
    @property
    def recent_avg_duration(self) -> float:
        return sum(self.recent_durations) / max(len(self.recent_durations), 1)
    
    def add_measurement(self, duration: float, success: bool = True):
        """Add a new measurement."""
        self.total_calls += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.recent_durations.append(duration)
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_name": self.operation_name,
            "total_calls": self.total_calls,
            "avg_duration": self.avg_duration,
            "min_duration": self.min_duration if self.min_duration != float('inf') else 0,
            "max_duration": self.max_duration,
            "recent_avg_duration": self.recent_avg_duration,
            "success_rate": self.success_rate,
            "error_count": self.error_count,
            "success_count": self.success_count
        }


class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()
        self.metrics: List[PerformanceMetric] = []
        self.operation_stats: Dict[str, OperationStats] = defaultdict(lambda: OperationStats(""))
        self.system_metrics: Dict[str, Any] = {}
        self.monitoring_active = True
        self.lock = threading.Lock()
        
        # Start background monitoring if enabled
        if self.config.performance.enable_metrics:
            self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background thread for system metrics collection."""
        def monitor_loop():
            while self.monitoring_active:
                try:
                    self._collect_system_metrics()
                    time.sleep(30)  # Collect every 30 seconds
                except Exception as e:
                    self.logger.logger.error(f"Error in background monitoring: {e}")
                    time.sleep(60)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.logger.info("Background performance monitoring started")
    
    def _collect_system_metrics(self):
        """Collect system-level performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system.cpu.usage", cpu_percent, "percent")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_metric("system.memory.usage", memory.percent, "percent")
            self.record_metric("system.memory.available", memory.available / 1024**3, "GB")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("system.disk.usage", disk_percent, "percent")
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                self.record_metric("system.network.bytes_sent", network.bytes_sent, "bytes")
                self.record_metric("system.network.bytes_recv", network.bytes_recv, "bytes")
            except:
                pass  # Network metrics might not be available
            
            # Process-specific metrics
            process = psutil.Process()
            self.record_metric("process.memory.rss", process.memory_info().rss / 1024**2, "MB")
            self.record_metric("process.cpu.percent", process.cpu_percent(), "percent")
            
        except Exception as e:
            self.logger.logger.warning(f"Error collecting system metrics: {e}")
    
    def record_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Record a performance metric."""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            
            self.metrics.append(metric)
            
            # Keep only recent metrics to prevent memory bloat
            max_metrics = 10000
            if len(self.metrics) > max_metrics:
                self.metrics = self.metrics[-max_metrics:]
    
    def record_operation(self, operation_name: str, duration: float, 
                        success: bool = True, tags: Dict[str, str] = None):
        """Record an operation's performance."""
        with self.lock:
            # Update operation statistics
            if operation_name not in self.operation_stats:
                self.operation_stats[operation_name] = OperationStats(operation_name)
            
            self.operation_stats[operation_name].add_measurement(duration, success)
            
            # Record as metric
            self.record_metric(
                f"operation.{operation_name}.duration",
                duration,
                "seconds",
                {**(tags or {}), "success": str(success)}
            )
    
    def get_operation_stats(self, operation_name: str = None) -> Dict[str, Any]:
        """Get operation statistics."""
        with self.lock:
            if operation_name:
                stats = self.operation_stats.get(operation_name)
                return stats.to_dict() if stats else {}
            
            return {name: stats.to_dict() for name, stats in self.operation_stats.items()}
    
    def get_recent_metrics(self, minutes: int = 30) -> List[PerformanceMetric]:
        """Get metrics from the last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            return [m for m in self.metrics if m.timestamp >= cutoff]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            health = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {}
            }
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            health["checks"]["cpu"] = {
                "usage_percent": cpu_percent,
                "status": "warning" if cpu_percent > 80 else "ok"
            }
            
            # Memory check
            memory = psutil.virtual_memory()
            health["checks"]["memory"] = {
                "usage_percent": memory.percent,
                "available_gb": memory.available / 1024**3,
                "status": "warning" if memory.percent > 85 else "ok"
            }
            
            # Disk check
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            health["checks"]["disk"] = {
                "usage_percent": disk_percent,
                "free_gb": disk.free / 1024**3,
                "status": "warning" if disk_percent > 90 else "ok"
            }
            
            # Operation health
            recent_errors = sum(1 for stats in self.operation_stats.values() 
                              if stats.error_count > 0 and stats.success_rate < 0.9)
            health["checks"]["operations"] = {
                "operations_with_errors": recent_errors,
                "status": "warning" if recent_errors > 5 else "ok"
            }
            
            # Overall status
            warning_checks = sum(1 for check in health["checks"].values() 
                               if check["status"] == "warning")
            if warning_checks > 0:
                health["status"] = "warning"
            
            return health
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "operations": {},
            "system_health": self.get_system_health(),
            "recommendations": []
        }
        
        with self.lock:
            # Operation summary
            report["operations"] = self.get_operation_stats()
            
            # Overall summary
            total_operations = sum(stats.total_calls for stats in self.operation_stats.values())
            total_errors = sum(stats.error_count for stats in self.operation_stats.values())
            
            report["summary"] = {
                "total_operations": total_operations,
                "total_errors": total_errors,
                "overall_success_rate": (total_operations - total_errors) / max(total_operations, 1),
                "unique_operations": len(self.operation_stats),
                "monitoring_duration_hours": self._get_monitoring_duration_hours()
            }
            
            # Generate recommendations
            report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _get_monitoring_duration_hours(self) -> float:
        """Get how long monitoring has been active."""
        if self.metrics:
            earliest = min(m.timestamp for m in self.metrics)
            return (datetime.now() - earliest).total_seconds() / 3600
        return 0
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Check for slow operations
        for stats in self.operation_stats.values():
            if stats.avg_duration > 5.0 and stats.total_calls > 10:
                recommendations.append(
                    f"Operation '{stats.operation_name}' is slow (avg: {stats.avg_duration:.2f}s). "
                    "Consider optimization or caching."
                )
        
        # Check for high error rates
        for stats in self.operation_stats.values():
            if stats.success_rate < 0.9 and stats.total_calls > 5:
                recommendations.append(
                    f"Operation '{stats.operation_name}' has high error rate "
                    f"({(1-stats.success_rate)*100:.1f}%). Check error handling."
                )
        
        # System resource recommendations
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                recommendations.append(
                    f"High memory usage ({memory.percent:.1f}%). Consider increasing memory or "
                    "optimizing memory-intensive operations."
                )
            
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                recommendations.append(
                    f"High CPU usage ({cpu_percent:.1f}%). Consider optimizing CPU-intensive operations."
                )
        except:
            pass
        
        return recommendations
    
    def export_metrics(self, filepath: str, format: str = "json"):
        """Export metrics to file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            data = {
                "performance_report": self.generate_performance_report(),
                "recent_metrics": [m.to_dict() for m in self.get_recent_metrics(60)]
            }
            
            with open(filepath, 'w') as f:
                if format.lower() == "json":
                    json.dump(data, f, indent=2, default=str)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            self.logger.logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            self.logger.logger.error(f"Error exporting metrics: {e}")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        self.logger.logger.info("Performance monitoring stopped")


def performance_monitor(operation_name: str = None):
    """Decorator for automatic performance monitoring of functions."""
    def decorator(func):
        nonlocal operation_name
        if operation_name is None:
            operation_name = f"{func.__module__}.{func.__name__}"
        
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                get_performance_monitor().record_operation(operation_name, duration, success)
        
        return wrapper
    return decorator


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor