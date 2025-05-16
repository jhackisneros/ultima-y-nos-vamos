# src/models/token_nft.py

import uuid
from datetime import datetime


class TokenNFT:
    """
    Representa un token NFT simulado generado al votar.

    Atributos:
        token_id (str): UUID único del token.
        owner (str): Usuario propietario del token.
        poll_id (str): ID de la encuesta asociada.
        option (str): Opción votada que dio origen al token.
        issued_at (datetime): Fecha de emisión del token.
    """

    def __init__(self, owner: str, poll_id: str, option: str):
        self.token_id = str(uuid.uuid4())
        self.owner = owner
        self.poll_id = poll_id
        self.option = option
        self.issued_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "owner": self.owner,
            "poll_id": self.poll_id,
            "option": self.option,
            "issued_at": self.issued_at.isoformat()
        }

    @staticmethod
    def from_dict(data: dict) -> "TokenNFT":
        token = TokenNFT(
            owner=data["owner"],
            poll_id=data["poll_id"],
            option=data["option"]
        )
        token.token_id = data["token_id"]
        token.issued_at = datetime.fromisoformat(data["issued_at"])
        return token
    def to_dict(self):
        return {
            "token_id": str(self.token_id),
            "owner": self.owner,
            "poll_id": str(self.poll_id),
            "option": self.option,
            "issued_at": self.issued_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return TokenNFT(
            token_id=UUID(data["token_id"]),
            owner=data["owner"],
            poll_id=UUID(data["poll_id"]),
            option=data["option"],
            issued_at=datetime.fromisoformat(data["issued_at"])
        )
