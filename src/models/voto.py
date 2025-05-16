# src/models/voto.py

from datetime import datetime
from typing import List


class Vote:
    """
    Representa un voto emitido por un usuario.

    Atributos:
        username (str): Usuario que emitió el voto.
        poll_id (str): ID de la encuesta.
        opciones (List[str]): Opción(es) seleccionadas.
        timestamp (datetime): Momento en que se emitió el voto.
    """

    def __init__(self, username: str, poll_id: str, opciones: List[str]):
        self.username = username
        self.poll_id = poll_id
        self.opciones = opciones
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "poll_id": self.poll_id,
            "opciones": self.opciones,
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: dict) -> "Vote":
        from datetime import datetime
        return Vote(
            username=data["username"],
            poll_id=data["poll_id"],
            opciones=data["opciones"]
        )
