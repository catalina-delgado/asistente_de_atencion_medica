# Informacion demografica del paciente

from app.models.enums import Sexo
from pydantic import BaseModel, Field


class Paciente(BaseModel):
    edad: int | None = Field(default=None, ge=0, le=120)
    sexo: Sexo | None = None
    nombre: str | None = Field(default=None, max_length=200)
