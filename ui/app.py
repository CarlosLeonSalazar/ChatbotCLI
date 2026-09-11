"""App principal. Ejecuta con: uv run python -m ui.app

Arranca en LoginScreen, que pide el user_id, lo valida/crea vía
UserManager, y solo entonces resuelve self.chatbot vía ChatbotManager
antes de pasar a la lista de chats.
"""

from __future__ import annotations

from textual.app import App

from ui.screens.login_screen import LoginScreen


class ChatApp(App):
    TITLE = "ChatbotCli"
    SUB_TITLE = "LangChain/LangGraph - OpenAI (gpt-4o-mini)"
    CSS_PATH = "app.tcss"

    # user_id y chatbot se rellenan en LoginScreen tras el login,
    # no en __init__ -- todavía no sabemos quién es el usuario aquí.
    user_id: str | None = None
    chatbot = None

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())

    async def on_unmount(self) -> None:
        """Cierra las conexiones de Checkpointer al salir.

        Sin esto, el hilo interno de aiosqlite puede quedar vivo al
        pulsar Ctrl+Q, impidiendo que Textual restaure la terminal
        correctamente (cursor/eco rotos tras salir).
        """
        if self.chatbot is None:
            return

        checkpointer = self.chatbot.checkpointer

        try:
            await checkpointer.async_conn.close()
        except Exception:
            pass

        try:
            checkpointer.conn.close()
        except Exception:
            pass


def main() -> None:
    """Punto de entrada para el comando instalado (ver [project.scripts])."""
    ChatApp().run()


if __name__ == "__main__":
    main()
