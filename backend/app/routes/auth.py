from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..dependencies import get_current_user, require_admin
from ..schemas import AuthenticatedUser, LoginRequest, LoginResponse, Token, User
from ..security import create_access_token, verify_password
from ..users import USER_DB

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_user(username: str, password: str, require_admin: bool = False) -> AuthenticatedUser:
    record = USER_DB.get(username)
    if not record or not verify_password(password, record["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if require_admin and not record["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return AuthenticatedUser(username=record["username"], is_admin=record["is_admin"], scopes=record["scopes"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest) -> LoginResponse:
    user = authenticate_user(credentials.username, credentials.password)
    token = Token(access_token=create_access_token(user.username, user.scopes), scope=" ".join(user.scopes))
    return LoginResponse(token=token, user=user)


@router.post("/token", response_model=Token, include_in_schema=False)
async def token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    return Token(access_token=create_access_token(user.username, user.scopes), scope=" ".join(user.scopes))


@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(credentials: LoginRequest) -> LoginResponse:
    user = authenticate_user(credentials.username, credentials.password, require_admin=True)
    token = Token(access_token=create_access_token(user.username, user.scopes), scope=" ".join(user.scopes))
    return LoginResponse(token=token, user=user)


@router.get("/me", response_model=User)
async def profile(user: AuthenticatedUser = Depends(get_current_user)) -> User:
    return User(username=user.username, is_admin=user.is_admin)


@router.get("/admin/health", response_model=User)
async def admin_health(user: AuthenticatedUser = Depends(require_admin)) -> User:
    return User(username=user.username, is_admin=user.is_admin)
