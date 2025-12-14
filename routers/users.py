from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import database
import schemas
import auth

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Endpoint PÚBLICO: Registro de usuario
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Verificar si ya existe
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    new_user = models.User(
        username=user.username, 
        email=user.email,
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Endpoint PRIVADO: Listar usuarios (Solo Admin)
@router.get("/", response_model=List[schemas.UserResponse])
def read_users(
    db: Session = Depends(database.get_db),
    admin: str = Depends(auth.get_current_user) # <--- CANDADO
):
    return db.query(models.User).all()