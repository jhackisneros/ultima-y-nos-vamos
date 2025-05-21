import json
from pathlib import Path
from src.models.encuesta import Encuesta
from src.models.voto import Voto
from datetime import datetime

class EncuestaRepository:
    def __init__(self, path="data/encuestas.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save_all([])

    def save_all(self, encuestas):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([e.__dict__ for e in encuestas], f, default=str)

    def load_all(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all(self):
        data = self.load_all()
        encuestas = [self._dict_to_encuesta(d) for d in data]
        return encuestas

    def save(self, encuesta: Encuesta):
        encuestas = self.get_all()
        # Reemplaza o añade la encuesta
        encuestas = [e for e in encuestas if e.poll_id != encuesta.poll_id]
        encuestas.append(encuesta)
        self.save_all(encuestas)

    def _dict_to_encuesta(self, data: dict) -> Encuesta:
        votos = [Voto(**v) for v in data.get('votos', [])]
        timestamp_inicio = datetime.fromisoformat(data['timestamp_inicio'])
        return Encuesta(
            poll_id=data['poll_id'],
            pregunta=data['pregunta'],
            opciones=data['opciones'],
            votos=votos,
            estado=data['estado'],
            timestamp_inicio=timestamp_inicio,
            duracion=data['duracion'],
            tipo=data['tipo'],
        )

    def _encuesta_to_dict(self, encuesta: Encuesta) -> dict:
        return {
            'poll_id': encuesta.poll_id,
            'pregunta': encuesta.pregunta,
            'opciones': encuesta.opciones,
            'votos': [voto.__dict__ for voto in encuesta.votos],
            'estado': encuesta.estado,
            'timestamp_inicio': encuesta.timestamp_inicio.isoformat(),
            'duracion': encuesta.duracion,
            'tipo': encuesta.tipo,
        }
