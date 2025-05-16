import argparse
import threading

from src.controllers.cli_controller import CLIController
from src.controllers.ui_controller import UIController
from src.ui.gradio_app import launch_gradio_ui

# Importa o crea tus servicios aquí
from src.services.poll_service import PollService
from src.services.user_service import UserService
from src.services.nft_service import NFTService
from src.services.chatbot_service import ChatbotService

def main():
    parser = argparse.ArgumentParser(description="Plataforma streaming interactiva")
    parser.add_argument("--ui", action="store_true", help="Arrancar con interfaz web Gradio")
    args = parser.parse_args()

    # Inicializa servicios
    poll_service = PollService()
    user_service = UserService()
    nft_service = NFTService()
    chatbot_service = ChatbotService()

    if args.ui:
        ui_controller = UIController(poll_service, user_service, nft_service, chatbot_service)
        # Lanzar UI Gradio en hilo principal
        launch_gradio_ui(ui_controller)
    else:
        # CLI en consola
        cli_controller = CLIController(poll_service, user_service, nft_service, chatbot_service)
        cli_controller.run()

if __name__ == "__main__":
    main()
