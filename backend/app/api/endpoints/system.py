from fastapi import APIRouter
from app.services.k8s_client import k8s_client

router = APIRouter()

@router.get("/status")
async def get_system_status():
    """
    Get current system status, including Kubernetes connection.
    """
    k8s_status = k8s_client.check_connection()
    return {
        "kubernetes": k8s_status
    }
