from fastapi import Header, HTTPException, status, Depends
from typing import Optional


def get_current_user(x_token: Optional[str] = Header(None)):
    """
    Candado simple para desarrollo.
    Solo permite acceso si el header es: x-token: secreto-super-seguro
    """
    if x_token != "secreto-super-seguro":
        raise HTTPException(status_code=401, detail="Token inválido o faltante.")

    # Devuelve un dict simulando un usuario admin (para desarrollo)
    return {"username": "admin_dev", "is_admin": True}


def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: solo administradores",
        )
    return current_user
