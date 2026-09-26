from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Simple liveness check.
    Nginx and load balancers ping this to verify the app is alive.
    In Kubernetes, this becomes a livenessProbe.
    """
    return {"status": "ok", "service": "sysinfo-api"}
