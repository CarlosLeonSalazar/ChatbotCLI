"""Contenedor con scroll para el historial completo de la conversación."""

from __future__ import annotations

from textual.containers import VerticalScroll

from ui.widgets.message import ChatMessage


class ChatLog(VerticalScroll):
    """Lista vertical de ChatMessage con autoscroll al fondo."""

    DEFAULT_CSS = """
    ChatLog {
        width: 100%;
        height: 1fr;
        padding: 1;
    }
    """

    async def add_user_message(self, text: str) -> ChatMessage:
        msg = ChatMessage(role="user", text=text)
        self.mount(msg)
        self.scroll_end(animate=False)
        return msg

    async def add_assistant_message(self, text: str = "") -> ChatMessage:
        msg = ChatMessage(role="assistant", text=text)
        self.mount(msg)
        self.scroll_end(animate=False)
        return msg

    async def load_history(self, history: list[dict]) -> None:
        """Pinta el historial cargado desde get_conversation_history().

        Como estos mensajes ya vienen completos (no se van a seguir
        actualizando), se finalizan (Markdown) de inmediato -- no hay
        ventana de riesgo de colisión con un click porque el contenido
        no vuelve a cambiar tras esto."""

        for entry in history:
            role = entry.get("role", "assistant")
            text = entry.get("content", "")
            if role == "user":
                msg = await self.add_user_message(text)
            else:
                msg = await self.add_assistant_message(text)
            await msg.finalize()
