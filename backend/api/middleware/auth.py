"""
Authentication middleware and dependencies
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session

from backend.database import get_db, User, APIKey
from backend.services.auth_service import AuthService

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract user from JWT bearer token."""
    if not credentials:
        return None
    
    payload = AuthService.decode_token(credentials.credentials)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = AuthService.get_user_by_id(db, int(user_id))
    return user


async def get_current_user_from_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[tuple[User, APIKey]]:
    """Extract user from API key header."""
    if not api_key:
        return None
    
    result = AuthService.validate_api_key(db, api_key)
    return result


async def get_current_user(
    token_user: Optional[User] = Depends(get_current_user_from_token),
    api_key_result: Optional[tuple] = Depends(get_current_user_from_api_key),
) -> User:
    """
    Get current authenticated user from either JWT token or API key.
    Raises 401 if not authenticated.
    """
    # Try JWT token first
    if token_user:
        return token_user
    
    # Try API key
    if api_key_result:
        return api_key_result[0]
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide a valid JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_optional(
    token_user: Optional[User] = Depends(get_current_user_from_token),
    api_key_result: Optional[tuple] = Depends(get_current_user_from_api_key),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Does not raise 401 - useful for optional auth endpoints.
    """
    if token_user:
        return token_user
    if api_key_result:
        return api_key_result[0]
    return None


async def require_verified_user(
    user: User = Depends(get_current_user)
) -> User:
    """Require a verified user (email verified)."""
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    return user
