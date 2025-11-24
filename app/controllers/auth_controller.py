# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

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
    UpdateProfileRequest,
    ProfilePictureResponse,
)
from app.auth.jwt_handler import get_token_expiry, verify_token
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.models.account import Account
from app.dtos.user_dto import UserInfoResponse
from app.services.property_relation_service import check_user_property_relation
from app.settings import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
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
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
    )
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=AuthUser, summary="Get current authenticated user")
async def me(current_user: Account = Depends(get_current_user)):
    """
    Returns the currently authenticated user resolved via JWT cookie.
    """
    return AuthUser.model_validate(current_user)

@router.put("/profile", response_model=AuthUser, summary="Update user profile")
async def update_profile(
    update_data: UpdateProfileRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update authenticated user's profile information.
    
    **US04**: Users can update their personal data (name, phone, email, password)
    **US17**: Property owners can update their personal data (name, phone, email, password)
    
    Features:
    - Update full name, phone number, email, or password
    - All fields are optional - update only what you need
    - Changing email or password requires current password verification
    - Email uniqueness is validated
    - Password must be at least 8 characters
    
    Security:
    - Requires authentication via JWT cookie
    - Current password verification for sensitive changes (email/password)
    - Cannot use email that already exists for another user
    
    Available for: USER, PROPERTY_OWNER, and ADMIN roles.
    """
    auth_service = AuthService(db)
    updated_user = auth_service.update_profile(current_user, update_data)
    return AuthUser.model_validate(updated_user)

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


@router.get("/admin/users/{user_id}", response_model=UserInfoResponse, summary="Get user info by ID (Admin or owner)")
async def get_user_by_id(
    user_id: str,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a user's public information by ID.

    Access rules:
    - ADMIN users can retrieve any user's information.
    - PROPERTY_OWNER users can retrieve information ONLY of users who:
      - Are themselves (own user_id)
      - Have visits scheduled at their properties
      - Have made proposals for their properties
    - Regular USER role is forbidden.
    
    Security:
    - Property owners MUST have a validated relation with the user
    - Relation is checked via inter-service call to properties API
    - Fail-safe: denies access if properties API is unavailable
    """
    # Authorization: only admins or property owners
    if not (current_user.is_admin() or current_user.is_property_owner()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access user information"
        )

    auth_service = AuthService(db)

    # Admins can retrieve any user's information.
    if current_user.is_admin():
        try:
            account = auth_service.get_user_by_id(user_id)
            return UserInfoResponse.from_account(account)
        except HTTPException as e:
            # For admin, a 404 means the user truly doesn't exist, re-raise it.
            if e.status_code == status.HTTP_404_NOT_FOUND:
                raise e
            # Re-raise any other exceptions
            raise

    # For property owners, additional checks are needed
    if current_user.is_property_owner():
        # Allow access to own information
        if str(current_user.id) == user_id:
            try:
                account = auth_service.get_user_by_id(user_id)
                return UserInfoResponse.from_account(account)
            except HTTPException as e:
                # If owner queries self and not found, re-raise 404
                if e.status_code == status.HTTP_404_NOT_FOUND:
                    raise e
                raise

        # Validate relation with properties API
        logger.info(
            f"Property owner {current_user.id} requesting info for user {user_id} - "
            f"checking relation via properties API"
        )
        
        has_relation = await check_user_property_relation(
            user_id=user_id,
            owner_id=str(current_user.id)
        )
        
        if not has_relation:
            logger.warning(
                f"Property owner {current_user.id} denied access to user {user_id} - "
                f"no relation found"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access information of users who interacted with your properties"
            )
        
        logger.info(
            f"Property owner {current_user.id} granted access to user {user_id} - "
            f"relation validated"
        )

        # At this point, has_relation is True.
        # Now, try to get the user from the local DB.
        try:
            account = auth_service.get_user_by_id(user_id)
            return UserInfoResponse.from_account(account)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                logger.warning(
                    f"User {user_id} not found in local DB for Property Owner {current_user.id} "
                    f"despite valid property relation. Returning placeholder data."
                )
                # Construct placeholder data as per the prompt's example
                # and the discussion about data synchronization.
                return UserInfoResponse(
                    id=user_id,
                    username=f"external_user_{user_id[:8]}", # Placeholder username
                    fullName="External User", # Placeholder full name
                    email=f"external-{user_id[:8]}@example.com", # Placeholder email
                    phoneNumber="+5500900000000", # Placeholder phone number
                    role="USER", # Assume USER role for external users
                    createdAt=datetime.now(), # Current time for createdAt
                    isActive=True, # Assume active
                    hasProfilePicture=False # Assume no profile picture
                )
            # Re-raise any other exceptions
            raise
    
    # This part should ideally not be reached given the initial authorization check,
    # but included for defensive programming.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions to access user information"
    )


@router.post("/profile/picture", response_model=ProfilePictureResponse, summary="Upload or update profile picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload or update the authenticated user's profile picture.
    
    Features:
    - Accepts image files via multipart/form-data
    - Stores image as binary data in database
    - Maximum file size: 5MB
    - Supported formats: JPEG, JPG, PNG, GIF
    - Replaces existing profile picture if one exists
    
    Security:
    - Requires authentication via JWT cookie
    - Validates file size and MIME type
    - Only the authenticated user can upload their own picture
    
    Available for: USER, PROPERTY_OWNER, and ADMIN roles.
    """
    # Read file content
    image_data = await file.read()
    content_type = file.content_type or 'image/jpeg'
    
    auth_service = AuthService(db)
    auth_service.upload_profile_picture(current_user, image_data, content_type)
    
    return ProfilePictureResponse(
        message="Profile picture uploaded successfully",
        hasProfilePicture=True
    )


@router.get("/profile/picture/{user_id}", summary="Get user profile picture")
async def get_profile_picture(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a user's profile picture by user ID.
    
    Features:
    - Returns image as binary stream with appropriate content-type header
    - Public endpoint - no authentication required
    - Can be used directly in <img> tags
    
    Returns:
    - Image binary data with correct MIME type
    - 404 if user not found or has no profile picture
    
    Example usage in frontend:
    ```html
    <img src="http://localhost:8001/auth/profile/picture/{user_id}" alt="Profile" />
    ```
    """
    auth_service = AuthService(db)
    image_data, content_type = auth_service.get_profile_picture(user_id)
    
    return StreamingResponse(
        BytesIO(image_data),
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": f"inline; filename=profile_{user_id}.jpg"
        }
    )


@router.delete("/profile/picture", response_model=ProfilePictureResponse, summary="Delete profile picture")
async def delete_profile_picture(
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the authenticated user's profile picture.
    
    Features:
    - Removes profile picture from database
    - Safe to call even if no picture exists
    
    Security:
    - Requires authentication via JWT cookie
    - Only the authenticated user can delete their own picture
    
    Available for: USER, PROPERTY_OWNER, and ADMIN roles.
    """
    auth_service = AuthService(db)
    auth_service.delete_profile_picture(current_user)
    
    return ProfilePictureResponse(
        message="Profile picture deleted successfully",
        hasProfilePicture=False
    )

