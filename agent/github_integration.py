"""
GitHub API Integration Module
Provides integration with GitHub API for repository management,
PR creation, issue management, and branch operations.
"""
import os
import requests
import json
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime


class GitHubIntegration:
    def __init__(self, token: str = None, repository: str = None):
        """
        Initialize GitHub integration.
        
        Args:
            token: GitHub personal access token
            repository: Repository in format 'owner/repo'
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repository = repository
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}' if self.token else '',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to GitHub API."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
            
            if response.status_code < 300:
                return response.json() if response.content else {"status": "success"}
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_repository_info(self, repo: str = None) -> Dict[str, Any]:
        """Get repository information."""
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        return self._make_request('GET', f'repos/{repo}')
    
    def list_issues(self, repo: str = None, state: str = 'open', 
                   labels: List[str] = None, assignee: str = None) -> List[Dict[str, Any]]:
        """
        List issues in repository.
        
        Args:
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            labels: List of label names
            assignee: Assignee username
        
        Returns:
            List of issues
        """
        repo = repo or self.repository
        if not repo:
            return [{"error": "No repository specified"}]
        
        params = []
        if state != 'open':
            params.append(f'state={state}')
        if labels:
            params.append(f'labels={",".join(labels)}')
        if assignee:
            params.append(f'assignee={assignee}')
        
        query_string = '?' + '&'.join(params) if params else ''
        endpoint = f'repos/{repo}/issues{query_string}'
        
        result = self._make_request('GET', endpoint)
        return result if isinstance(result, list) else [result]
    
    def create_issue(self, title: str, body: str = '', labels: List[str] = None,
                    assignees: List[str] = None, repo: str = None) -> Dict[str, Any]:
        """
        Create a new issue.
        
        Args:
            title: Issue title
            body: Issue description
            labels: List of label names
            assignees: List of assignee usernames
            repo: Repository name
        
        Returns:
            Created issue information
        """
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        
        return self._make_request('POST', f'repos/{repo}/issues', data)
    
    def update_issue(self, issue_number: int, title: str = None, body: str = None,
                    state: str = None, labels: List[str] = None,
                    assignees: List[str] = None, repo: str = None) -> Dict[str, Any]:
        """Update an existing issue."""
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        data = {}
        if title is not None:
            data["title"] = title
        if body is not None:
            data["body"] = body
        if state is not None:
            data["state"] = state
        if labels is not None:
            data["labels"] = labels
        if assignees is not None:
            data["assignees"] = assignees
        
        return self._make_request('PATCH', f'repos/{repo}/issues/{issue_number}', data)
    
    def list_pull_requests(self, repo: str = None, state: str = 'open',
                          base: str = None, head: str = None) -> List[Dict[str, Any]]:
        """List pull requests in repository."""
        repo = repo or self.repository
        if not repo:
            return [{"error": "No repository specified"}]
        
        params = []
        if state != 'open':
            params.append(f'state={state}')
        if base:
            params.append(f'base={base}')
        if head:
            params.append(f'head={head}')
        
        query_string = '?' + '&'.join(params) if params else ''
        endpoint = f'repos/{repo}/pulls{query_string}'
        
        result = self._make_request('GET', endpoint)
        return result if isinstance(result, list) else [result]
    
    def create_pull_request(self, title: str, head: str, base: str = 'main',
                           body: str = '', draft: bool = False,
                           repo: str = None) -> Dict[str, Any]:
        """
        Create a new pull request.
        
        Args:
            title: PR title
            head: Head branch name
            base: Base branch name (default: 'main')
            body: PR description
            draft: Whether to create as draft PR
            repo: Repository name
        
        Returns:
            Created PR information
        """
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
        
        return self._make_request('POST', f'repos/{repo}/pulls', data)
    
    def update_pull_request(self, pr_number: int, title: str = None,
                           body: str = None, state: str = None,
                           base: str = None, repo: str = None) -> Dict[str, Any]:
        """Update an existing pull request."""
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        data = {}
        if title is not None:
            data["title"] = title
        if body is not None:
            data["body"] = body
        if state is not None:
            data["state"] = state
        if base is not None:
            data["base"] = base
        
        return self._make_request('PATCH', f'repos/{repo}/pulls/{pr_number}', data)
    
    def list_branches(self, repo: str = None) -> List[Dict[str, Any]]:
        """List repository branches."""
        repo = repo or self.repository
        if not repo:
            return [{"error": "No repository specified"}]
        
        result = self._make_request('GET', f'repos/{repo}/branches')
        return result if isinstance(result, list) else [result]
    
    def create_branch(self, branch_name: str, from_branch: str = 'main',
                     repo: str = None) -> Dict[str, Any]:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of new branch
            from_branch: Source branch to create from
            repo: Repository name
        
        Returns:
            Branch creation result
        """
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        # First get the SHA of the source branch
        source_ref = self._make_request('GET', f'repos/{repo}/git/refs/heads/{from_branch}')
        if "error" in source_ref:
            return source_ref
        
        sha = source_ref.get('object', {}).get('sha')
        if not sha:
            return {"error": f"Could not get SHA for branch {from_branch}"}
        
        # Create new branch reference
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha
        }
        
        return self._make_request('POST', f'repos/{repo}/git/refs', data)
    
    def delete_branch(self, branch_name: str, repo: str = None) -> Dict[str, Any]:
        """Delete a branch."""
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        return self._make_request('DELETE', f'repos/{repo}/git/refs/heads/{branch_name}')
    
    def get_file_content(self, file_path: str, branch: str = None,
                        repo: str = None) -> Dict[str, Any]:
        """Get file content from repository."""
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        endpoint = f'repos/{repo}/contents/{file_path}'
        if branch:
            endpoint += f'?ref={branch}'
        
        return self._make_request('GET', endpoint)
    
    def update_file(self, file_path: str, content: str, message: str,
                   branch: str = None, repo: str = None) -> Dict[str, Any]:
        """
        Update file content in repository.
        
        Args:
            file_path: Path to file
            content: New file content (base64 encoded)
            message: Commit message
            branch: Target branch
            repo: Repository name
        
        Returns:
            Update result
        """
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        # Get current file to get SHA
        current_file = self.get_file_content(file_path, branch, repo)
        if "error" in current_file:
            # File doesn't exist, create new
            sha = None
        else:
            sha = current_file.get('sha')
        
        import base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message,
            "content": encoded_content
        }
        
        if sha:
            data["sha"] = sha
        if branch:
            data["branch"] = branch
        
        return self._make_request('PUT', f'repos/{repo}/contents/{file_path}', data)
    
    def create_webhook(self, url: str, events: List[str] = None,
                      secret: str = None, repo: str = None) -> Dict[str, Any]:
        """Create a webhook for repository."""
        repo = repo or self.repository
        if not repo:
            return {"error": "No repository specified"}
        
        events = events or ['push', 'pull_request']
        
        data = {
            "name": "web",
            "active": True,
            "events": events,
            "config": {
                "url": url,
                "content_type": "json"
            }
        }
        
        if secret:
            data["config"]["secret"] = secret
        
        return self._make_request('POST', f'repos/{repo}/hooks', data)
    
    def search_repositories(self, query: str, sort: str = 'stars',
                           order: str = 'desc') -> List[Dict[str, Any]]:
        """Search for repositories."""
        params = f'q={query}&sort={sort}&order={order}'
        endpoint = f'search/repositories?{params}'
        
        result = self._make_request('GET', endpoint)
        return result.get('items', []) if 'items' in result else [result]
    
    def get_user_info(self, username: str = None) -> Dict[str, Any]:
        """Get user information."""
        if username:
            endpoint = f'users/{username}'
        else:
            endpoint = 'user'  # Current authenticated user
        
        return self._make_request('GET', endpoint)


