from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from backend.database import get_db, UserModel
from backend.models import UserCreate, UserLogin
from backend.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = UserModel(
        id=str(uuid.uuid4()),
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": db_user.username, "user_id": db_user.id})
    refresh_token = create_refresh_token(data={"sub": db_user.username, "user_id": db_user.id})
    
    # Set HttpOnly Cookie for Refresh Token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,     # Must be True for SameSite=None
        samesite="none", # Required for cross-domain requests (Render <-> Cloudflare)
        max_age=7 * 24 * 60 * 60 # 7 days
    )
    
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}

@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    try:
        # Verify the refresh token
        payload = verify_token(refresh_token, HTTPException(status_code=401, detail="Invalid refresh token"))
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        # Verify user still exists
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists")
        
        # Issue new access token
        new_access_token = create_access_token(data={"sub": username, "user_id": user_id})
        return {"access_token": new_access_token, "token_type": "bearer", "username": username}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        secure=True,
        samesite="none"
    )
    return {"message": "Logged out successfully"}
