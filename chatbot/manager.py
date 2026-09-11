from graph.modern_chatbot import ModernChatbot


class ChatbotManager:
    """Gestiona las instancias de ModernChatbot por usuario."""

    _instances = {}

    @classmethod
    def get_chatbot(cls, user_id):
        """Obtiene o crea una instancia de chatbot para un usuario."""
        if user_id not in cls._instances:
            cls._instances[user_id] = ModernChatbot(user_id)

        return cls._instances[user_id]

    @classmethod
    def remove_chatbot(cls, user_id):
        """Elimina una instancia de chatbot."""
        if user_id in cls._instances:
            del cls._instances[user_id]

    @classmethod
    def clear_all(cls):
        """Elimina todas las instancias de chatbot."""
        cls._instances.clear()
