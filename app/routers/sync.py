from fastapi import APIRouter
from app.database import synchronization

router = APIRouter(prefix="/sync", tags=["Sync"])

@router.post("/run", tags=["Sync"])
def run_synchronization():
    """
    Endpoint do ręcznego wywołania synchronizacji.
    """
    synchronization()
    return {"message": "Synchronizacja wywołana"}
