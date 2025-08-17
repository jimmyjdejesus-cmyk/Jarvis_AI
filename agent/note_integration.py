"""
Note-taking Integration Module
Provides integration with note-taking services like Notion and OneNote.
Supports saving text, creating pages, and organizing notes.
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64


class NotionIntegration:
    def __init__(self, integration_token: str = None, database_id: str = None):
        """
        Initialize Notion integration.
        
        Args:
            integration_token: Notion integration token
            database_id: Default database ID for storing notes
        """
        self.token = integration_token or os.getenv('NOTION_TOKEN')
        self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')
        self.base_url = 'https://api.notion.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.token}' if self.token else '',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to Notion API."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
            
            if response.status_code < 300:
                return response.json() if response.content else {"status": "success"}
            else:
                return {
                    "error": f"Notion API error: HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def create_page(self, title: str, content: str, database_id: str = None,
                   tags: List[str] = None, properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new page in Notion.
        
        Args:
            title: Page title
            content: Page content (markdown or plain text)
            database_id: Database ID (uses default if not provided)
            tags: List of tags
            properties: Additional page properties
        
        Returns:
            Created page information
        """
        if not self.token:
            return {"error": "Notion token not configured"}
        
        db_id = database_id or self.database_id
        if not db_id:
            return {"error": "No database ID provided"}
        
        # Build page data
        page_data = {
            "parent": {"database_id": db_id},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
            "children": self._content_to_blocks(content)
        }
        
        # Add tags if provided
        if tags:
            page_data["properties"]["Tags"] = {
                "multi_select": [{"name": tag} for tag in tags]
            }
        
        # Add custom properties
        if properties:
            page_data["properties"].update(properties)
        
        return self._make_request('POST', 'pages', page_data)
    
    def append_to_page(self, page_id: str, content: str) -> Dict[str, Any]:
        """
        Append content to an existing page.
        
        Args:
            page_id: Notion page ID
            content: Content to append
        
        Returns:
            Operation result
        """
        if not self.token:
            return {"error": "Notion token not configured"}
        
        blocks = self._content_to_blocks(content)
        
        data = {
            "children": blocks
        }
        
        return self._make_request('PATCH', f'blocks/{page_id}/children', data)
    
    def search_pages(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """
        Search for pages in Notion.
        
        Args:
            query: Search query
            page_size: Number of results to return
        
        Returns:
            Search results
        """
        if not self.token:
            return {"error": "Notion token not configured"}
        
        search_data = {
            "query": query,
            "page_size": page_size,
            "filter": {
                "value": "page",
                "property": "object"
            }
        }
        
        return self._make_request('POST', 'search', search_data)
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get page information."""
        if not self.token:
            return {"error": "Notion token not configured"}
        
        return self._make_request('GET', f'pages/{page_id}')
    
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get page content blocks."""
        if not self.token:
            return {"error": "Notion token not configured"}
        
        return self._make_request('GET', f'blocks/{page_id}/children')
    
    def _content_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Convert text content to Notion blocks."""
        if not content.strip():
            return []
        
        # Simple implementation - split by double newlines for paragraphs
        paragraphs = content.split('\n\n')
        blocks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if it's a heading
            if paragraph.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph[2:]}}]
                    }
                })
            elif paragraph.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph[3:]}}]
                    }
                })
            elif paragraph.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph[4:]}}]
                    }
                })
            elif paragraph.startswith('- ') or paragraph.startswith('* '):
                # Bulleted list
                items = paragraph.split('\n')
                for item in items:
                    item = item.strip()
                    if item.startswith(('- ', '* ')):
                        blocks.append({
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [{"type": "text", "text": {"content": item[2:]}}]
                            }
                        })
            else:
                # Regular paragraph
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph}}]
                    }
                })
        
        return blocks


class OneNoteIntegration:
    def __init__(self, access_token: str = None):
        """
        Initialize OneNote integration.
        
        Args:
            access_token: Microsoft Graph access token
        """
        self.token = access_token or os.getenv('ONENOTE_TOKEN')
        self.base_url = 'https://graph.microsoft.com/v1.0/me/onenote'
        self.headers = {
            'Authorization': f'Bearer {self.token}' if self.token else '',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     content_type: str = 'application/json') -> Dict[str, Any]:
        """Make authenticated request to Microsoft Graph API."""
        url = f"{self.base_url}/{endpoint}"
        headers = self.headers.copy()
        headers['Content-Type'] = content_type
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                if content_type == 'application/json':
                    response = requests.post(url, headers=headers, json=data)
                else:
                    response = requests.post(url, headers=headers, data=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
            
            if response.status_code < 300:
                return response.json() if response.content else {"status": "success"}
            else:
                return {
                    "error": f"OneNote API error: HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def list_notebooks(self) -> Dict[str, Any]:
        """List OneNote notebooks."""
        if not self.token:
            return {"error": "OneNote token not configured"}
        
        return self._make_request('GET', 'notebooks')
    
    def list_sections(self, notebook_id: str = None) -> Dict[str, Any]:
        """List sections in a notebook."""
        if not self.token:
            return {"error": "OneNote token not configured"}
        
        if notebook_id:
            endpoint = f'notebooks/{notebook_id}/sections'
        else:
            endpoint = 'sections'
        
        return self._make_request('GET', endpoint)
    
    def create_page(self, section_id: str, title: str, content: str) -> Dict[str, Any]:
        """
        Create a new page in OneNote.
        
        Args:
            section_id: OneNote section ID
            title: Page title
            content: Page content (HTML)
        
        Returns:
            Created page information
        """
        if not self.token:
            return {"error": "OneNote token not configured"}
        
        # Convert content to HTML if it's plain text
        if not content.strip().startswith('<'):
            content = self._text_to_html(content)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        return self._make_request('POST', f'sections/{section_id}/pages', 
                                html_content, 'text/html')
    
    def search_pages(self, query: str) -> Dict[str, Any]:
        """Search for pages in OneNote."""
        if not self.token:
            return {"error": "OneNote token not configured"}
        
        endpoint = f'pages?$search={query}'
        return self._make_request('GET', endpoint)
    
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get page content."""
        if not self.token:
            return {"error": "OneNote token not configured"}
        
        return self._make_request('GET', f'pages/{page_id}/content')
    
    def _text_to_html(self, text: str) -> str:
        """Convert plain text to basic HTML."""
        if not text.strip():
            return ""
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        html_parts = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check for headings
            if paragraph.startswith('# '):
                html_parts.append(f'<h1>{paragraph[2:]}</h1>')
            elif paragraph.startswith('## '):
                html_parts.append(f'<h2>{paragraph[3:]}</h2>')
            elif paragraph.startswith('### '):
                html_parts.append(f'<h3>{paragraph[4:]}</h3>')
            elif paragraph.startswith('- ') or paragraph.startswith('* '):
                # Handle lists
                items = paragraph.split('\n')
                list_html = '<ul>'
                for item in items:
                    item = item.strip()
                    if item.startswith(('- ', '* ')):
                        list_html += f'<li>{item[2:]}</li>'
                list_html += '</ul>'
                html_parts.append(list_html)
            else:
                # Regular paragraph - preserve line breaks
                paragraph_html = paragraph.replace('\n', '<br/>')
                html_parts.append(f'<p>{paragraph_html}</p>')
        
        return '\n'.join(html_parts)


class NoteManager:
    """Unified note management interface."""
    
    def __init__(self, notion_token: str = None, notion_db_id: str = None,
                 onenote_token: str = None):
        self.notion = NotionIntegration(notion_token, notion_db_id)
        self.onenote = OneNoteIntegration(onenote_token)
    
    def save_note(self, text: str, service: str = 'notion', title: str = None,
                 tags: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Save note to specified service.
        
        Args:
            text: Note content
            service: Service to use ('notion' or 'onenote')
            title: Note title (auto-generated if not provided)
            tags: Note tags
            **kwargs: Service-specific parameters
        
        Returns:
            Save operation result
        """
        if not title:
            # Generate title from first line or timestamp
            first_line = text.split('\n')[0].strip()
            if len(first_line) > 50:
                title = first_line[:47] + "..."
            elif first_line:
                title = first_line
            else:
                title = f"Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        if service.lower() == 'notion':
            return self.notion.create_page(title, text, tags=tags, **kwargs)
        elif service.lower() == 'onenote':
            # OneNote requires section_id
            section_id = kwargs.get('section_id')
            if not section_id:
                return {"error": "OneNote requires section_id parameter"}
            return self.onenote.create_page(section_id, title, text)
        else:
            return {"error": f"Unsupported service: {service}"}
    
    def search_notes(self, query: str, service: str = 'notion') -> Dict[str, Any]:
        """Search notes in specified service."""
        if service.lower() == 'notion':
            return self.notion.search_pages(query)
        elif service.lower() == 'onenote':
            return self.onenote.search_pages(query)
        else:
            return {"error": f"Unsupported service: {service}"}


def parse_note_command(command: str) -> Dict[str, Any]:
    """
    Parse natural language note-taking command.
    
    Args:
        command: Natural language command
    
    Returns:
        Parsed command information
    """
    command_lower = command.lower().strip()
    
    # Determine service
    service = 'notion'  # default
    if 'onenote' in command_lower:
        service = 'onenote'
    
    # Extract action and content
    if 'save to' in command_lower:
        # Find the service name and extract text after it
        service_index = command_lower.find(service)
        if service_index != -1:
            text_start = service_index + len(service)
            text = command[text_start:].strip()
            
            return {
                "action": "save_note",
                "service": service,
                "text": text,
                "title": None  # Will be auto-generated
            }
    
    elif 'create note' in command_lower:
        # Extract text after "create note"
        note_index = command_lower.find('create note')
        if note_index != -1:
            text_start = note_index + len('create note')
            remaining = command[text_start:].strip()
            
            # Check if service is specified
            if service in remaining.lower():
                service_index = remaining.lower().find(service)
                text = remaining[service_index + len(service):].strip()
            else:
                text = remaining
            
            return {
                "action": "save_note",
                "service": service,
                "text": text,
                "title": None
            }
    
    elif 'search notes' in command_lower:
        # Extract search query
        search_index = command_lower.find('search notes')
        if search_index != -1:
            query_start = search_index + len('search notes')
            query = command[query_start:].strip()
            
            # Remove service name from query if present
            if service in query.lower():
                query = query.lower().replace(service, '').strip()
            
            return {
                "action": "search_notes",
                "service": service,
                "query": query
            }
    
    return {"error": f"Unsupported note command: {command}"}


def execute_note_command(command: str, notion_token: str = None, 
                        notion_db_id: str = None, onenote_token: str = None,
                        onenote_section_id: str = None) -> Dict[str, Any]:
    """
    Execute note-taking command based on natural language input.
    
    Args:
        command: Natural language command
        notion_token: Notion integration token
        notion_db_id: Notion database ID
        onenote_token: OneNote access token
        onenote_section_id: OneNote section ID
    
    Returns:
        Execution result
    """
    parsed = parse_note_command(command)
    
    if "error" in parsed:
        return parsed
    
    note_manager = NoteManager(notion_token, notion_db_id, onenote_token)
    
    if parsed["action"] == "save_note":
        kwargs = {}
        if parsed["service"] == "onenote" and onenote_section_id:
            kwargs["section_id"] = onenote_section_id
        
        return note_manager.save_note(
            parsed["text"], 
            parsed["service"], 
            parsed.get("title"),
            **kwargs
        )
    elif parsed["action"] == "search_notes":
        return note_manager.search_notes(parsed["query"], parsed["service"])
    else:
        return {"error": f"Unsupported action: {parsed['action']}"}


def get_note_services_status(notion_token: str = None, onenote_token: str = None) -> Dict[str, Any]:
    """Get status of note-taking services."""
    status = {
        "notion": {
            "configured": bool(notion_token or os.getenv('NOTION_TOKEN')),
            "database_configured": bool(os.getenv('NOTION_DATABASE_ID'))
        },
        "onenote": {
            "configured": bool(onenote_token or os.getenv('ONENOTE_TOKEN'))
        }
    }
    
    return status