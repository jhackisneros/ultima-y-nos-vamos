import uuid
import datetime
from collections import defaultdict
from src.models.encuesta import Encuesta
from src.models.voto import Vote
from src.patterns.observer import Subject

class PollService(Subject):
    def __init__(self, encuesta_repository, nft_service, desempate_strategy):
        super().__init__()
        self.encuesta_repository = encuesta_repository
        self.nft_service = nft_service
        self.desempate_strategy = desempate_strategy
        self._polls = {}  # Cache en memoria de encuestas, id -> Encuesta
        self._load_polls()

    def _load_polls(self):
        # Carga las encuestas desde el repositorio al iniciar el servicio
        encuestas = self.encuesta_repository.get_all()
        for encuesta in encuestas:
            self._polls[encuesta.poll_id] = encuesta

    def create_poll(self, pregunta: str, opciones: list[str], duracion_segundos: int, tipo: str) -> Encuesta:
        poll_id = str(uuid.uuid4())
        timestamp_inicio = datetime.datetime.now()
        encuesta = Encuesta(
            poll_id=poll_id,
            pregunta=pregunta,
            opciones=opciones,
            votos=[],
            estado="activa",
            timestamp_inicio=timestamp_inicio,
            duracion=duracion_segundos,
            tipo=tipo,
        )
        self._polls[poll_id] = encuesta
        self.encuesta_repository.save(encuesta)
        return encuesta

    def vote(self, poll_id: str, username: str, opcion) -> bool:
        encuesta = self._polls.get(poll_id)
        if not encuesta:
            return False
        if encuesta.estado != "activa":
            return False
        # Verificar si el usuario ya votó
        if any(voto.usuario == username for voto in encuesta.votos):
            return False
        # Validar opción
        if encuesta.tipo == "simple":
            if opcion not in encuesta.opciones:
                return False
            voto = Vote(usuario=username, opcion=opcion)
        elif encuesta.tipo == "multiple":
            if not isinstance(opcion, list) or not all(o in encuesta.opciones for o in opcion):
                return False
            voto = Vote(usuario=username, opcion=opcion)
        else:
            # Otros tipos pueden implementarse aquí
            return False

        encuesta.votos.append(voto)
        self.encuesta_repository.save(encuesta)

        # Mint token NFT para cada opción votada
        opciones_votadas = opcion if isinstance(opcion, list) else [opcion]
        for op in opciones_votadas:
            self.nft_service.mint_token(username, poll_id, op)

        return True

    def close_poll(self, poll_id: str) -> bool:
        encuesta = self._polls.get(poll_id)
        if not encuesta or encuesta.estado != "activa":
            return False
        encuesta.estado = "cerrada"
        self.encuesta_repository.save(encuesta)
        self.notify_observers(encuesta)
        return True

    def check_and_close_expired_polls(self):
        ahora = datetime.datetime.now()
        for encuesta in self._polls.values():
            if encuesta.estado == "activa":
                tiempo_expiracion = encuesta.timestamp_inicio + datetime.timedelta(seconds=encuesta.duracion)
                if ahora >= tiempo_expiracion:
                    self.close_poll(encuesta.poll_id)

    def get_partial_results(self, poll_id: str) -> dict:
        encuesta = self._polls.get(poll_id)
        if not encuesta:
            raise ValueError("Encuesta no encontrada")
        return self._calcular_resultados(encuesta)

    def get_final_results(self, poll_id: str) -> dict:
        encuesta = self._polls.get(poll_id)
        if not encuesta:
            raise ValueError("Encuesta no encontrada")
        if encuesta.estado != "cerrada":
            raise ValueError("La encuesta no está cerrada")
        return self._calcular_resultados(encuesta)

    def _calcular_resultados(self, encuesta: Encuesta) -> dict:
        votos_por_opcion = defaultdict(int)
        total_votos = 0

        for voto in encuesta.votos:
            opciones = voto.opcion if isinstance(voto.opcion, list) else [voto.opcion]
            for op in opciones:
                votos_por_opcion[op] += 1
                total_votos += 1

        resultados = {}
        for opcion in encuesta.opciones:
            count = votos_por_opcion.get(opcion, 0)
            percent = (count / total_votos * 100) if total_votos > 0 else 0
            resultados[opcion] = (count, percent)

        # Si hay empate, aplicar estrategia de desempate (opcional)
        max_votos = max(votos_por_opcion.values()) if votos_por_opcion else 0
        opciones_max = [op for op, c in votos_por_opcion.items() if c == max_votos]
        if len(opciones_max) > 1:
            desempate = self.desempate_strategy.resolve(encuesta, opciones_max)
            resultados['desempate'] = desempate

        return resultados
