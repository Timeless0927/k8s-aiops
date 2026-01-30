from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.plugin_manager import plugin_manager
import shutil
import os
import tempfile
from pydantic import BaseModel

router = APIRouter()

class ToggleRequest(BaseModel):
    active: bool

@router.get("/")
def list_plugins():
    """
    List all installed plugins and their status.
    """
    return plugin_manager.list_plugins()

@router.post("/reload")
async def reload_plugins():
    """
    Force reload all plugins from disk.
    """
    await plugin_manager.reload_all()
    return {"status": "reloaded", "count": len(plugin_manager.plugins)}

@router.post("/upload")
async def upload_plugin(file: UploadFile = File(...)):
    """
    Upload a .zip file containing a plugin.
    The zip must contain a single root folder with __init__.py.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        plugin_id = await plugin_manager.install_plugin(tmp_path)
        return {"status": "success", "plugin_id": plugin_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.delete("/{plugin_id}")
async def delete_plugin(plugin_id: str):
    """
    Delete a user-installed plugin.
    """
    try:
        # Use new async method
        if await plugin_manager.delete_plugin_async(plugin_id):
            return {"status": "deleted", "plugin_id": plugin_id}
        else:
            raise HTTPException(status_code=404, detail="Plugin not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/{plugin_id}/toggle")
async def toggle_plugin(plugin_id: str, request: ToggleRequest):
    """
    Enable or disable a plugin.
    """
    try:
        await plugin_manager.toggle_plugin(plugin_id, request.active)
        return {"status": "updated", "plugin_id": plugin_id, "active": request.active}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
