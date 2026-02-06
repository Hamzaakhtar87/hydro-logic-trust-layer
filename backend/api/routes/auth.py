"""
Authentication API routes
Signup, login, API key management
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database import get_db, User
from backend.services.auth_service import AuthService
from backend.api.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============ Request/Response Models ============

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


class UserResponse(BaseModel):
    id: int
    email: str
    company_name: Optional[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyRequest(BaseModel):
    name: str = "Default Key"


class APIKeyResponse(BaseModel):
    id: int
    key_prefix: str
    name: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(BaseModel):
    id: int
    key: str  # Full key, only shown once
    key_prefix: str
    name: str
    message: str = "Store this key securely. It will not be shown again."


class RefreshRequest(BaseModel):
    refresh_token: str


# ============ Endpoints ============

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Returns access and refresh tokens on success.
    """
    try:
        user = AuthService.create_user(
            db=db,
            email=request.email,
            password=request.password,
            company_name=request.company_name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generate tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return tokens.
    """
    user = AuthService.authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    payload = AuthService.decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = AuthService.get_user_by_id(db, int(user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        company_name=user.company_name,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.post("/api-keys", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: APIKeyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for the authenticated user.
    The full key is only shown once - store it securely!
    """
    full_key, api_key = AuthService.create_api_key(db, user.id, request.name)
    
    return APIKeyCreatedResponse(
        id=api_key.id,
        key=full_key,
        key_prefix=api_key.key_prefix,
        name=api_key.name
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the authenticated user.
    """
    keys = AuthService.get_user_api_keys(db, user.id)
    return [APIKeyResponse.model_validate(k) for k in keys]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key.
    """
    success = AuthService.revoke_api_key(db, user.id, key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return None


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    """
    Logout user (client should discard tokens).
    In a production system, you might want to blacklist the token.
    """
    return {"message": "Logged out successfully. Please discard your tokens."}
