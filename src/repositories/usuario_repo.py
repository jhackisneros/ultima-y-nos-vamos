from src.repositories.firebase_client import FirebaseClient
from src.models.usuario import Usuario
from src.models.token_nft import TokenNFT
from typing import Optional

class UsuarioRepository:
    def __init__(self, firebase_client: FirebaseClient):
        self.db = firebase_client.get_db()
        self.collection = self.db.collection("usuarios")

    def add_user(self, usuario: Usuario):
        self.collection.document(usuario.username).set({
            "password_hash": usuario.password_hash,
            "tokens": [token.to_dict() for token in usuario.tokens]
        })

    def get_user(self, username: str) -> Optional[Usuario]:
        doc = self.collection.document(username).get()
        if doc.exists:
            data = doc.to_dict()
            tokens = [TokenNFT.from_dict(t) for t in data.get("tokens", [])]
            return Usuario(username=username, password_hash=data["password_hash"], tokens=tokens)
        return None

    def update_user_tokens(self, username: str, tokens):
        self.collection.document(username).update({
            "tokens": [token.to_dict() for token in tokens]
        })
