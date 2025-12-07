from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.db.database import get_async_session
from api.db.models import UserDB
from api.models.user import (
    UserCreate,
    UserResponse,
    Token,
    TokenData,
    LoginRequest,
    PasswordChange,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/python/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


async def get_user_by_username(session: AsyncSession, username: str) -> UserDB | None:
    """Get a user by username"""
    result = await session.execute(select(UserDB).where(UserDB.username == username))
    return result.scalar_one_or_none()


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> UserDB | None:
    """Authenticate a user"""
    user = await get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserDB:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    if token_data.username is None:
        raise credentials_exception

    user = await get_user_by_username(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserDB, Depends(get_current_user)],
) -> UserDB:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """OAuth2 compatible token login endpoint"""
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Login with username and password"""
    user = await authenticate_user(session, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
):
    """Get current user information"""
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Change user password"""
    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await session.commit()

    return {"message": "Password changed successfully"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Register a new user (public endpoint - only if no users exist)"""
    # Check if any users exist
    result = await session.execute(select(UserDB))
    existing_users = result.scalars().all()

    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User registration is disabled. Contact administrator.",
        )

    # Check if username already exists
    existing_user = await get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create new user (first user is always admin)
    new_user = UserDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role if not existing_users else user_data.role,
        is_active=True,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user
