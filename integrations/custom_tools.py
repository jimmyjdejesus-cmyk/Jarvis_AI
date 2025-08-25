#!/usr/bin/env python3
"""
Custom Tools & Plugins System
Create and manage custom tools for your workflows.
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlparse

class ToolBase(ABC):
    """Base class for all custom tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.author = "Custom"
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool's main functionality."""
        pass
    
    def validate_inputs(self, *args, **kwargs) -> bool:
        """Validate input parameters. Override in subclasses."""
        return True
    
    def get_info(self) -> Dict:
        """Get tool information."""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author
        }

class ToolRegistry:
    """Registry for managing custom tools."""
    
    def __init__(self):
        self.tools: Dict[str, ToolBase] = {}
        self.tool_categories: Dict[str, List[str]] = {}
    
    def register_tool(self, tool: ToolBase, category: str = "general"):
        """Register a new tool."""
        self.tools[tool.name] = tool
        
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        
        if tool.name not in self.tool_categories[category]:
            self.tool_categories[category].append(tool.name)
        
        print(f"✅ Registered tool: {tool.name} (category: {category})")
    
    def get_tool(self, name: str) -> ToolBase:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self, category: str = None) -> List[str]:
        """List available tools."""
        if category:
            return self.tool_categories.get(category, [])
        return list(self.tools.keys())
    
    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        if not tool.validate_inputs(*args, **kwargs):
            raise ValueError(f"Invalid inputs for tool '{name}'")
        
        print(f"🛠️ Executing tool: {name}")
        return tool.execute(*args, **kwargs)
    
    def get_tools_by_category(self) -> Dict[str, List[Dict]]:
        """Get tools organized by category."""
        result = {}
        for category, tool_names in self.tool_categories.items():
            result[category] = []
            for name in tool_names:
                tool = self.tools[name]
                result[category].append(tool.get_info())
        return result

# Example Custom Tools

class FileProcessorTool(ToolBase):
    """Tool for processing various file types."""
    
    def __init__(self):
        super().__init__(
            name="file_processor",
            description="Process and analyze different file types (CSV, JSON, TXT, etc.)"
        )
    
    def execute(self, file_path: str, operation: str = "analyze") -> Dict:
        """Process a file based on the operation."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        file_info = {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix,
            "operation": operation
        }
        
        if operation == "analyze":
            return self._analyze_file(file_path, file_info)
        elif operation == "read":
            return self._read_file(file_path, file_info)
        elif operation == "convert":
            return self._convert_file(file_path, file_info)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _analyze_file(self, file_path: Path, file_info: Dict) -> Dict:
        """Analyze file contents."""
        result = file_info.copy()
        
        if file_path.suffix == '.csv':
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                result.update({
                    "rows": len(df),
                    "columns": list(df.columns),
                    "data_types": df.dtypes.to_dict()
                })
            except Exception as e:
                result["error"] = f"CSV analysis failed: {e}"
                
        elif file_path.suffix == '.json':
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                result.update({
                    "type": type(data).__name__,
                    "keys": list(data.keys()) if isinstance(data, dict) else None,
                    "length": len(data) if isinstance(data, (list, dict)) else None
                })
            except Exception as e:
                result["error"] = f"JSON analysis failed: {e}"
                
        elif file_path.suffix == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result.update({
                    "lines": len(content.split('\n')),
                    "words": len(content.split()),
                    "characters": len(content)
                })
            except Exception as e:
                result["error"] = f"Text analysis failed: {e}"
        
        return result
    
    def _read_file(self, file_path: Path, file_info: Dict) -> Dict:
        """Read file contents."""
        result = file_info.copy()
        
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    result["content"] = json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result["content"] = f.read()
        except Exception as e:
            result["error"] = f"Read failed: {e}"
        
        return result
    
    def _convert_file(self, file_path: Path, file_info: Dict) -> Dict:
        """Convert file to different format."""
        result = file_info.copy()
        result["conversion"] = "Feature not implemented in demo"
        return result

class WebScraperTool(ToolBase):
    """Tool for web scraping and content extraction."""
    
    def __init__(self):
        super().__init__(
            name="web_scraper",
            description="Extract content from web pages"
        )
    
    def execute(self, url: str, selector: str = None, extract_type: str = "text") -> Dict:
        """Scrape content from a web page."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("url must include http or https scheme")
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                "url": url,
                "status_code": response.status_code,
                "title": soup.title.string if soup.title else "No title"
            }
            
            if selector:
                elements = soup.select(selector)
                if extract_type == "text":
                    result["content"] = [elem.get_text().strip() for elem in elements]
                elif extract_type == "html":
                    result["content"] = [str(elem) for elem in elements]
                elif extract_type == "attributes":
                    result["content"] = [elem.attrs for elem in elements]
            else:
                # Extract all text
                result["content"] = soup.get_text().strip()
            
            return result
            
        except ImportError:
            return {"error": "BeautifulSoup4 and requests required: pip install beautifulsoup4 requests"}
        except Exception as e:
            return {"error": f"Scraping failed: {e}"}

