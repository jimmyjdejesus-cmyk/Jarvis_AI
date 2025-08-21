"""FastAPI application providing a web UI for managing Jarvis plugins."""

from pathlib import Path
from typing import Dict, List
import subprocess
import json

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .auth import authenticate_user, get_current_user, require_role
from .moderation import approve_submission, list_pending, reject_submission, submit_plugin

# Simple in-memory plugin registry for demonstration purposes
_installed_plugins: Dict[str, Dict[str, object]] = {}

app = FastAPI(title="Jarvis Plugin Hub")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    token = authenticate_user(username, password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "plugins": _installed_plugins.values(), "user": user})


@app.get("/api/plugins", response_class=JSONResponse)
async def list_plugins(user=Depends(get_current_user)):
    return list(_installed_plugins.values())


@app.post("/api/plugins/install")
async def install_plugin(
    name: str = Form(...),
    version: str = Form("latest"),
    description: str = Form(""),
    author: str = Form(""),
    dependencies: str = Form(""),
    user=Depends(require_role("admin")),
):
    deps = [d.strip() for d in dependencies.split(",") if d.strip()]
    for dep in deps:
        if not _dependency_installed(dep):
            _pip_install(dep)
    _pip_install(f"{name}=={version}" if version != "latest" else name)
    _installed_plugins[name] = {
        "name": name,
        "version": version,
        "description": description,
        "author": author,
        "dependencies": deps,
    }
    return {"status": "installed", "plugin": _installed_plugins[name]}


@app.post("/api/plugins/uninstall")
async def uninstall_plugin(name: str = Form(...), user=Depends(require_role("admin"))):
    if name in _installed_plugins:
        _pip_uninstall(name)
        _installed_plugins.pop(name)
        return {"status": "uninstalled"}
    raise HTTPException(status_code=404, detail="Plugin not installed")


@app.post("/api/plugins/update")
async def update_plugin(name: str = Form(...), user=Depends(require_role("admin"))):
    if name not in _installed_plugins:
        raise HTTPException(status_code=404, detail="Plugin not installed")
    _pip_install(f"{name} --upgrade")
    return {"status": "updated"}


@app.get("/api/plugins/check_updates")
async def check_updates(user=Depends(require_role("admin"))):
    outdated = _pip_outdated()
    return {"outdated": [p for p in outdated if p["name"] in _installed_plugins]}


@app.post("/api/plugins/submit")
async def submit(
    name: str = Form(...),
    description: str = Form(""),
    author: str = Form(""),
    user=Depends(get_current_user),
):
    submission_id = submit_plugin({"name": name, "description": description, "author": author})
    return {"submission_id": submission_id}


@app.get("/api/moderation/pending")
async def moderation_queue(user=Depends(require_role("admin"))):
    return list_pending()


@app.post("/api/moderation/approve")
async def moderation_approve(
    submission_id: str = Form(...),
    user=Depends(require_role("admin")),
):
    plugin = approve_submission(submission_id)
    _installed_plugins[plugin["name"]] = plugin
    return {"status": "approved", "plugin": plugin}


@app.post("/api/moderation/reject")
async def moderation_reject(
    submission_id: str = Form(...),
    user=Depends(require_role("admin")),
):
    return reject_submission(submission_id)


# Utility functions

def _dependency_installed(package: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(package) is not None

    """
    Check if a package is installed via pip (i.e., present in the list of installed distributions).
    """
    try:
        # importlib.metadata returns a PackageNotFoundError if not installed via pip
        importlib.metadata.version(package)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False
    except Exception:
        # Fallback: not installed
        return False
def _pip_install(package: str):
    try:
        subprocess.run(["pip", "install"] + package.split(), check=True)
    except Exception as exc:
def _pip_install(package_args: List[str]):
    try:
        subprocess.run(["pip", "install"] + package_args, check=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to install {' '.join(package_args)}: {exc}")


def _pip_uninstall(package: str):
    try:
        subprocess.run(["pip", "uninstall", "-y", package], check=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to uninstall {package}: {exc}")


def _pip_outdated() -> List[Dict[str, str]]:
    try:
        result = subprocess.run(["pip", "list", "--outdated", "--format", "json"], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception:
        return []
