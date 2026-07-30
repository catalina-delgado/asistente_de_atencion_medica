from pydantic import BaseModel
from app.models.enums import RolMensaje


class Mensaje(BaseModel):
    rol: RolMensaje
    contenido: str