class DataAnalyticsTool(ToolBase):
    """Tool for basic data analytics and statistics."""
    
    def __init__(self):
        super().__init__(
            name="data_analytics",
            description="Perform statistical analysis on datasets"
        )
    
    def execute(self, data: List[float], analysis_type: str = "summary") -> Dict:
        """Perform data analysis."""
        if not data or not all(isinstance(x, (int, float)) for x in data):
            return {"error": "Data must be a list of numbers"}
        
        result = {
            "data_points": len(data),
            "analysis_type": analysis_type
        }
        
        if analysis_type == "summary":
            result.update(self._summary_statistics(data))
        elif analysis_type == "distribution":
            result.update(self._distribution_analysis(data))
        elif analysis_type == "outliers":
            result.update(self._outlier_detection(data))
        
        return result
    
    def _summary_statistics(self, data: List[float]) -> Dict:
        """Calculate summary statistics."""
        import statistics
        
        return {
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "mode": statistics.multimode(data),
            "std_dev": statistics.stdev(data) if len(data) > 1 else 0,
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data)
        }
    
    def _distribution_analysis(self, data: List[float]) -> Dict:
        """Analyze data distribution."""
        import statistics
        
        sorted_data = sorted(data)
        n = len(data)
        
        return {
            "quartiles": {
                "q1": sorted_data[n//4],
                "q2": statistics.median(data),
                "q3": sorted_data[3*n//4]
            },
            "percentiles": {
                "p10": sorted_data[n//10],
                "p90": sorted_data[9*n//10]
            }
        }
    
    def _outlier_detection(self, data: List[float]) -> Dict:
        """Detect outliers using IQR method."""
        import statistics
        
        sorted_data = sorted(data)
        n = len(data)
        q1 = sorted_data[n//4]
        q3 = sorted_data[3*n//4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [x for x in data if x < lower_bound or x > upper_bound]
        
        return {
            "outliers": outliers,
            "outlier_count": len(outliers),
            "outlier_percentage": len(outliers) / len(data) * 100,
            "bounds": {"lower": lower_bound, "upper": upper_bound}
        }

class NotificationTool(ToolBase):
    """Tool for sending notifications through various channels."""
    
    def __init__(self):
        super().__init__(
            name="notification",
            description="Send notifications via email, Slack, or webhooks"
        )
    
    def execute(self, message: str, channel: str = "console", **kwargs) -> Dict:
        """Send notification through specified channel."""
        if channel == "console":
            return self._console_notification(message)
        elif channel == "email":
            return self._email_notification(message, kwargs.get("to"), kwargs.get("subject"))
        elif channel == "slack":
            return self._slack_notification(message, kwargs.get("slack_channel"))
        elif channel == "webhook":
            return self._webhook_notification(message, kwargs.get("webhook_url"))
        else:
            return {"error": f"Unknown notification channel: {channel}"}
    
    def _console_notification(self, message: str) -> Dict:
        """Send console notification."""
        print(f"🔔 Notification: {message}")
        return {"status": "sent", "channel": "console", "message": message}
    
    def _email_notification(self, message: str, to: str, subject: str = "Notification") -> Dict:
        """Send email notification (placeholder)."""
        # In a real implementation, you'd use smtplib or a service like SendGrid
        return {
            "status": "simulated",
            "channel": "email",
            "to": to,
            "subject": subject,
            "message": "Email sending requires SMTP configuration"
        }
    
    def _slack_notification(self, message: str, slack_channel: str) -> Dict:
        """Send Slack notification (placeholder)."""
        # Would use Slack API integration
        return {
            "status": "simulated",
            "channel": "slack",
            "slack_channel": slack_channel,
            "message": "Slack integration requires API token"
        }
    
    def _webhook_notification(self, message: str, webhook_url: str) -> Dict:
        """Send webhook notification."""
        parsed = urlparse(webhook_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("webhook_url must include http or https scheme")
        try:
            import requests

            payload = {"message": message, "timestamp": str(datetime.now())}
            response = requests.post(webhook_url, json=payload, timeout=10)

            return {
                "status": "sent",
                "channel": "webhook",
                "url": webhook_url,
                "response_code": response.status_code
            }
        except Exception as e:
            return {"error": f"Webhook failed: {e}"}

# Tool-Integrated Workflow Example
class CustomToolWorkflow:
    """Example workflow that uses custom tools."""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools."""
        self.registry.register_tool(FileProcessorTool(), "data")
        self.registry.register_tool(WebScraperTool(), "web")
        self.registry.register_tool(DataAnalyticsTool(), "analytics")
        self.registry.register_tool(NotificationTool(), "communication")
    
    def process_file_and_analyze(self, file_path: str):
        """Workflow: Process file and perform analytics."""
        print("📊 File Processing & Analytics Workflow")
        print("=" * 40)
        
        # Step 1: Analyze file
        file_analysis = self.registry.execute_tool("file_processor", file_path, "analyze")
        print(f"📁 File analysis: {file_analysis.get('name', 'Unknown')}")
        
        # Step 2: If it's CSV with numeric data, perform analytics
        if file_analysis.get("extension") == ".csv" and not file_analysis.get("error"):
            try:
                # Read the file to get data for analytics
                file_content = self.registry.execute_tool("file_processor", file_path, "read")
                
                # Simulate extracting numeric data (in real scenario, you'd parse CSV)
                sample_data = [1, 2, 3, 4, 5, 10, 2, 3, 4, 100]  # Simulated data
                
                analytics = self.registry.execute_tool("data_analytics", sample_data, "summary")
                print(f"📈 Analytics: Mean = {analytics.get('mean', 'N/A')}")
                
                # Step 3: Send notification
                self.registry.execute_tool(
                    "notification",
                    f"File analysis complete for {file_analysis.get('name')}",
                    "console"
                )
                
            except Exception as e:
                print(f"❌ Analytics failed: {e}")
        
        return file_analysis
    
    def web_research_workflow(self, url: str, topic: str):
        """Workflow: Web research and summarization."""
        print("🔍 Web Research Workflow")
        print("=" * 30)
        
        # Step 1: Scrape content
        content = self.registry.execute_tool("web_scraper", url)
        
        if not content.get("error"):
            print(f"📄 Scraped: {content.get('title', 'Unknown')}")
            
            # Step 2: Notify about completion
            self.registry.execute_tool(
                "notification",
                f"Web research completed for topic: {topic}",
                "console"
            )
        else:
            print(f"❌ Scraping failed: {content.get('error')}")
        
        return content
    
    def list_available_tools(self):
        """List all available tools by category."""
        print("🛠️ Available Tools")
        print("=" * 20)
        
        tools_by_category = self.registry.get_tools_by_category()
        for category, tools in tools_by_category.items():
            print(f"\n📂 {category.title()}:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")

def demo_custom_tools():
    """Demonstrate custom tools system."""
    print("🛠️ Custom Tools Demo")
    print("=" * 25)
    
    workflow = CustomToolWorkflow()
    
    # List available tools
    workflow.list_available_tools()
    
    print("\n" + "=" * 40)
    
    # Demo file processing (create a sample file first)
    sample_file = Path("sample_data.txt")
    with open(sample_file, 'w') as f:
        f.write("This is a sample text file for testing.\nIt has multiple lines.\nAnd some content to analyze.")
    
    print("\n📁 Demo: File Processing")
    result = workflow.process_file_and_analyze(str(sample_file))
    print(f"   Result: {result.get('lines', 'N/A')} lines, {result.get('words', 'N/A')} words")
    
    # Clean up
    sample_file.unlink()
    
    print("\n" + "=" * 40)
    print("✅ Custom tools demo completed!")

if __name__ == "__main__":
    demo_custom_tools()
