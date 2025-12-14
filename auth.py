from fastapi import Header, HTTPException, Depends
from typing import Optional

# Simulación de seguridad:
# En un futuro real, esto decodificaría un JWT o verificaría sesión en DB.
def get_current_user(x_token: Optional[str] = Header(None)):
    """
    Esta función actúa como candado.
    Si el usuario no envía el header 'x-token: secreto-super-seguro',
    la API lo rechaza.
    """
    if x_token != "secreto-super-seguro":
        raise HTTPException(status_code=401, detail="Token inválido o faltante. Acceso denegado.")
    return "UsuarioAdmin"