class GitOperations:
    """Git operations wrapper for local repository management."""
    
    def __init__(self, repository_path: str = None):
        self.repository_path = repository_path or os.getcwd()
    
    def run_git_command(self, command: List[str]) -> Dict[str, Any]:
        """Run git command and return result."""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Git command timed out"}
        except Exception as e:
            return {"error": f"Git command failed: {str(e)}"}
    
    def git_status(self) -> Dict[str, Any]:
        """Get git status."""
        return self.run_git_command(['status', '--porcelain'])
    
    def git_diff(self, file_path: str = None) -> Dict[str, Any]:
        """Get git diff."""
        cmd = ['diff']
        if file_path:
            cmd.append(file_path)
        return self.run_git_command(cmd)
    
    def git_commit(self, message: str, files: List[str] = None) -> Dict[str, Any]:
        """Create git commit."""
        # Stage files if specified
        if files:
            for file in files:
                stage_result = self.run_git_command(['add', file])
                if not stage_result.get('success', False):
                    return {"error": f"Failed to stage file {file}: {stage_result.get('stderr', '')}"}
        
        # Commit
        return self.run_git_command(['commit', '-m', message])
    
    def git_push(self, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """Push changes to remote."""
        cmd = ['push', remote]
        if branch:
            cmd.append(branch)
        return self.run_git_command(cmd)
    
    def git_pull(self, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """Pull changes from remote."""
        cmd = ['pull', remote]
        if branch:
            cmd.append(branch)
        return self.run_git_command(cmd)
    
    def git_checkout(self, branch: str, create: bool = False) -> Dict[str, Any]:
        """Checkout branch."""
        cmd = ['checkout']
        if create:
            cmd.append('-b')
        cmd.append(branch)
        return self.run_git_command(cmd)
    
    def git_branch(self, branch_name: str = None, delete: bool = False) -> Dict[str, Any]:
        """Manage branches."""
        if delete and branch_name:
            return self.run_git_command(['branch', '-d', branch_name])
        elif branch_name:
            return self.run_git_command(['branch', branch_name])
        else:
            return self.run_git_command(['branch'])


def execute_git_command(command: str, repository_path: str = None) -> Dict[str, Any]:
    """
    Execute git command based on natural language input.
    
    Args:
        command: Natural language git command
        repository_path: Path to git repository
    
    Returns:
        Command execution result
    """
    git_ops = GitOperations(repository_path)
    command_lower = command.lower().strip()
    
    if command_lower == 'git status':
        return git_ops.git_status()
    elif command_lower.startswith('git commit'):
        # Extract commit message
        if ' ' in command_lower:
            message = command[command.find(' ') + 1:].strip()
            if message.startswith('commit '):
                message = message[7:].strip()
            return git_ops.git_commit(message)
        else:
            return {"error": "Commit message required"}
    elif command_lower == 'git diff':
        return git_ops.git_diff()
    elif command_lower.startswith('git diff '):
        file_path = command[9:].strip()
        return git_ops.git_diff(file_path)
    elif command_lower == 'git push':
        return git_ops.git_push()
    elif command_lower == 'git pull':
        return git_ops.git_pull()
    elif command_lower.startswith('git checkout '):
        branch = command[13:].strip()
        return git_ops.git_checkout(branch)
    elif command_lower == 'git branch':
        return git_ops.git_branch()
    else:
        return {"error": f"Unsupported git command: {command}"}


def github_integration_handler(action: str, **kwargs) -> Dict[str, Any]:
    """
    Handle GitHub integration actions.
    
    Args:
        action: Action to perform
        **kwargs: Action-specific parameters
    
    Returns:
        Action result
    """
    github = GitHubIntegration(
        token=kwargs.get('token'),
        repository=kwargs.get('repository')
    )
    
    if action == 'list_issues':
        return {"issues": github.list_issues(**kwargs)}
    elif action == 'create_issue':
        return github.create_issue(**kwargs)
    elif action == 'list_prs':
        return {"pull_requests": github.list_pull_requests(**kwargs)}
    elif action == 'create_pr':
        return github.create_pull_request(**kwargs)
    elif action == 'list_branches':
        return {"branches": github.list_branches(**kwargs)}
    elif action == 'create_branch':
        return github.create_branch(**kwargs)
    elif action == 'repo_info':
        return github.get_repository_info(**kwargs)
    else:
        return {"error": f"Unsupported GitHub action: {action}"}