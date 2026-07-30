from pydantic import BaseModel
from models.enums import RolMensaje


class Mensaje(BaseModel):
    rol: RolMensaje
    contenido: str