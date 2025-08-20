#!/usr/bin/env python3
"""
OpenAPI specification generator for Jarvis AI Plugin System.

This module generates OpenAPI documentation for the plugin system APIs,
enabling third-party integrations and providing clear API documentation.
"""

from typing import Any, Dict, List, Optional
import json
import yaml
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.openapi.utils import get_openapi
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    # Fallback for when FastAPI is not available
    class BaseModel:
        pass
    def Field(**kwargs):
        return None
    FASTAPI_AVAILABLE = False

from agent.adapters.plugin_base import PluginType
from agent.adapters.extensibility_sdk import PluginManifest


# Pydantic models for API documentation
class PluginMetadataModel(BaseModel):
    """API model for plugin metadata."""
    name: str = Field(default=..., description="Unique name of the plugin")
    description: str = Field(default=..., description="Description of what the plugin does")
    version: str = Field(default=..., description="Plugin version in semver format")
    author: str = Field(default=..., description="Plugin author or organization")
    plugin_type: str = Field(default=..., description="Type of plugin (automation, integration, command, workflow)")
    triggers: List[str] = Field(default=[], description="Natural language triggers for the plugin")
    dependencies: List[str] = Field(default=[], description="List of required dependencies")
    tags: List[str] = Field(default=[], description="Tags for categorizing the plugin")


class PluginActionModel(BaseModel):
    """API model for plugin actions."""
    name: str = Field(default=..., description="Name of the action")
    description: str = Field(default=..., description="Description of what the action does")
    args: Dict[str, Any] = Field(default={}, description="Arguments for the action")
    preview: str = Field(default="", description="Preview of what the action will do")
    requires_approval: bool = Field(default=False, description="Whether the action requires user approval")


class PluginResultModel(BaseModel):
    """API model for plugin execution results."""
    success: bool = Field(default=..., description="Whether the action was successful")
    output: Optional[Any] = Field(default=None, description="Output from the action execution")
    error: Optional[str] = Field(default=None, description="Error message if the action failed")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata about the execution")


class PluginRegistrationModel(BaseModel):
    """API model for plugin registration."""
    plugin_manifest: PluginManifest = Field(default=..., description="Plugin manifest with metadata")
    entry_point: str = Field(default=..., description="Entry point module path")
    installation_path: str = Field(default=..., description="Path where the plugin is installed")


class PluginQueryModel(BaseModel):
    """API model for querying plugins."""
    command: str = Field(default=..., description="Natural language command to match against plugins")
    context: Dict[str, Any] = Field(default={}, description="Context information for command parsing")
    plugin_types: Optional[List[str]] = Field(None, description="Filter by plugin types")
    tags: Optional[List[str]] = Field(None, description="Filter by plugin tags")


class KnowledgeSourceQueryModel(BaseModel):
    """API model for knowledge source queries."""
    query: str = Field(default=..., description="Query string")
    max_results: int = Field(default=10, description="Maximum number of results to return")
    source_filter: Optional[List[str]] = Field(None, description="Filter by knowledge source names")
    context: Dict[str, Any] = Field(default={}, description="Additional context for the query")


class BuildCommandModel(BaseModel):
    """API model for build system commands."""
    project_path: str = Field(default=..., description="Path to the project")
    command: str = Field(default=..., description="Build command to execute")
    options: Dict[str, Any] = Field(default={}, description="Additional options for the command")


class TestCommandModel(BaseModel):
    """API model for testing framework commands."""
    project_path: str = Field(default=..., description="Path to the project")
    test_path: Optional[str] = Field(None, description="Specific test file or directory")
    framework: Optional[str] = Field(None, description="Testing framework to use (auto-detected if not specified)")
    options: Dict[str, Any] = Field(default={}, description="Additional options for test execution")


