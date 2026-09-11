"""Pantalla de listado de conversaciones del usuario.

Conectada a los métodos reales:
- Listar / crear: self.app.chatbot.chatmanager (ChatManager)
- Borrar: self.app.chatbot.delete_chat(chat_id) -- NO chatmanager.delete_chat()
  directamente, porque ModernChatbot.delete_chat() borra tanto el estado en
  LangGraph/SQLite como los metadatos en chat_meta.json. Llamar solo al
  método de chatmanager dejaría el estado de LangGraph huérfano.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem, ListView, Static

from ui.screens.chat_screen import ChatScreen


class ChatListScreen(Screen):
    BINDINGS = [
        ("ctrl+n", "new_chat", "Nuevo chat"),
        ("ctrl+d", "delete_chat", "Borrar chat"),
        ("escape", "back_to_home", "Volver a Inicio")
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Static("Tus conversaciones", classes="section-title"),
            ListView(*self._build_items(), id="chat-list"),
        )
        yield Footer()

    def _get_user_chats(self) -> list[dict]:
        """Devuelve los chats del usuario, más recientes primero."""
        return self.app.chatbot.chatmanager.get_user_chats()

    def _build_items(self) -> list[ListItem]:
        items = []
        for chat in self._get_user_chats():
            title = chat.get("title", "Chat sin título")
            item = ListItem(Static(title))
            # atributo custom para recuperarlo luego
            item.chat_id = chat["chat_id"]
            items.append(item)
        return items

    def _refresh_list(self) -> None:
        list_view = self.query_one("#chat-list", ListView)
        list_view.clear()
        for item in self._build_items():
            list_view.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        chat_id = getattr(event.item, "chat_id", None)
        if chat_id:
            self.app.push_screen(ChatScreen(chat_id=chat_id))

    def action_new_chat(self) -> None:
        new_id = self.app.chatbot.chatmanager.create_new_chat()
        self.app.push_screen(ChatScreen(chat_id=new_id))

    def action_delete_chat(self) -> None:
        list_view = self.query_one("#chat-list", ListView)
        if list_view.index is None:
            return

        item = list_view.children[list_view.index]
        chat_id = getattr(item, "chat_id", None)
        if not chat_id:
            return

        # Borra estado de LangGraph + metadatos a la vez (ver docstring arriba)
        if self.app.chatbot.delete_chat(chat_id):
            self._refresh_list()
        else:
            self.notify("No se pudo borrar el chat", severity="error")

    def on_screen_resume(self) -> None:
        # Refresca la lista al volver de ChatScreen (por si se creó/borró algo)
        self._refresh_list()

    def action_back_to_home(self) -> None:
        from ui.screens.login_screen import LoginScreen
        self.app.switch_screen(LoginScreen())
