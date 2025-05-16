import json
import os
from src.models.encuesta import Encuesta
from src.models.voto import Voto
from datetime import datetime

class EncuestaRepository:
    def __init__(self, filepath='data/encuestas.json'):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def get_all(self):
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        encuestas = [self._dict_to_encuesta(d) for d in data]
        return encuestas

    def save(self, encuesta: Encuesta):
        encuestas = self.get_all()
        # Reemplaza o añade la encuesta
        encuestas = [e for e in encuestas if e.poll_id != encuesta.poll_id]
        encuestas.append(encuesta)
        with open(self.filepath, 'w') as f:
            json.dump([self._encuesta_to_dict(e) for e in encuestas], f, indent=4)

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
