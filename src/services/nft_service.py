from src.patterns.observer import Observer

class NFTService(Observer):
    def __init__(self, nft_repository):
        self.nft_repository = nft_repository

    def mint_token(self, username, poll_id, option):
        # Aquí va la lógica para crear un token NFT y guardarlo
        # Por simplicidad dejamos la implementación aparte
        print(f"Minting NFT for {username} - poll {poll_id} - option {option}")

    def update(self, encuesta):
        # Se llama automáticamente cuando la encuesta se cierra
        print(f"NFTService recibió notificación: encuesta {encuesta.poll_id} cerrada")
        # Por ejemplo, aquí podrías emitir un NFT especial de cierre o notificar a usuarios
        # O actualizar algún estado interno
