# src/models/usuario.py

from typing import List
import uuid


class User:
    """
    Representa un usuario del sistema.

    Atributos:
        username (str): Nombre único de usuario.
        password_hash (str): Contraseña hasheada (no texto plano).
        tokens (List[str]): Lista de IDs de tokens NFT que posee.
    """

    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash
        self.tokens: List[str] = []

    def agregar_token(self, token_id: str):
        if token_id not in self.tokens:
            self.tokens.append(token_id)

    def eliminar_token(self, token_id: str):
        if token_id in self.tokens:
            self.tokens.remove(token_id)

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "tokens": self.tokens,
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        user = User(
            username=data["username"],
            password_hash=data["password_hash"]
        )
        user.tokens = data.get("tokens", [])
        return user


class Usuario:
    def __init__(self, username, password_hash, tokens=None):
        self.username = username
        self.password_hash = password_hash
        self.tokens = tokens if tokens is not None else []
    # Puedes agregar más métodos y atributos según tus necesidades
