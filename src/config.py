import json
import os

class Config:
    def __init__(self, path='config.json'):
        self.path = path
        self.params = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.params = json.load(f)
        else:
            self.params = {
                "server_port": 7860,
                "model_name": "facebook/blenderbot-400M-distill",
                "db_path": "data/app.db",
                "default_desempate_strategy": "alfabetico"
            }

    def get(self, key, default=None):
        return self.params.get(key, default)
