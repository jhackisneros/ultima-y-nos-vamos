import sys
import os
import argparse
import threading

# Añade la raíz del proyecto al sys.path para permitir imports absolutos tipo 'src.*'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.controllers.cli_controller import CLIController
from src.controllers.ui_controller import UIController
from src.ui.gradio_app import launch_gradio_ui

# Importa o crea tus servicios aquí
from src.services.poll_service import PollService
from src.services.user_service import UserService
from src.services.nft_service import NFTService
from src.services.chatbot_service import ChatbotService
from src.repositories.encuesta_repo import EncuestaRepository
from src.repositories.nft_repo import NFTRepository
from src.repositories.usuario_repo import UsuarioRepository
from src.patterns.strategy import DesempateAlfabetico

def main():
    parser = argparse.ArgumentParser(description="Plataforma streaming interactiva")
    parser.add_argument("--ui", action="store_true", help="Arrancar con interfaz web Gradio")
    args = parser.parse_args()

    # Inicializa servicios y repositorios
    encuesta_repository = EncuestaRepository()
    nft_repository = NFTRepository()
    user_repository = UsuarioRepository()  # Asume constructor sin argumentos

    nft_service = NFTService(nft_repository)
    desempate_strategy = DesempateAlfabetico()

    poll_service = PollService(
        encuesta_repository,
        nft_service,
        desempate_strategy
    )
    user_service = UserService(user_repository)
    chatbot_service = ChatbotService()

    if args.ui:
        ui_controller = UIController(poll_service, user_service, nft_service, chatbot_service)
        launch_gradio_ui(ui_controller)
    else:
        cli_controller = CLIController(poll_service, user_service, nft_service, chatbot_service)
        cli_controller.run()

if __name__ == "__main__":
    main()
