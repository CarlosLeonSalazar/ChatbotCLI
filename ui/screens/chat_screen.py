"""Pantalla principal de conversación, conectada al ModernChatbot real
obtenido a través de ChatbotManager (ver app.py).

Actualización: 2024-06-05
Sustituye Input por TextArea en chat_screen.py.

Como Enter siempre añade línea nueva en TextArea (comportamiento por
defecto, y no se puede fiablemente distinguir Shift+Enter en terminal),
usamos una tecla de modificador que SÍ se transmite bien: Ctrl+S para
enviar. Es la solución más robusta entre terminales (Windows Terminal,
iTerm, etc.), en vez de depender de Shift+Enter.
"""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, TextArea, Button

from ui.widgets.chat_log import ChatLog


class ChatScreen(Screen):
    BINDINGS = [
        ("ctrl+n", "new_chat", "Nuevo chat"),
        ("escape", "back_to_list", "Volver a mis chats"),
        Binding("ctrl+s", "send_message", "Enviar", priority=True)
    ]

    def __init__(self, chat_id: str) -> None:
        super().__init__()
        self.chat_id = chat_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ChatLog(id="log")
        with Horizontal(id="input-bar"):
            yield TextArea(id="input", soft_wrap=True)
            yield Button("Enviar", id="send-btn", variant="primary")
        yield Footer()

    async def on_mount(self) -> None:
        chatbot = self.app.chatbot
        history = chatbot.get_conversation_history(chat_id=self.chat_id)
        if history:
            await self.query_one(ChatLog).load_history(history)
        self.query_one(TextArea).focus()

    async def action_send_message(self) -> None:
        await self._send_current_text()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            await self._send_current_text()

    async def _send_current_text(self) -> None:
        text_area = self.query_one(TextArea)
        text = text_area.text.strip()
        if not text:
            return
        text_area.clear()
        log = self.query_one(ChatLog)
        await log.add_user_message(text)
        self.stream_response(text)

    @work(exclusive=True)
    async def stream_response(self, user_text: str) -> None:
        log = self.query_one(ChatLog)
        bubble = await log.add_assistant_message("")
        chatbot = self.app.chatbot  # instancia de ModernChatbot vía ChatbotManager

        async for event in chatbot.astream_events(user_text, chat_id=self.chat_id):
            kind = event["event"]

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    bubble.append_text(chunk)

            elif kind == "on_tool_start":
                bubble.set_status(f"usando {event['name']}...")
            elif kind == "on_tool_end":
                bubble.clear_status()

            # Nodos reales de state_graph.py, en orden:
            # memory_retrieval -> context_optimization -> response_generation
            # -> memory_extraction -> memory_persistence
            elif kind == "on_chain_start" and event.get("name") == "memory_retrieval":
                bubble.set_status("consultando memoria...")
            elif kind == "on_chain_end" and event.get("name") == "memory_retrieval":
                bubble.clear_status()

            elif kind == "on_chain_start" and event.get("name") == "memory_extraction":
                bubble.set_status("analizando la conversación...")
            elif kind == "on_chain_start" and event.get("name") == "memory_persistence":
                bubble.set_status("guardando memoria...")
            elif kind == "on_chain_end" and event.get("name") == "memory_persistence":
                bubble.clear_status()

            elif kind == "on_astream_error":
                bubble.clear_status()
                bubble.append_text(f"\n\n⚠️ Error: {event['data']['error']}")

        # Streaming terminado (con o sin error): convierte a Markdown UNA
        # vez. A partir de aquí el contenido no cambia más, así que hacer
        # click ya no puede coincidir con una reconstrucción interna.
        await bubble.finalize()

    def action_new_chat(self) -> None:
        self.query_one(ChatLog).remove_children()

    def action_back_to_list(self) -> None:
        self.app.pop_screen()
