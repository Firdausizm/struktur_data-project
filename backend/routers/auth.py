"""
Router untuk autentikasi: registrasi, login, dan info user.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from backend.services import auth_service

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency untuk FastAPI: decode JWT token dari header Authorization
    dan kembalikan data user yang sedang login.
    """
    payload = auth_service.decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=401, detail="Token tidak valid atau sudah kadaluarsa"
        )

    user_id = int(payload["sub"])
    user = auth_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User tidak ditemukan")

    return user


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegisterRequest):
    """Registrasi user baru."""
    try:
        user = auth_service.register_user(data.username, data.email, data.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLoginRequest):
    """Login dan dapatkan JWT access token."""
    user = auth_service.authenticate_user(data.email, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Email atau password salah")

    token = auth_service.create_access_token(user["id"], user["username"])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Ambil info user yang sedang login berdasarkan JWT token."""
    return current_user
