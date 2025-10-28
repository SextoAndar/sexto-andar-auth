# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.dtos.auth_dto import (
    LoginRequest,
    LoginResponse,
    RegisterUserRequest,
    RegisterPropertyOwnerRequest,
    RegisterAdminRequest,
    AuthUser,
    IntrospectRequest,
    IntrospectResponse,
)
from app.auth.jwt_handler import get_token_expiry, verify_token
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.models.account import Account

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse, summary="User Login")
async def login(
    response: Response,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user credentials and establish secure session.
    
    - Validates username and password against database
    - Generates JWT token with 30-minute expiry
    - Sets secure HTTP-only cookie
    - Returns user profile and access token
    
    Supports USER, PROPERTY_OWNER, and ADMIN roles.
    """
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create JWT token
    access_token = auth_service.create_user_token(user)
    
    # Set HTTP-only cookie with JWT token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevent XSS attacks
        secure=False,   # Set to True in production with HTTPS
        samesite="lax", # CSRF protection
        max_age=int(get_token_expiry().total_seconds())
    )
    
    # Return response
    user_data = AuthUser.model_validate(user)
    return LoginResponse(
        access_token=access_token,
        user=user_data.model_dump()
    )

@router.post("/register/user", response_model=AuthUser, status_code=status.HTTP_201_CREATED, summary="Register User")
async def register_user(
    register_data: RegisterUserRequest,
    db: Session = Depends(get_db)
):
    """
    Create new USER account with basic permissions.
    
    - Browse properties and schedule visits
    - Make purchase/rental proposals
    - Manage personal profile
    
    Requires unique username and email.
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(register_data)
    return AuthUser.model_validate(user)

@router.post("/register/property-owner", response_model=AuthUser, status_code=status.HTTP_201_CREATED, summary="Register Property Owner")
async def register_property_owner(
    register_data: RegisterPropertyOwnerRequest,
    db: Session = Depends(get_db)
):
    """
    Create new PROPERTY_OWNER account with property management permissions.
    
    - List and manage property portfolio
    - Handle visit requests and proposals
    - Access advanced dashboard and analytics
    
    Requires unique username and email.
    """
    auth_service = AuthService(db)
    owner = auth_service.register_property_owner(register_data)
    return AuthUser.model_validate(owner)

@router.post("/admin/create-admin", response_model=AuthUser, status_code=status.HTTP_201_CREATED, summary="Create Admin User (Admin Only)")
async def create_admin(
    register_data: RegisterAdminRequest,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new ADMIN account. **Requires existing admin authentication.**
    
    Security features:
    - Requires valid admin JWT token
    - Only users with ADMIN role can access
    - Logs action for audit trail
    - Validates unique username/email
    - Recommended: Add rate limiting in production
    
    The creator admin information is logged for security auditing.
    """
    auth_service = AuthService(db)
    new_admin = auth_service.register_admin(register_data, current_admin)
    return AuthUser.model_validate(new_admin)

@router.delete("/admin/delete-admin/{admin_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Admin User (Admin Only)")
async def delete_admin(
    admin_id: str,
    current_admin: Account = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete an ADMIN account. **Requires existing admin authentication.**
    
    Security features:
    - Requires valid admin JWT token
    - Only users with ADMIN role can access
    - Cannot delete yourself (prevents lockout)
    - Cannot delete the last admin in the system
    - Logs action for audit trail
    - Validates target is actually an admin
    
    Returns 204 No Content on success.
    """
    auth_service = AuthService(db)
    auth_service.delete_admin(admin_id, current_admin)
    return None

@router.post("/logout", summary="User Logout")
async def logout(response: Response):
    """
    Terminate user session by clearing authentication cookie.
    
    - Removes access token from browser
    - Invalidates client-side session
    - Safe to call multiple times
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=AuthUser, summary="Get current authenticated user")
async def me(current_user: Account = Depends(get_current_user)):
    """
    Returns the currently authenticated user resolved via JWT cookie.
    """
    return AuthUser.model_validate(current_user)

@router.post("/introspect", response_model=IntrospectResponse, summary="Validate and decode a JWT token")
async def introspect(body: IntrospectRequest) -> IntrospectResponse:
    """
    Validates a JWT token and returns whether it's active plus claims when valid.
    Intended for service-to-service checks.
    """
    payload = verify_token(body.token)
    if not payload:
        return IntrospectResponse(active=False, reason="invalid_or_expired")
    return IntrospectResponse(active=True, claims=payload)
