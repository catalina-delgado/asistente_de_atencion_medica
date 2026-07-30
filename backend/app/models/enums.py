from enum import StrEnum


class RolMensaje(StrEnum):
    PACIENTE = "paciente"
    ASISTENTE = "asistente"


class Sexo(StrEnum):
    M = "M"
    F = "F"
    OTRO = "Otro"


class NivelTriage(StrEnum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"