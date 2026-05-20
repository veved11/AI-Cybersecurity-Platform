from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.user import User

from app.schemas.user_schema import (
    UserCreate,
    UserLogin
)

from app.security.hashing import (
    hash_password,
    verify_password
)

from app.security.jwt_handler import (
    create_access_token
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully"
    }


@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        return {
            "error": "Invalid email or password"
        }

    if not verify_password(
        user.password,
        existing_user.password
    ):
        return {
            "error": "Invalid email or password"
        }

    access_token = create_access_token(
        data={
            "sub": existing_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }