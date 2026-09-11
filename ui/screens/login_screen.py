"""Pantalla de login: pide un user_id, lo valida/crea con UserManager,
y solo entonces inicializa self.app.user_id y self.app.chatbot.

Muestra también los usuarios existentes (get_users()) como referencia,
pero el campo de texto acepta tanto un usuario existente como uno nuevo.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static

from chatbot.manager import ChatbotManager
from user.manager import UserManager


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        existing = UserManager.get_users()
        hint = (
            f"Usuarios existentes:\n{',\n'.join(existing)}"
            if existing
            else "Todavía no hay usuarios — se creará uno nuevo."
        )
        yield Vertical(
            Static("¿Quién eres?", classes="section-title"),
            Static(hint, classes="hint"),
            Input(placeholder="Escribe tu user_id y pulsa Enter...", id="user-input"),
            id="login-box",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_id = event.value.strip()
        if not user_id:
            return

        if not UserManager.user_exists(user_id):
            UserManager.create_user(user_id)

        self.app.user_id = user_id
        self.app.chatbot = ChatbotManager.get_chatbot(user_id)

        from ui.screens.chat_list_screen import ChatListScreen

        self.app.switch_screen(ChatListScreen())
