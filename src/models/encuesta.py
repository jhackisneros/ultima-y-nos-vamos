# src/models/encuesta.py

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class Encuesta:
    def __init__(self, pregunta, opciones, duracion, tipo):
        self.id = str(uuid.uuid4())
        self.pregunta = pregunta
        self.opciones = opciones
        self.votos = []
        self.active = True
        self.timestamp_inicio = datetime.now()
        self.duracion = duracion
        self.tipo = tipo  # 'simple' o 'multiple'


class Poll:
    """
    Representa una encuesta en el sistema.

    Atributos:
        poll_id (str): Identificador único de la encuesta (UUID).
        pregunta (str): Texto de la pregunta.
        opciones (List[str]): Lista de opciones disponibles para votar.
        votos (Dict[str, int]): Conteo de votos por opción.
        estado (str): 'activa' o 'cerrada'.
        timestamp_inicio (datetime): Momento en que se creó la encuesta.
        duracion (int): Duración de la encuesta en segundos.
        tipo (str): Tipo de encuesta ('simple', 'multiple', etc.).
        votos_emitidos (Dict[str, List[str]]): Usuarios que han votado y sus opciones.
    """

    def __init__(
        self,
        pregunta: str,
        opciones: List[str],
        duracion_segundos: int,
        tipo: str = "simple"
    ):
        self.poll_id: str = str(uuid.uuid4())
        self.pregunta: str = pregunta
        self.opciones: List[str] = opciones
        self.votos: Dict[str, int] = {opcion: 0 for opcion in opciones}
        self.estado: str = "activa"
        self.timestamp_inicio: datetime = datetime.now()
        self.duracion: int = duracion_segundos
        self.tipo: str = tipo
        self.votos_emitidos: Dict[str, List[str]] = {}

    def esta_activa(self) -> bool:
        """
        Verifica si la encuesta sigue activa en función del tiempo.
        """
        if self.estado == "cerrada":
            return False
        ahora = datetime.now()
        if ahora >= self.timestamp_inicio + timedelta(seconds=self.duracion):
            self.estado = "cerrada"
            return False
        return True

    def votar(self, username: str, opciones_votadas: List[str]) -> bool:
        """
        Registra un voto si el usuario no ha votado aún.
        """
        if not self.esta_activa():
            return False
        if username in self.votos_emitidos:
            return False
        for opcion in opciones_votadas:
            if opcion in self.votos:
                self.votos[opcion] += 1
        self.votos_emitidos[username] = opciones_votadas
        return True

    def cerrar(self):
        """
        Cierra la encuesta manualmente.
        """
        self.estado = "cerrada"

    def resultados(self) -> Dict[str, float]:
        """
        Devuelve los resultados actuales o finales en porcentajes.
        """
        total_votos = sum(self.votos.values())
        if total_votos == 0:
            return {opcion: 0.0 for opcion in self.opciones}
        return {
            opcion: (self.votos[opcion] / total_votos) * 100
            for opcion in self.opciones
        }

    def hay_empate(self) -> bool:
        """
        Detecta si hay empate en los resultados.
        """
        if self.estado != "cerrada":
            return False
        max_votos = max(self.votos.values(), default=0)
        opciones_maximas = [op for op, v in self.votos.items() if v == max_votos]
        return len(opciones_maximas) > 1
