from abc import ABC, abstractmethod
import random

class DesempateStrategy(ABC):
    @abstractmethod
    def resolver(self, encuesta):
        pass

class DesempateAlfabetico(DesempateStrategy):
    def resolver(self, encuesta):
        opciones_empate = encuesta.obtener_opciones_empate()
        return sorted(opciones_empate)[0]

class DesempateAleatorio(DesempateStrategy):
    def resolver(self, encuesta):
        opciones_empate = encuesta.obtener_opciones_empate()
        return random.choice(opciones_empate)

class DesempateProrroga(DesempateStrategy):
    def resolver(self, encuesta):
        # Aquí podrías implementar lógica para extender la encuesta y volver a votar
        # Pero para ejemplo simple, seleccionamos aleatoriamente
        opciones_empate = encuesta.obtener_opciones_empate()
        return random.choice(opciones_empate)

# Para formatos de resultados

class PresentacionStrategy(ABC):
    @abstractmethod
    def mostrar(self, resultados):
        pass

class PresentacionTexto(PresentacionStrategy):
    def mostrar(self, resultados):
        return '\n'.join(f"{opcion}: {count} votos ({porcentaje:.2f}%)" for opcion, (count, porcentaje) in resultados.items())

class PresentacionAscii(PresentacionStrategy):
    def mostrar(self, resultados):
        lines = []
        for opcion, (count, porcentaje) in resultados.items():
            barra = '#' * int(porcentaje)
            lines.append(f"{opcion}: {barra} ({count})")
        return '\n'.join(lines)

class PresentacionJson(PresentacionStrategy):
    def mostrar(self, resultados):
        import json
        return json.dumps({opcion: {'votos': count, 'porcentaje': porcentaje} for opcion, (count, porcentaje) in resultados.items()}, indent=4)
