from getpass import getpass
# Asegúrate de importar servicios y modelos desde los nuevos paquetes
# from ..services.poll_service import PollService
# from ..services.user_service import UserService
# from ..services.nft_service import NFTService
# from ..services.chatbot_service import ChatbotService

class CLIController:
    def __init__(self, poll_service, user_service, nft_service, chatbot_service):
        self.poll_service = poll_service
        self.user_service = user_service
        self.nft_service = nft_service
        self.chatbot_service = chatbot_service
        self.current_user = None

    def run(self):
        print("Bienvenido al sistema de votaciones interactivas")
        while True:
            if not self.current_user:
                print("\nComandos: register, login, exit")
                cmd = input("> ").strip().lower()
                if cmd == "register":
                    self.register()
                elif cmd == "login":
                    self.login()
                elif cmd == "exit":
                    print("Saliendo...")
                    break
                else:
                    print("Comando no reconocido.")
            else:
                print(f"\nUsuario: {self.current_user.username}")
                print("Comandos: crear_encuesta, listar_encuestas, votar, ver_resultados, cerrar_encuesta, mis_tokens, transferir_token, chat, logout, exit")
                cmd = input("> ").strip().lower()
                if cmd == "crear_encuesta":
                    self.crear_encuesta()
                elif cmd == "listar_encuestas":
                    self.listar_encuestas()
                elif cmd == "votar":
                    self.votar()
                elif cmd == "ver_resultados":
                    self.ver_resultados()
                elif cmd == "cerrar_encuesta":
                    self.cerrar_encuesta()
                elif cmd == "mis_tokens":
                    self.mis_tokens()
                elif cmd == "transferir_token":
                    self.transferir_token()
                elif cmd == "chat":
                    self.chat()
                elif cmd == "logout":
                    self.current_user = None
                    print("Sesión cerrada.")
                elif cmd == "exit":
                    print("Saliendo...")
                    break
                else:
                    print("Comando no reconocido.")

    def register(self):
        print("Registro de usuario")
        username = input("Username: ").strip()
        while True:
            # Preguntar si quiere mostrar o no la contraseña al escribir
            mostrar = input("¿Quieres mostrar la contraseña mientras escribes? (s/n): ").strip().lower()
            if mostrar in ['s', 'n']:
                break
            print("Responde con 's' o 'n'.")

        if mostrar == 's':
            password = input("Password: ")
        else:
            password = getpass("Password: ")

        success, msg = self.user_service.register(username, password)
        print(msg)
        if success:
            print("Ahora puedes hacer login.")

    def login(self):
        print("Login de usuario")
        username = input("Username: ").strip()
        password = getpass("Password: ")
        user, msg = self.user_service.login(username, password)
        if user:
            self.current_user = user
            print(f"Bienvenido, {user.username}")
        else:
            print(f"Error: {msg}")

    def crear_encuesta(self):
        print("Crear nueva encuesta")
        pregunta = input("Pregunta: ").strip()
        opciones = []
        print("Introduce las opciones (una por línea). Deja línea vacía para terminar:")
        while True:
            opt = input("> ").strip()
            if not opt:
                break
            opciones.append(opt)
        if len(opciones) < 2:
            print("Debe haber al menos dos opciones.")
            return

        while True:
            try:
                duracion = int(input("Duración en segundos: ").strip())
                if duracion <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Introduce un número entero positivo.")

        tipo = input("Tipo de encuesta (simple/multiple): ").strip().lower()
        if tipo not in ['simple', 'multiple']:
            print("Tipo no válido, se usará 'simple' por defecto.")
            tipo = 'simple'

        poll = self.poll_service.create_poll(pregunta, opciones, duracion, tipo)
        print(f"Encuesta creada con ID: {poll.id}")

    def listar_encuestas(self):
        polls = self.poll_service.list_polls()
        if not polls:
            print("No hay encuestas.")
            return
        for p in polls:
            estado = "Activa" if p.active else "Cerrada"
            print(f"ID: {p.id} | Pregunta: {p.question} | Estado: {estado}")

    def votar(self):
        poll_id = input("ID de la encuesta: ").strip()
        poll = self.poll_service.get_poll(poll_id)
        if not poll:
            print("Encuesta no encontrada.")
            return
        if not poll.active:
            print("La encuesta está cerrada.")
            return

        print("Opciones:")
        for idx, opt in enumerate(poll.options, 1):
            print(f"{idx}. {opt}")

        if poll.poll_type == "simple":
            try:
                opcion = int(input("Selecciona opción (número): ").strip())
                if opcion < 1 or opcion > len(poll.options):
                    raise ValueError
                opciones = [poll.options[opcion - 1]]
            except ValueError:
                print("Opción no válida.")
                return
        else:
            print("Introduce números de opciones separados por coma (ejemplo: 1,3):")
            entrada = input("> ").strip()
            try:
                indices = [int(i) for i in entrada.split(",") if i.strip()]
                if any(i < 1 or i > len(poll.options) for i in indices):
                    raise ValueError
                opciones = [poll.options[i - 1] for i in indices]
            except ValueError:
                print("Opciones no válidas.")
                return

        success, msg = self.poll_service.vote(poll_id, self.current_user.username, opciones)
        print(msg)

    def ver_resultados(self):
        poll_id = input("ID de la encuesta: ").strip()
        poll = self.poll_service.get_poll(poll_id)
        if not poll:
            print("Encuesta no encontrada.")
            return

        if poll.active:
            resultados = self.poll_service.get_partial_results(poll_id)
            print("Resultados parciales:")
        else:
            resultados = self.poll_service.get_final_results(poll_id)
            print("Resultados finales:")

        for opcion, datos in resultados.items():
            print(f"{opcion}: {datos['count']} votos ({datos['percentage']:.2f}%)")

    def cerrar_encuesta(self):
        poll_id = input("ID de la encuesta a cerrar: ").strip()
        success, msg = self.poll_service.close_poll(poll_id)
        print(msg)

    def mis_tokens(self):
        tokens = self.nft_service.get_tokens_of_owner(self.current_user.username)
        if not tokens:
            print("No tienes tokens.")
            return
        print("Tus tokens:")
        for t in tokens:
            print(f"ID: {t.token_id} | Encuesta: {t.poll_id} | Opción: {t.option} | Emitido: {t.issued_at}")

    def transferir_token(self):
        token_id = input("ID del token a transferir: ").strip()
        nuevo_owner = input("Nuevo propietario (username): ").strip()
        success, msg = self.nft_service.transfer_token(token_id, self.current_user.username, nuevo_owner)
        print(msg)

    def chat(self):
        print("Chatbot interactivo (escribe 'salir' para terminar)")
        while True:
            texto = input(f"{self.current_user.username}: ")
            if texto.lower() == 'salir':
                break
            respuesta = self.chatbot_service.ask(self.current_user.username, texto)
            print(f"Bot: {respuesta}")
