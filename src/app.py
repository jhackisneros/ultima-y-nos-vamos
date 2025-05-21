import sys
import os
import argparse
import threading
import gradio as gr
import re
import json
import uuid
from datetime import datetime, timedelta

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

# Simulación de almacenamiento de usuarios en memoria
usuarios_registrados = {}

# --- Persistencia simple en disco para encuestas y votos ---
ENCUESTAS_FILE = "encuestas.json"
VOTOS_FILE = "votos.json"
TOKENS_FILE = "tokens.json"

def cargar_encuestas():
    try:
        with open(ENCUESTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_encuestas(encuestas):
    with open(ENCUESTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(encuestas, f, ensure_ascii=False, indent=2)

def cargar_votos():
    try:
        with open(VOTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_votos(votos):
    with open(VOTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(votos, f, ensure_ascii=False, indent=2)

def cargar_tokens():
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_tokens(tokens):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

def validar_password(password):
    # Al menos 7 caracteres, una mayúscula, una minúscula, un número
    if len(password) < 7:
        return False, "La contraseña debe tener al menos 7 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe tener al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe tener al menos una letra minúscula."
    if not re.search(r"\d", password):
        return False, "La contraseña debe tener al menos un número."
    return True, ""

# Simulación de datos y funciones (luego se conectarán a los servicios reales)
def login(username, password):
    # Ahora verifica contra el almacenamiento real
    if username in usuarios_registrados and usuarios_registrados[username] == password:
        return f"Bienvenido, {username}", gr.update(visible=True)
    return "Usuario o contraseña incorrectos", gr.update(visible=False)

def registrar(username, password):
    # Valida requisitos de contraseña
    if username in usuarios_registrados:
        return "El usuario ya existe"
    if not username or not password:
        return "Usuario y contraseña requeridos"
    valido, msg = validar_password(password)
    if not valido:
        return msg
    usuarios_registrados[username] = password
    return f"Usuario {username} registrado correctamente"

def crear_encuesta(pregunta, opciones, duracion_segundos, tipo):
    encuestas = cargar_encuestas()
    nueva = {
        "id": str(len(encuestas) + 1),
        "pregunta": pregunta,
        "opciones": opciones,
        "tipo": tipo,
        "estado": "Activa",
        "inicio": datetime.now().isoformat(),
        "fin": (datetime.now() + timedelta(seconds=int(duracion_segundos))).isoformat()
    }
    encuestas.append(nueva)
    guardar_encuestas(encuestas)
    return f"Encuesta creada con ID {nueva['id']}"

def listar_encuestas():
    encuestas = cargar_encuestas()
    ahora = datetime.now()
    # Cierre automático si corresponde
    for e in encuestas:
        if e["estado"] == "Activa" and datetime.fromisoformat(e["fin"]) < ahora:
            e["estado"] = "Cerrada"
    guardar_encuestas(encuestas)
    return encuestas

def votar(poll_id, opcion, username):
    encuestas = cargar_encuestas()
    votos = cargar_votos()
    encuesta = next((e for e in encuestas if e["id"] == poll_id), None)
    if not encuesta:
        return "Encuesta no encontrada"
    if encuesta["estado"] != "Activa":
        return "La encuesta está cerrada"
    # Un voto por usuario por encuesta
    if any(v["poll_id"] == poll_id and v["username"] == username for v in votos):
        return "Ya has votado en esta encuesta"
    if opcion not in encuesta["opciones"]:
        return "Opción no válida"
    votos.append({
        "poll_id": poll_id,
        "opcion": opcion,
        "username": username,
        "timestamp": datetime.now().isoformat()
    })
    guardar_votos(votos)
    mint_token(username, poll_id, opcion)
    return f"Voto registrado en encuesta {poll_id}: opción {opcion}. ¡Token NFT generado!"

def cerrar_encuesta(poll_id):
    encuestas = cargar_encuestas()
    encuesta = next((e for e in encuestas if e["id"] == poll_id), None)
    if not encuesta:
        return "Encuesta no encontrada"
    encuesta["estado"] = "Cerrada"
    guardar_encuestas(encuestas)
    return f"Encuesta {poll_id} cerrada"

def resultados_encuesta(poll_id):
    encuestas = cargar_encuestas()
    votos = cargar_votos()
    encuesta = next((e for e in encuestas if e["id"] == poll_id), None)
    if not encuesta:
        return "Encuesta no encontrada", {}
    total = sum(1 for v in votos if v["poll_id"] == poll_id)
    conteo = {op: 0 for op in encuesta["opciones"]}
    for v in votos:
        if v["poll_id"] == poll_id:
            conteo[v["opcion"]] += 1
    resultados = {op: f"{conteo[op]} votos ({(conteo[op]/total*100 if total else 0):.1f}%)" for op in conteo}
    return f"Resultados de la encuesta '{encuesta['pregunta']}':", resultados

def mint_token(username, poll_id, option):
    tokens = cargar_tokens()
    token_id = str(uuid.uuid4())
    token = {
        "token_id": token_id,
        "owner": username,
        "poll_id": poll_id,
        "option": option,
        "issued_at": datetime.now().isoformat()
    }
    tokens.append(token)
    guardar_tokens(tokens)
    return token

def ver_tokens(username):
    tokens = cargar_tokens()
    return [t for t in tokens if t["owner"] == username]

def transferir_token(token_id, nuevo_owner):
    tokens = cargar_tokens()
    for t in tokens:
        if t["token_id"] == token_id:
            t["owner"] = nuevo_owner
            guardar_tokens(tokens)
            return f"Token {token_id} transferido a {nuevo_owner}"
    return "Token no encontrado"

def chatbot_fn(user, mensaje):
    # Simulación de respuesta del bot
    if "ganando" in mensaje:
        return "Actualmente va ganando la opción 'Sí' en la encuesta 1."
    return f"Bot: Recibí tu mensaje, {user}: {mensaje}"

# --- UI Gradio ---

with gr.Blocks(title="Votaciones Interactivas") as demo:
    gr.Markdown("# Plataforma de Votaciones Interactivas para Streamers")

    with gr.Tab("Login"):
        usuario = gr.Textbox(label="Usuario")
        password = gr.Textbox(label="Contraseña", type="password")
        login_btn = gr.Button("Iniciar sesión")
        login_msg = gr.Markdown()
        # Nuevo: Registro
        gr.Markdown("¿No tienes cuenta? Regístrate aquí:")
        reg_usuario = gr.Textbox(label="Nuevo usuario")
        reg_password = gr.Textbox(label="Nueva contraseña", type="password")
        reg_btn = gr.Button("Registrarse")
        reg_msg = gr.Markdown()
        main_panel = gr.Row(visible=False)

        def on_login(u, p):
            msg, visible = login(u, p)
            return msg, visible

        def on_registrar(u, p):
            return registrar(u, p)

        login_btn.click(on_login, inputs=[usuario, password], outputs=[login_msg, main_panel])
        reg_btn.click(on_registrar, inputs=[reg_usuario, reg_password], outputs=reg_msg)

    with main_panel:
        with gr.Tab("Encuestas"):
            gr.Markdown("## Crear nueva encuesta")
            pregunta = gr.Textbox(label="Pregunta")
            opciones = gr.Textbox(label="Opciones (separadas por coma)")
            duracion = gr.Number(label="Duración (segundos)", value=60)
            tipo = gr.Dropdown(choices=["simple", "multiple"], value="simple", label="Tipo")
            crear_btn = gr.Button("Crear encuesta")
            crear_msg = gr.Markdown()

            crear_btn.click(
                lambda p, o, d, t: crear_encuesta(p, [x.strip() for x in o.split(",") if x.strip()], d, t),
                inputs=[pregunta, opciones, duracion, tipo],
                outputs=crear_msg
            )

            gr.Markdown("## Listado de encuestas")
            encuesta_list = gr.Dataframe(
                headers=["ID", "Pregunta", "Opciones", "Tipo", "Estado", "Inicio", "Fin"],
                datatype=["str"]*7,
                value=[[e["id"], e["pregunta"], ", ".join(e["opciones"]), e["tipo"], e["estado"], e["inicio"], e["fin"]] for e in listar_encuestas()],
                interactive=False,
                label="Encuestas activas"
            )

            gr.Markdown("## Votar en encuesta")
            encuesta_id = gr.Textbox(label="ID de la encuesta para votar")
            opcion = gr.Textbox(label="Opción (texto exacto)")
            usuario_voto = gr.Textbox(label="Usuario")
            votar_btn = gr.Button("Votar")
            voto_msg = gr.Markdown()
            votar_btn.click(lambda eid, op, u: votar(eid, op, u), inputs=[encuesta_id, opcion, usuario_voto], outputs=voto_msg)

            gr.Markdown("## Cerrar encuesta")
            cerrar_id = gr.Textbox(label="ID de la encuesta a cerrar")
            cerrar_btn = gr.Button("Cerrar encuesta")
            cerrar_msg = gr.Markdown()
            cerrar_btn.click(cerrar_encuesta, inputs=cerrar_id, outputs=cerrar_msg)

            gr.Markdown("## Resultados de encuesta")
            res_id = gr.Textbox(label="ID de la encuesta para ver resultados")
            res_btn = gr.Button("Ver resultados")
            res_msg = gr.Markdown()
            res_table = gr.Dataframe(headers=["Opción", "Resultado"], datatype=["str", "str"], value=[])
            def ver_resultados(eid):
                msg, resultados = resultados_encuesta(eid)
                tabla = [[op, resultados[op]] for op in resultados]
                return msg, tabla
            res_btn.click(ver_resultados, inputs=res_id, outputs=[res_msg, res_table])

        with gr.Tab("Mis Tokens"):
            gr.Markdown(
                "Cada vez que votas en una encuesta, recibes un Token NFT simulado. "
                "Puedes ver tus tokens aquí y transferirlos a otros usuarios."
            )
            usuario_tokens = gr.Textbox(label="Usuario para ver tokens")
            tokens_btn = gr.Button("Ver mis tokens")
            tokens_galeria = gr.Dataframe(
                headers=["Token ID", "Encuesta", "Opción", "Emitido", "Propietario"],
                datatype=["str", "str", "str", "str", "str"],
                value=[],
                interactive=False,
                label="Galería de tokens"
            )
            tokens_btn.click(
                lambda u: [[t["token_id"], t["poll_id"], t["option"], t["issued_at"], t["owner"]] for t in ver_tokens(u)],
                inputs=usuario_tokens,
                outputs=tokens_galeria
            )
            transfer_id = gr.Textbox(label="Token ID a transferir")
            nuevo_owner = gr.Textbox(label="Nuevo propietario")
            transfer_btn = gr.Button("Transferir token")
            transfer_msg = gr.Markdown()
            transfer_btn.click(transferir_token, inputs=[transfer_id, nuevo_owner], outputs=transfer_msg)

        with gr.Tab("Chatbot"):
            chat_user = gr.Textbox(label="Usuario")
            chat_input = gr.Textbox(label="Mensaje")
            chat_btn = gr.Button("Enviar")
            chat_output = gr.Markdown()
            chat_btn.click(chatbot_fn, inputs=[chat_user, chat_input], outputs=chat_output)

if __name__ == "__main__":
    demo.launch()
