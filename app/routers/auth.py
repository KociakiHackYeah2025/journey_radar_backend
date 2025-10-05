from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from app.models.user import User
from app.utils import hash_password, verify_password
from app.utils.token import create_access_token
from jose import JWTError, jwt
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

class UserCreate(BaseModel):
    email: str
    password: str

# Rejestracja
@router.post("/register", tags=["Auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.email})
    return {
        "id": new_user.id,
        "email": new_user.email,
        "access_token": access_token,
        "token_type": "bearer"
    }

# Logowanie
@router.post("/login", tags=["Auth"])
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Bearer auth
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        exp_timestamp = payload.get("exp")
        if email is None or exp_timestamp is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Sprawdzenie wygaśnięcia tokenu
        if datetime.utcnow().timestamp() > exp_timestamp:
            raise HTTPException(status_code=401, detail="Token has expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Usuwanie zalogowanego użytkownika
@router.delete("/delete", status_code=204, tags=["Auth"])
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Sprawdzenie ważności tokenu / sesji
@router.get("/check_session", tags=["Auth"])
def check_session(current_user: User = Depends(get_current_user)):
    """
    Sprawdza ważność tokenu i zwraca informacje o zalogowanym użytkowniku.
    Jeśli token jest nieważny lub użytkownik nie istnieje, zwraca 401.
    """
    return {
        "email": current_user.email,
        "message": "Token is valid"
    }


# Informacje o koncie użytkownika
@router.get("/me", tags=["Auth"])
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "points": getattr(current_user, "points", None),
        "created_at": getattr(current_user, "created_at", None),
    }