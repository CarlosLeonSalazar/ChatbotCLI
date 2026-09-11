# Python
import json
import uuid
from datetime import datetime

# LangChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Múdulo config
from config.config import DEFAULT_IA_MODEL, USERS_DIR


class ChatManager:
    """Gestiona los metadatos de las conversasiones de un usuario"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_dir = USERS_DIR / user_id
        self.chats_meta_file = self.user_dir / "chat_meta.json"
        self.llm = ChatOpenAI(model=DEFAULT_IA_MODEL, temperature=0)

    def get_user_chats(self):
        """Obtiene todos los chats del usuario"""

        try:
            if not self.chats_meta_file.exists():
                return []
            with self.chats_meta_file.open(
                'r',
                encoding="utf-8"
            ) as f:
                chats_data = json.load(f)
            chats_data.sort(
                key=lambda x: x.get("updated_at", ""),
                reverse=True
            )
            return chats_data
        except Exception as e:
            print(f"Error obteniedo chats: {e}")

    def _save_chats_metadata(self, chats_data):
        """Guarda los metadatos ligeros de los chats."""

        try:
            self.user_dir.mkdir(parents=True, exist_ok=True)

            with self.chats_meta_file.open(
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    chats_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            print(f"Error al guardar matedatos de chats: {e}")

    def create_new_chat(self, first_message: str = ""):
        """Crea un nuevo chat y actualiza sus metadatos"""

        chat_id = str(uuid.uuid4())

        title = (
            self._generate_chat_title(first_message)
            if first_message
            else "Nuevo chat"
        )

        now = datetime.now().isoformat()

        new_chat = {
            "chat_id": chat_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "message_count": 0
        }

        chats_data = self.get_user_chats()
        chats_data.append(new_chat)

        self._save_chats_metadata(chats_data)

        return chat_id

    def update_chat_metadata(
        self,
        chat_id: str,
        title: str | None = None,
        increment_messages: bool = False
    ):
        """Actualiza los metadatos de un chat"""

        chats_data = self.get_user_chats()

        for chat in chats_data:
            if chat["chat_id"] == chat_id:
                if title:
                    chat["title"] = title

                if increment_messages:
                    chat["message_count"] = (
                        chat.get("message_count", 0) + 1
                    )

                chat["updated_at"] = datetime.now().isoformat()
                break

        else:
            if chat_id:
                now = datetime.now().isoformat()

                new_chat = {
                    "chat_id": chat_id,
                    "title": title or "Chat sin título",
                    "created_at": now,
                    "updated_at": now,
                    "message_count": (
                        1 if increment_messages else 0
                    )
                }

                chats_data.append(new_chat)

        self._save_chats_metadata(chats_data)

    def delete_chat(self, chat_id: str):
        """Elimina un chat de los metadatos."""

        try:
            chats_data = self.get_user_chats()

            chats_data = [
                chat
                for chat in chats_data
                if chat["chat_id"] != chat_id
            ]

            self._save_chats_metadata(chats_data)

            return True

        except Exception as e:
            print(f"Error eliminando chat: {e}")
            return False

    def get_chat_info(self, chat_id: str):
        """Obtiene los metadatos de un chat."""

        chats = self.get_user_chats()

        for chat in chats:
            if chat["chat_id"] == chat_id:
                return chat

        return None

    def _generate_chat_title(self, first_message: str):
        """Genera un título corto para el chat."""

        try:
            title_prompt = PromptTemplate(
                template="""Genera un título corto
                (máximo 4-5 palabras) para una conversación
                que comienza con este mensaje:

                "{message}"

                El título debe:
                - Ser conciso y descriptivo
                - Capturar el tema principal
                - Ser apropiado para un historial de chat
                - No incluir comillas

                Título:""",
                input_variables=["message"]
            )

            title_chain = title_prompt | self.llm

            response = title_chain.invoke(
                {"message": first_message[:200]}
            )

            title = response.content.strip().strip('"').strip("'")

            return (
                title
                if len(title) <= 50
                else title[:47] + "..."
            )

        except Exception as e:
            print(f"Error generando título: {e}")

            return (
                first_message[:30] + "..."
                if len(first_message) > 30
                else first_message
            )

    def update_title_from_message(self, chat_id: str, message: str):
        """Actualiza el título del chat a partir de un mensaje."""

        chat = self.get_chat_info(chat_id)

        if chat is None:
            return

        if chat["title"] == "Nuevo chat":
            title = self._generate_chat_title(message)
            self.update_chat_metadata(chat_id, title=title)
