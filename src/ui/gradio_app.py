import gradio as gr
from src.controllers.ui_controller import UIController

def launch_gradio_ui(ui_controller):

    # Variables globales para sesión simple (puede mejorarse con cookies o base de sesión)
    logged_user = {"username": None}

    # Funciones para UI

    def register(username, password):
        return ui_controller.register(username, password)

    def login(username, password):
        success, msg = ui_controller.login(username, password)
        if success:
            logged_user["username"] = username
        return msg

    def logout():
        logged_user["username"] = None
        return "Sesión cerrada."

    def get_polls():
        polls = ui_controller.get_active_polls()
        # Devolver lista de opciones para dropdown con id y pregunta
        return [(str(poll.id), poll.question) for poll in polls]

    def vote(poll_id, option):
        if not logged_user["username"]:
            return "Debes iniciar sesión para votar."
        return ui_controller.vote(poll_id, logged_user["username"], [option])

    def show_results(poll_id):
        return ui_controller.get_results(poll_id)

    def get_tokens():
        if not logged_user["username"]:
            return []
        tokens = ui_controller.get_user_tokens(logged_user["username"])
        # Formatear para mostrar en tabla o lista
        return [{
            "Token ID": str(t.token_id),
            "Poll ID": str(t.poll_id),
            "Option": t.option,
            "Issued At": t.issued_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Owner": t.owner
        } for t in tokens]

    def transfer_token(token_id, new_owner):
        if not logged_user["username"]:
            return "Debes iniciar sesión para transferir tokens."
        return ui_controller.transfer_token(token_id, logged_user["username"], new_owner)

    # Chatbot
    def chatbot_respond(message):
        if not logged_user["username"]:
            return "Debes iniciar sesión para usar el chatbot."
        return ui_controller.chatbot_query(logged_user["username"], message)


    # Layout UI

    with gr.Blocks() as demo:

        gr.Markdown("## Plataforma Interactiva Streaming - Votaciones y NFT")

        with gr.Tab("Registro / Login"):
            reg_user = gr.Textbox(label="Usuario")
            reg_pass = gr.Textbox(label="Contraseña", type="password")
            reg_button = gr.Button("Registrar")
            reg_output = gr.Textbox(label="Mensaje Registro", interactive=False)

            reg_button.click(register, inputs=[reg_user, reg_pass], outputs=reg_output)

            login_user = gr.Textbox(label="Usuario")
            login_pass = gr.Textbox(label="Contraseña", type="password")
            login_button = gr.Button("Iniciar Sesión")
            login_output = gr.Textbox(label="Mensaje Login", interactive=False)
            logout_button = gr.Button("Cerrar Sesión")

            login_button.click(login, inputs=[login_user, login_pass], outputs=login_output)
            logout_button.click(logout, outputs=login_output)

        with gr.Tab("Encuestas"):
            poll_dropdown = gr.Dropdown(choices=[], label="Encuestas activas", interactive=True)
            vote_option = gr.Radio(choices=[], label="Opciones")
            vote_button = gr.Button("Votar")
            vote_output = gr.Textbox(label="Mensaje Voto", interactive=False)
            results_button = gr.Button("Mostrar Resultados")
            results_output = gr.Textbox(label="Resultados", interactive=False)

            def update_options(poll_id):
                if not poll_id:
                    return []
                polls = ui_controller.get_active_polls()
                poll = next((p for p in polls if str(p.id) == poll_id), None)
                if not poll:
                    return []
                return poll.options

            poll_dropdown.change(update_options, inputs=poll_dropdown, outputs=vote_option)

            vote_button.click(vote, inputs=[poll_dropdown, vote_option], outputs=vote_output)
            results_button.click(show_results, inputs=poll_dropdown, outputs=results_output)

        with gr.Tab("Tokens NFT"):
            tokens_table = gr.Dataframe(headers=["Token ID", "Poll ID", "Option", "Issued At", "Owner"], interactive=False)
            refresh_tokens = gr.Button("Actualizar Tokens")
            transfer_token_id = gr.Textbox(label="Token ID a transferir")
            transfer_new_owner = gr.Textbox(label="Nuevo propietario (username)")
            transfer_button = gr.Button("Transferir Token")
            transfer_output = gr.Textbox(label="Mensaje Transferencia", interactive=False)

            refresh_tokens.click(get_tokens, outputs=tokens_table)
            transfer_button.click(transfer_token, inputs=[transfer_token_id, transfer_new_owner], outputs=transfer_output)

        with gr.Tab("Chatbot IA"):
            chatbot = gr.Chatbot()
            message = gr.Textbox(label="Escribe tu mensaje")

            def respond(user_message, chat_history):
                response = chatbot_respond(user_message)
                chat_history = chat_history or []
                chat_history.append((user_message, response))
                return chat_history, ""

            message.submit(respond, inputs=[message, chatbot], outputs=[chatbot, message])

    demo.launch()
