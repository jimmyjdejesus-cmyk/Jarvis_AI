
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# API Contracts and Specifications

This directory contains comprehensive API contracts and specifications for the
Jarvis AI platform. It provides machine-readable definitions that enable
automated client generation, schema validation, and professional API
documentation.

## 📁 File Structure

```
├── openapi.yaml                    # Main OpenAPI 3.0 specification
├── api_schemas/                    # Reusable JSON Schema components
│   ├── chat_models.yaml           # Chat and messaging models
│   ├── agent_models.yaml          # Agent execution models
│   ├── workflow_models.yaml       # Workflow execution models
│   ├── security_models.yaml       # Security and validation models
│   ├── monitoring_models.yaml     # Monitoring and metrics models
│   └── job_models.yaml           # Job processing models
└── postman/                       # API testing collections
    └── Jarvis_API_v1.postman_collection.json
```

## 🚀 Quick Start

### 1. **View API Documentation**
- **OpenAPI UI**: Use tools like [Swagger UI](https://swagger.io/tools/swagger-ui/)
  or [Redoc](https://redocly.com/redoc/) to visualize the API
- **Local viewing**: Serve the `openapi.yaml` file through any OpenAPI-compatible documentation tool

### 2. **Generate Client SDKs**
```bash
# Using OpenAPI Generator
openapi-generator-cli generate -i openapi.yaml -g python -o ./generated/python_client

# Using Swagger Codegen
swagger-codegen generate -i openapi.yaml -l python -o ./generated/python_client
```

### 3. **Validate API Requests**
Use the provided JSON schemas to validate requests before sending them to the API.

## 📊 API Overview

### **Base Information**
- **Version**: 1.0.0
- **Base URL**: `http://127.0.0.1:8000/api/v1`
- **Authentication**: `X-API-Key` header required
- **Format**: JSON (requests/responses)

### **Available Endpoints**

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Health** | `GET /health` | System health checks |
| **Models** | `GET /models` | Available AI models |
| **Chat** | `POST /chat`, `POST /chat/stream` | Chat completion (sync & streaming) |
| **Agents** | `GET /agents`, `POST /agents/execute`, `POST /agents/collaborate` | Agent management & execution |
| **Memory** | `GET /memory/stats`, `POST /memory/*` | Memory management & migration |
| **Workflows** | `POST /workflows/execute`, `GET /workflows/*` | Workflow execution & monitoring |
| **Security** | `POST /security/validate`, `GET /security/*` | Security validation & auditing |
| **Monitoring** | `GET /monitoring/*` | System monitoring & metrics |
| **Feed** | `POST /feed/ingest` | Content ingestion |
| **Jobs** | `POST /jobs`, `GET /jobs/{id}` | Asynchronous job processing |

### **Schema Statistics**
- **Total Schemas**: 31 reusable components
- **Request Models**: 15 request schemas
- **Response Models**: 16 response schemas
- **Schema Files**: 6 modular YAML files

## 🛠 Usage Examples

### **Chat Request Example**
```yaml
# Request
POST /api/v1/chat
Content-Type: application/json
X-API-Key: your-api-key

{
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "model": "llama3.1:8b-instruct-q4_K_M",
  "temperature": 0.7,
  "max_tokens": 100
}

# Response
{
  "content": "I'm doing well, thank you for asking! How can I help you today?",
  "model": "llama3.1:8b-instruct-q4_K_M"
}
```

### **Agent Execution Example**
```yaml
# Request
POST /api/v1/agents/execute
Content-Type: application/json
X-API-Key: your-api-key

{
  "agent_type": "code_assistant",
  "objective": "Write a Python function to sort a list",
  "context": {"language": "python"},
  "priority": 8,
  "timeout": 300
}

# Response
{
  "result": {
    "code": "def sort_list(items):\n    return sorted(items)",
    "language": "python"
  },
  "agent_type": "code_assistant",
  "success": true,
  "execution_time": 1.23
}
```

## 🔒 Authentication

All endpoints require authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://127.0.0.1:8000/api/v1/health
```

For local development, set `JARVIS_DISABLE_AUTH=true` to bypass authentication.

## 🧪 Testing

### **Postman Collection**
Import the provided Postman collection (`postman/Jarvis_API_v1.postman_collection.json`) for:
- Pre-configured environment variables
- Sample requests for all endpoints
- Authentication setup
- Request/response validation

### **Manual Testing**
```bash
# Health check
curl -H "X-API-Key: your-key" http://127.0.0.1:8000/api/v1/health

# List models
curl -H "X-API-Key: your-key" http://127.0.0.1:8000/api/v1/models

# Chat completion
curl -X POST -H "X-API-Key: your-key" -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}' \
  http://127.0.0.1:8000/api/v1/chat
```

## 🔧 Schema Validation

### **Request Validation**
Validate requests against the appropriate schema before sending:

```python
import yaml
from jsonschema import validate, ValidationError

# Load schema
with open('api_schemas/chat_models.yaml') as f:
    chat_schemas = yaml.safe_load(f)

# Validate request
request_data = {
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7
}

try:
    validate(request_data, chat_schemas['ChatRequest'])
    print("✅ Request is valid")
except ValidationError as e:
    print(f"❌ Validation error: {e.message}")
```

## 📈 Benefits

### **For Developers**
- **Auto-generated clients** in multiple languages
- **Schema validation** for request/response integrity
- **IDE support** with auto-completion and type hints
- **Contract testing** to ensure API compatibility

### **For API Consumers**
- **Interactive documentation** with examples
- **Clear error messages** with detailed schemas
- **Version compatibility** checking
- **Multiple language support** via generated SDKs

### **For API Maintainers**
- **Centralized contract definition** in one place
- **Breaking change detection** through schema validation
- **Automated documentation generation**
- **Consistent API design** patterns

## 🔄 Maintenance

### **Updating Schemas**
1. Modify the appropriate schema file in `api_schemas/`
2. Update the main `openapi.yaml` if needed
3. Validate the changes using OpenAPI tools
4. Test with the Postman collection
5. Update client SDKs if necessary

### **Validation Tools**
- **OpenAPI Validator**: Validate OpenAPI 3.0 specification
- **JSON Schema Validator**: Validate request/response schemas
- **API Linting**: Tools like `spectral` for API design consistency

## 📚 Additional Resources

- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.3)
- [JSON Schema Documentation](https://json-schema.org/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Postman API Platform](https://www.postman.com/)

---

**Generated**: 2025-12-12T12:42:43Z
**Version**: 1.0.0
**Status**: Production Ready ✅
