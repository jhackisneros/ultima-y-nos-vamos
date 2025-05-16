# src/repositories/nft_repo.py

import json
from typing import List, Optional
from src.models.token_nft import TokenNFT


class NFTRepository:
    """
    Repositorio para persistencia de tokens NFT simulados en JSON.
    """

    def __init__(self, filepath: str = "nfts.json"):
        self.filepath = filepath
        self._cache: List[TokenNFT] = []
        self._load()

    def _load(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._cache = [TokenNFT.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = []

    def _save(self):
        data = [token.to_dict() for token in self._cache]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def save(self, token: TokenNFT):
        self._cache.append(token)
        self._save()

    def get_by_owner(self, owner: str) -> List[TokenNFT]:
        return [token for token in self._cache if token.owner == owner]

    def get(self, token_id: str) -> Optional[TokenNFT]:
        for token in self._cache:
            if token.token_id == token_id:
                return token
        return None

    def update(self, token: TokenNFT):
        for i, t in enumerate(self._cache):
            if t.token_id == token.token_id:
                self._cache[i] = token
                self._save()
                break
