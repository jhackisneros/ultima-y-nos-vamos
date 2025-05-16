import firebase_admin
from firebase_admin import credentials, firestore
import threading

class FirebaseClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, credential_path: str = None):
        with cls._lock:
            if cls._instance is None:
                cred = credentials.Certificate(credential_path)
                firebase_admin.initialize_app(cred)
                cls._instance = super().__new__(cls)
                cls._instance.db = firestore.client()
            return cls._instance

    def get_db(self):
        return self.db
