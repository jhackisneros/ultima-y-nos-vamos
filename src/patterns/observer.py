from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, encuesta):
        pass

class Subject:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, encuesta):
        for observer in self._observers:
            observer.update(encuesta)
