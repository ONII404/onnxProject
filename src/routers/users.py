# src/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.models import users as modelsUsers
from src.schemas import users as schemasUsers
from src.config import db as database
from src.config import auth


users = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ==========================================
#  PÚBLICO - Registro y perfil personal
# ==========================================

@users.post(
    "/",
    response_model=schemasUsers.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario"
)
def create_user(
    user_data: schemasUsers.UserCreate,
    db: Session = Depends(database.get_db)
):
    """Registro público de nuevos usuarios"""
    # Verificar si el email o username ya existe
    if db.query(modelsUsers.User).filter(modelsUsers.User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    if db.query(modelsUsers.User).filter(modelsUsers.User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso"
        )

    # Crear usuario (sin password por ahora - ver nota abajo)
    new_user = modelsUsers.User(
        username=user_data.username,
        email=user_data.email,
        is_admin=False  # Los nuevos usuarios nunca son admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@users.get("/me", response_model=schemasUsers.UserResponse, summary="Ver mi perfil")
def read_current_user(
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Devuelve la información del usuario autenticado.
    Como ahora auth devuelve un dict simple, simulamos el objeto completo.
    """
    # En el futuro, cuando uses JWT real, aquí devolverás directamente el models.User
    return {
        "id": 1,  # Placeholder - en producción será current_user.id
        "username": current_user["username"],
        "email": "user@example.com",  # Placeholder
        "is_admin": current_user.get("is_admin", False),
        "created_at": "2025-01-01T00:00:00"  # Placeholder
    }


# ==========================================
#  PRIVADO - Solo usuario autenticado
# ==========================================

@users.patch("/me", response_model=schemasUsers.UserResponse, summary="Actualizar mi perfil")
def update_current_user(
    update_data: schemasUsers.UserUpdate,
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Permite al usuario actualizar su propio username o email"""
    # Buscar al usuario real (en futuro usarás el ID del JWT)
    # Por ahora usamos un placeholder - cuando implementes login real, cambia esto
    db_user = db.query(modelsUsers.User).filter(modelsUsers.User.username == current_user["username"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key in ["username", "email"]:
            # Validar unicidad
            if key == "email" and db.query(modelsUsers.User).filter(modelsUsers.User.email == value, modelsUsers.User.id != db_user.id).first():
                raise HTTPException(status_code=400, detail="El email ya está en uso")
            if key == "username" and db.query(modelsUsers.User).filter(modelsUsers.User.username == value, modelsUsers.User.id != db_user.id).first():
                raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@users.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar mi cuenta")
def delete_current_user(
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """El usuario puede eliminar su propia cuenta"""
    db_user = db.query(modelsUsers.User).filter(modelsUsers.User.username == current_user["username"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_user)
    db.commit()
    return None


# ==========================================
#  ADMIN - Solo administradores
# ==========================================

@users.get("/", response_model=List[schemasUsers.UserResponse], summary="Listar todos los usuarios (Admin)")
def read_all_users(
    db: Session = Depends(database.get_db),
    admin_user: dict = Depends(auth.get_current_admin_user)
):
    """Solo admins pueden ver la lista completa de usuarios"""
    return db.query(modelsUsers.User).all()


@users.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario (Admin)")
def delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    admin_user: dict = Depends(auth.get_current_admin_user)
):
    """Admin puede eliminar cualquier cuenta"""
    db_user = db.query(modelsUsers.User).filter(modelsUsers.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_user)
    db.commit()
    return None