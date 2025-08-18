# Admin Model Management

This document describes the admin model management features added to Jarvis AI.

## Features Implemented

### 1. Admin-Only Model Management Tab
- Added a new "🤖 Model Management" tab to the admin panel
- Only accessible to users with admin role
- Located at position 4 in the admin panel tabs

### 2. Endpoint Configuration (Admin-Only)
- Moved endpoint configuration from public sidebar to admin panel
- Admin users can configure:
  - LLM API Endpoint
  - RAG API Endpoint
- Changes are logged for security auditing
- Non-admin users use system defaults

### 3. Model Management Features
- **View Available Models**: Display all installed models with details:
  - Model name
  - Size (in GB)
  - Modified date
- **Pull New Models**: 
  - Enter model name (e.g., llama2:7b, qwen3:4b)
  - Real-time progress display during download
  - Security logging of model pulls
- **Update Models**: 
  - Update existing models with progress feedback
  - Security logging of model updates
- **Delete Models**: 
  - Remove unwanted models
  - Security logging of model deletions

### 4. Security Features
- All model management actions are logged with:
  - Event type (MODEL_PULLED, MODEL_UPDATED, MODEL_DELETED, ENDPOINT_UPDATED)
  - Username of admin performing action
  - Details of the action
- Rate limiting protection
- Admin-only access control

### 5. Enhanced ollama_client Functions
Added new functions to `ollama_client.py`:
- `get_model_details()`: Get detailed model information
- `delete_model(model_name)`: Delete a model via API
- `update_endpoint(new_endpoint)`: Update the Ollama endpoint

## Usage

### Accessing Model Management
1. Log in as an admin user
2. Click "Admin Panel" in the sidebar
3. Navigate to the "🤖 Model Management" tab

### Managing Models
- **View Models**: Automatically displayed when tab is opened
- **Pull New Model**: 
  1. Enter model name in the text input
  2. Click "📥 Pull Model"
  3. Monitor progress in the expandable section
- **Update Model**: Click "🔄 Update" next to any existing model
- **Delete Model**: Click "🗑️ Delete" next to any model (use with caution)

### Configuring Endpoints
- In the Model Management tab, use the "Endpoint Configuration" section
- Enter new LLM and RAG endpoints
- Click "Update Endpoints" to save changes

## Technical Implementation

### Files Modified
1. `app.py`: 
   - Added Model Management tab to admin panel
   - Restricted endpoint configuration to admin users
   - Added security logging for admin actions

2. `ollama_client.py`:
   - Added `get_model_details()` function
   - Added `delete_model()` function  
   - Added `update_endpoint()` function
   - Enhanced error handling

### Security Considerations
- All model management operations require admin privileges
- Comprehensive logging of all admin actions
- Endpoint configuration restricted to admin users
- Progress feedback prevents UI blocking during long operations

## Testing
- Create admin user with proper role
- Test model listing functionality
- Test model pull/update/delete operations
- Verify security logging
- Confirm non-admin users cannot access features