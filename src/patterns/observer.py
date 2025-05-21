class Observer:
    def update(self, event, data):
        pass

class Subject:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def unregister(self, observer):
        self._observers.remove(observer)

    def notify(self, event, data):
        for observer in self._observers:
            observer.update(event, data)