def create_plugin_api_spec() -> Dict[str, Any]:
    """Create OpenAPI specification for the Jarvis AI Plugin System."""
    
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Jarvis AI Plugin System API",
            "description": "API for interacting with the Jarvis AI extensibility framework, including plugin management, execution, and discovery.",
            "version": "1.0.0",
            "contact": {
                "name": "Jarvis AI Support",
                "url": "https://github.com/jimmyjdejesus-cmyk/Jarvis_AI",
                "email": "support@jarvis-ai.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Local development server"
            },
            {
                "url": "https://api.jarvis-ai.com",
                "description": "Production server"
            }
        ],
        "paths": {
            "/api/v1/plugins": {
                "get": {
                    "summary": "List all registered plugins",
                    "description": "Retrieve a list of all plugins registered in the system",
                    "tags": ["Plugins"],
                    "parameters": [
                        {
                            "name": "plugin_type",
                            "in": "query",
                            "description": "Filter by plugin type",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["automation", "integration", "command", "workflow"]
                            }
                        },
                        {
                            "name": "tags",
                            "in": "query",
                            "description": "Filter by tags (comma-separated)",
                            "required": False,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of plugins",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/PluginMetadata"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Register a new plugin",
                    "description": "Register a new plugin with the system",
                    "tags": ["Plugins"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PluginRegistration"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Plugin registered successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "plugin_id": {"type": "string"},
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid plugin data",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/plugins/{plugin_name}": {
                "get": {
                    "summary": "Get plugin details",
                    "description": "Get detailed information about a specific plugin",
                    "tags": ["Plugins"],
                    "parameters": [
                        {
                            "name": "plugin_name",
                            "in": "path",
                            "required": True,
                            "description": "Name of the plugin",
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Plugin details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PluginMetadata"}
                                }
                            }
                        },
                        "404": {
                            "description": "Plugin not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Unregister a plugin",
                    "description": "Remove a plugin from the system",
                    "tags": ["Plugins"],
                    "parameters": [
                        {
                            "name": "plugin_name",
                            "in": "path",
                            "required": True,
                            "description": "Name of the plugin",
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Plugin unregistered successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Plugin not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/plugins/query": {
                "post": {
                    "summary": "Query plugins by command",
                    "description": "Find plugins that can handle a natural language command",
                    "tags": ["Plugins"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PluginQuery"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Matching plugins and parsed actions",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "matching_plugins": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/PluginMetadata"}
                                            },
                                            "suggested_action": {"$ref": "#/components/schemas/PluginAction"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/plugins/execute": {
                "post": {
                    "summary": "Execute a plugin action",
                    "description": "Execute a specific plugin action",
                    "tags": ["Plugins"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PluginAction"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Action executed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PluginResult"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid action data",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/knowledge-sources": {
                "get": {
                    "summary": "List knowledge sources",
                    "description": "Get a list of all available knowledge sources",
                    "tags": ["Knowledge Sources"],
                    "responses": {
                        "200": {
                            "description": "List of knowledge sources",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "description": {"type": "string"},
                                                "type": {"type": "string"},
                                                "capabilities": {"type": "array", "items": {"type": "string"}}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/knowledge-sources/query": {
                "post": {
                    "summary": "Query knowledge sources",
                    "description": "Search across available knowledge sources",
                    "tags": ["Knowledge Sources"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/KnowledgeSourceQuery"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Search results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "results": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {"type": "string"},
                                                        "content": {"type": "string"},
                                                        "source": {"type": "string"},
                                                        "relevance_score": {"type": "number"}
                                                    }
                                                }
                                            },
                                            "total_results": {"type": "integer"},
                                            "query_time": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/build-systems": {
                "get": {
                    "summary": "List supported build systems",
                    "description": "Get a list of all supported build systems",
                    "tags": ["Build Systems"],
                    "responses": {
                        "200": {
                            "description": "List of build systems",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "description": {"type": "string"},
                                                "file_patterns": {"type": "array", "items": {"type": "string"}}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/build-systems/detect": {
                "post": {
                    "summary": "Detect build system",
                    "description": "Detect which build system is used in a project",
                    "tags": ["Build Systems"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "project_path": {"type": "string"}
                                    },
                                    "required": ["project_path"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Detected build systems",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "detected_systems": {"type": "array", "items": {"type": "string"}},
                                            "primary_system": {"type": "string"},
                                            "available_commands": {"type": "array", "items": {"type": "object"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/build-systems/execute": {
                "post": {
                    "summary": "Execute build command",
                    "description": "Execute a build system command",
                    "tags": ["Build Systems"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BuildCommand"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Command execution result",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "output": {"type": "string"},
                                            "error": {"type": "string"},
                                            "return_code": {"type": "integer"},
                                            "execution_time": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/testing-frameworks": {
                "get": {
                    "summary": "List supported testing frameworks",
                    "description": "Get a list of all supported testing frameworks",
                    "tags": ["Testing Frameworks"],
                    "responses": {
                        "200": {
                            "description": "List of testing frameworks",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "description": {"type": "string"},
                                                "file_patterns": {"type": "array", "items": {"type": "string"}}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/testing-frameworks/run": {
                "post": {
                    "summary": "Run tests",
                    "description": "Execute tests using detected or specified testing framework",
                    "tags": ["Testing Frameworks"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TestCommand"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Test execution result",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "output": {"type": "string"},
                                            "error": {"type": "string"},
                                            "return_code": {"type": "integer"},
                                            "tests_passed": {"type": "boolean"},
                                            "test_summary": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "PluginMetadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "author": {"type": "string"},
                        "plugin_type": {"type": "string", "enum": ["automation", "integration", "command", "workflow"]},
                        "triggers": {"type": "array", "items": {"type": "string"}},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name", "description", "version", "author", "plugin_type"]
                },
                "PluginAction": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "args": {"type": "object"},
                        "preview": {"type": "string"},
                        "requires_approval": {"type": "boolean"}
                    },
                    "required": ["name", "description", "args"]
                },
                "PluginResult": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "output": {},
                        "error": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["success"]
                },
                "PluginRegistration": {
                    "type": "object",
                    "properties": {
                        "plugin_manifest": {"$ref": "#/components/schemas/PluginManifest"},
                        "entry_point": {"type": "string"},
                        "installation_path": {"type": "string"}
                    },
                    "required": ["plugin_manifest", "entry_point"]
                },
                "PluginManifest": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "author": {"type": "string"},
                        "license": {"type": "string"},
                        "homepage": {"type": "string"},
                        "repository": {"type": "string"},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "dependencies": {"type": "object"},
                        "plugin_entry_point": {"type": "string"},
                        "supported_platforms": {"type": "array", "items": {"type": "string"}},
                        "min_jarvis_version": {"type": "string"}
                    },
                    "required": ["name", "description", "version", "author"]
                },
                "PluginQuery": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "context": {"type": "object"},
                        "plugin_types": {"type": "array", "items": {"type": "string"}},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["command"]
                },
                "KnowledgeSourceQuery": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer", "default": 10},
                        "source_filter": {"type": "array", "items": {"type": "string"}},
                        "context": {"type": "object"}
                    },
                    "required": ["query"]
                },
                "BuildCommand": {
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string"},
                        "command": {"type": "string"},
                        "options": {"type": "object"}
                    },
                    "required": ["project_path", "command"]
                },
                "TestCommand": {
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string"},
                        "test_path": {"type": "string"},
                        "framework": {"type": "string"},
                        "options": {"type": "object"}
                    },
                    "required": ["project_path"]
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "message": {"type": "string"},
                        "code": {"type": "integer"}
                    },
                    "required": ["error", "message"]
                }
            },
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                },
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer"
                }
            }
        },
        "security": [
            {"ApiKeyAuth": []},
            {"BearerAuth": []}
        ],
        "tags": [
            {
                "name": "Plugins",
                "description": "Plugin management and execution operations"
            },
            {
                "name": "Knowledge Sources",
                "description": "Knowledge source querying and management"
            },
            {
                "name": "Build Systems",
                "description": "Build system detection and execution"
            },
            {
                "name": "Testing Frameworks",
                "description": "Testing framework detection and execution"
            }
        ]
    }
    
    return spec


def save_openapi_spec(output_dir: str = "docs/api"):
    """Save the OpenAPI specification to files."""
    spec = create_plugin_api_spec()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON
    json_path = output_path / "plugin_system_api.json"
    with open(json_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    # Save as YAML
    yaml_path = output_path / "plugin_system_api.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
    
    print(f"OpenAPI specification saved to:")
    print(f"  JSON: {json_path}")
    print(f"  YAML: {yaml_path}")
    
    return json_path, yaml_path


if FASTAPI_AVAILABLE:
    def create_fastapi_app() -> FastAPI:
        """Create a FastAPI application with the plugin system endpoints."""
        
        app = FastAPI(
            title="Jarvis AI Plugin System API",
            description="API for the Jarvis AI extensibility framework",
            version="1.0.0"
        )
        
        # Import plugin system components
        try:
            from agent.adapters.plugin_registry import plugin_manager
            from agent.adapters.extensibility_sdk import PluginSDK
        except ImportError:
            print("Warning: Could not import plugin system components")
        
        @app.get("/api/v1/plugins", response_model=List[PluginMetadataModel])
        async def list_plugins(plugin_type: Optional[str] = None, tags: Optional[str] = None):
            """List all registered plugins."""
            plugins = plugin_manager.registry.list_plugins()
            
            # Apply filters
            if plugin_type:
                plugins = [p for p in plugins if p.metadata.plugin_type.value == plugin_type]
            
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                plugins = [p for p in plugins if any(tag in p.metadata.tags for tag in tag_list)]
            
            return [PluginMetadataModel(
                name=p.metadata.name,
                description=p.metadata.description,
                version=p.metadata.version,
                author=p.metadata.author,
                plugin_type=p.metadata.plugin_type.value,
                triggers=p.metadata.triggers,
                dependencies=p.metadata.dependencies,
                tags=p.metadata.tags
            ) for p in plugins]
        
        @app.get("/api/v1/plugins/{plugin_name}", response_model=PluginMetadataModel)
        async def get_plugin(plugin_name: str):
            """Get details of a specific plugin."""
            plugin = plugin_manager.registry.get_plugin(plugin_name)
            if not plugin:
                raise HTTPException(status_code=404, detail="Plugin not found")
            
            return PluginMetadataModel(
                name=plugin.metadata.name,
                description=plugin.metadata.description,
                version=plugin.metadata.version,
                author=plugin.metadata.author,
                plugin_type=plugin.metadata.plugin_type.value,
                triggers=plugin.metadata.triggers,
                dependencies=plugin.metadata.dependencies,
                tags=plugin.metadata.tags
            )
        
        @app.post("/api/v1/plugins/query")
        async def query_plugins(query: PluginQueryModel):
            """Find plugins that can handle a command."""
            plugins = plugin_manager.registry.find_plugins_for_command(query.command, query.context)
            
            suggested_action = None
            if plugins:
                action = plugins[0].parse_command(query.command, query.context)
                if action:
                    suggested_action = PluginActionModel(
                        name=action.name,
                        description=action.description,
                        args=action.args,
                        preview=action.preview,
                        requires_approval=action.requires_approval
                    )
            
            return {
                "matching_plugins": [PluginMetadataModel(
                    name=p.metadata.name,
                    description=p.metadata.description,
                    version=p.metadata.version,
                    author=p.metadata.author,
                    plugin_type=p.metadata.plugin_type.value,
                    triggers=p.metadata.triggers,
                    dependencies=p.metadata.dependencies,
                    tags=p.metadata.tags
                ) for p in plugins],
                "suggested_action": suggested_action
            }
        
        @app.post("/api/v1/plugins/execute", response_model=PluginResultModel)
        async def execute_plugin_action(action: PluginActionModel):
            """Execute a plugin action."""
            from agent.adapters.plugin_base import PluginAction
            
            plugin_action = PluginAction(
                name=action.name,
                description=action.description,
                args=action.args,
                preview=action.preview,
                requires_approval=action.requires_approval
            )
            
            result = plugin_manager.execute_action(plugin_action)
            
            return PluginResultModel(
                success=result.success,
                output=result.output,
                error=result.error,
                metadata={}
            )
        
        # Override OpenAPI schema
        def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            
            openapi_schema = create_plugin_api_spec()
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        
        app.openapi = custom_openapi
        
        return app


if __name__ == "__main__":
    # Generate and save OpenAPI specification
    print("Generating OpenAPI specification for Jarvis AI Plugin System...")
    save_openapi_spec()
    print("OpenAPI specification generated successfully!")
    
    if FASTAPI_AVAILABLE:
        print("\nStarting FastAPI server...")
        import uvicorn
        app = create_fastapi_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)