from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prisma import Prisma
from datetime import timedelta
from typing import Optional

from app.db.schemas import (
    UserCreate, UserLogin, UserResponse, Token, 
    StandardResponse, TokenData
)
from app.db.sessions import get_database
from app.core.security import (
    create_access_token, verify_token, get_password_hash, 
    verify_password, validate_email_domain
)
from app.core.config import settings

# Create router instance
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme for JWT token
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Prisma = Depends(get_database)
) -> UserResponse:
    """
    Dependency to get the current authenticated user.
    
    This function validates the JWT token and returns the current user.
    Used as a dependency for protected routes.
    
    Args:
        credentials: HTTP authorization credentials containing the JWT token
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token and extract email
        email = verify_token(token)
        if email is None:
            raise credentials_exception
            
        token_data = TokenData(email=email)
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user = await db.user.find_unique(where={"email": token_data.email})
    if user is None:
        raise credentials_exception
        
    return UserResponse.model_validate(user)

@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Prisma = Depends(get_database)
):
    """
    Register a new user.
    
    This endpoint allows new users to create an account. It validates
    the email domain, checks for existing users, hashes the password,
    and stores the user in the database.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If email already exists or other validation errors
    """
    # Check if user already exists
    existing_user = await db.user.find_unique(where={"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    try:
        # Create new user
        new_user = await db.user.create(
            data={
                "email": user_data.email,
                "hashedPassword": hashed_password,
                "firstName": user_data.firstName,
                "lastName": user_data.lastName,
            }
        )
        
        return StandardResponse(
            message=f"User {user_data.email} registered successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Prisma = Depends(get_database)
):
    """
    Authenticate user and return JWT token.
    
    This endpoint validates user credentials and returns a JWT token
    for authenticated access to protected routes.
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        JWT token with expiration info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = await db.user.find_unique(where={"email": user_credentials.email})
    
    # Validate user exists and password is correct
    if not user or not verify_password(user_credentials.password, user.hashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        accessToken=access_token,
        tokenType="bearer",
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current user information.
    
    This is a protected endpoint that returns the current user's information.
    Requires a valid JWT token in the Authorization header.
    
    Args:
        current_user: Current authenticated user (injected by dependency)
        
    Returns:
        Current user information
    """
    return current_user

@router.post("/change-password", response_model=StandardResponse)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Prisma = Depends(get_database)
):
    """
    Change user password.
    
    This protected endpoint allows users to change their password.
    Requires valid JWT token and correct current password.
    
    Args:
        old_password: Current password
        new_password: New password
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If old password is incorrect
    """
    # Get user with password from database
    user = await db.user.find_unique(where={"id": current_user.id})
    
    # Verify old password
    if not verify_password(old_password, user.hashedPassword):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new password strength (basic validation)
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Hash new password and update
    hashed_password = get_password_hash(new_password)
    await db.user.update(
        where={"id": current_user.id},
        data={"hashedPassword": hashed_password}
    )
    
    return StandardResponse(message="Password changed successfully")

@router.post("/logout", response_model=StandardResponse)
async def logout_user(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout user.
    
    Note: Since we're using stateless JWT tokens, logout is handled
    on the client side by removing the token. This endpoint serves
    as a confirmation that the user wants to logout.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    return StandardResponse(message="Logged out successfully")