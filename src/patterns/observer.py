class Observer:
    def update(self, event, data):
        pass

class Observable:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def notify(self, event, data):
        for obs in self._observers:
            obs.update(event, data)
