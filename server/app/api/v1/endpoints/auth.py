from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_userprofile_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.userprofile import User
from app.schemas.auth import AuthUser, Token, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_to_auth(user: User) -> AuthUser:
    parts = user.full_name.split(" ", 1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""
    return AuthUser(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        first_name=first,
        last_name=last,
        avatar_url=user.avatar_url,
        locale=user.locale,
        is_admin=user.is_admin,
    )


@router.post(
    "/register",
    response_model=AuthUser,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (userprofile database)",
)
def register(user_in: UserRegister, db: Session = Depends(get_userprofile_db)):
    full_name = f"{user_in.first_name.strip()} {user_in.last_name.strip()}".strip()
    user = User(
        email=user_in.email.lower(),
        password_hash=hash_password(user_in.password),
        full_name=full_name,
        locale=user_in.locale,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        ) from exc
    db.refresh(user)
    return _user_to_auth(user)


@router.post("/login", response_model=Token, summary="Login and receive JWT access token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_userprofile_db),
):
    email = form_data.username.lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=str(user.id), email=user.email)
    return Token(access_token=access_token)


@router.get("/me", response_model=AuthUser, summary="Current authenticated user")
def read_me(current_user: User = Depends(get_current_user)):
    return _user_to_auth(current_user)
