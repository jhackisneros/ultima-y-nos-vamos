from transformers import pipeline

class ChatbotService:
    def __init__(self):
        # Modelo español finetuneado para conversaciones
        self.chatbot = pipeline("conversational", model="mrm8488/bert-spanish-finetuned-conversational")
        self.histories = {}

    def ask(self, username, text):
        # Inicializa historial si no existe
        if username not in self.histories:
            self.histories[username] = []

        # Agrega la pregunta al historial
        self.histories[username].append({"role": "user", "content": text})

        # Para este pipeline básico no soporta contexto, así que se ignora historial
        response = self.chatbot(text)

        # Guarda respuesta en historial (opcional)
        self.histories[username].append({"role": "bot", "content": response[0]['generated_text']})

        return response[0]['generated_text']
