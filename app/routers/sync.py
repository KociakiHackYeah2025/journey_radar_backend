from fastapi import APIRouter
from app.database import synchronization

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/run")
def run_synchronization():
    """
    Endpoint do ręcznego wywołania synchronizacji.
    """
    synchronization()
    return {"message": "Synchronizacja wywołana"}
