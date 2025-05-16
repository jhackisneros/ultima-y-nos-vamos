class UIController:
    def __init__(self, poll_service, user_service, nft_service, chatbot_service):
        self.poll_service = poll_service
        self.user_service = user_service
        self.nft_service = nft_service
        self.chatbot_service = chatbot_service
        self.sessions = {}  # para manejar sesiones de usuarios por sesión web

    # Registro usuario web
    def register(self, username, password):
        success, msg = self.user_service.register(username, password)
        return msg

    # Login usuario web
    def login(self, username, password):
        user, msg = self.user_service.login(username, password)
        if user:
            self.sessions[username] = user
            return True, f"Bienvenido, {username}"
        else:
            return False, msg

    # Obtener encuestas activas para mostrar en UI
    def get_active_polls(self):
        return [p for p in self.poll_service.list_polls() if p.active]

    # Votar desde UI
    def vote(self, poll_id, username, selected_options):
        # selected_options debe ser lista de strings
        success, msg = self.poll_service.vote(poll_id, username, selected_options)
        return msg

    # Obtener resultados parciales o finales según estado
    def get_results(self, poll_id):
        poll = self.poll_service.get_poll(poll_id)
        if not poll:
            return "Encuesta no encontrada."
        if poll.active:
            results = self.poll_service.get_partial_results(poll_id)
        else:
            results = self.poll_service.get_final_results(poll_id)
        return results

    # Obtener tokens de un usuario
    def get_user_tokens(self, username):
        return self.nft_service.get_tokens_of_owner(username)

    # Transferir token entre usuarios
    def transfer_token(self, token_id, current_owner, new_owner):
        success, msg = self.nft_service.transfer_token(token_id, current_owner, new_owner)
        return msg

    # Chatbot interacción
    def chatbot_query(self, username, text):
        response = self.chatbot_service.ask(username, text)
        return response
