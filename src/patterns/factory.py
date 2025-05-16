import uuid
from datetime import datetime
from src.models.encuesta import Encuesta, EncuestaMultiple, EncuestaPonderada
from src.models.token_nft import TokenNFT, TokenNFTEdicionLimitada

class EncuestaFactory:
    @staticmethod
    def crear_encuesta(tipo: str, pregunta: str, opciones: list, duracion: int):
        poll_id = str(uuid.uuid4())
        timestamp_inicio = datetime.now()
        if tipo == 'simple':
            return Encuesta(poll_id, pregunta, opciones, [], 'activa', timestamp_inicio, duracion, tipo)
        elif tipo == 'multiple':
            return EncuestaMultiple(poll_id, pregunta, opciones, [], 'activa', timestamp_inicio, duracion, tipo)
        elif tipo == 'ponderada':
            return EncuestaPonderada(poll_id, pregunta, opciones, [], 'activa', timestamp_inicio, duracion, tipo)
        else:
            raise ValueError(f"Tipo de encuesta desconocido: {tipo}")

class TokenNFTFactory:
    @staticmethod
    def crear_token(owner: str, poll_id: str, option: str, edicion_limitada=False):
        token_id = str(uuid.uuid4())
        issued_at = datetime.now()
        if edicion_limitada:
            return TokenNFTEdicionLimitada(token_id, owner, poll_id, option, issued_at)
        else:
            return TokenNFT(token_id, owner, poll_id, option, issued_at)
