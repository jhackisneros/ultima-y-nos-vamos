# src/services/user_service.py

import bcrypt
import uuid
from typing import Optional
from src.models.usuario import User
from src.repositories.usuario_repo import UsuarioRepository


class UserService:
    """
    Servicio para registrar usuarios, validar login y gestionar sesiones temporales.
    """

    def __init__(self, user_repo: UsuarioRepository):
        self.user_repo = user_repo
        self.sessions = {}  # username -> session_token (UUID string)

    def register(self, username: str, password: str) -> bool:
        if self.user_repo.exists(username):
            return False

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        user = User(username=username, password_hash=hashed.decode(), tokens=[])
        self.user_repo.save(user)
        return True

    def login(self, username: str, password: str) -> Optional[str]:
        user = self.user_repo.get(username)
        if not user:
            return None

        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            session_token = str(uuid.uuid4())
            self.sessions[username] = session_token
            return session_token

        return None

    def is_logged_in(self, username: str, token: str) -> bool:
        return self.sessions.get(username) == token

    def logout(self, username: str):
        if username in self.sessions:
            del self.sessions[username]
