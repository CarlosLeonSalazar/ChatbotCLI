"""Widget que representa un único mensaje (usuario o asistente) en el chat."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Markdown, Static


class ChatMessage(Vertical):
    """Burbuja de mensaje individual.

    - role="user" o role="assistant"
    - El contenido se renderiza como Markdown para que listas, código,
      negritas, etc. del LLM se vean correctamente.
    - `append_text` permite ir añadiendo texto (streaming token a token).
    - `set_status` / `clear_status` muestran una línea auxiliar tipo
      "usando herramienta X..." mientras el grafo está trabajando.
    """

    DEFAULT_CSS = """
    ChatMessage {
        width: 100%;
        height: auto;
        margin: 0 1 1 1;
        padding: 1 2;
        border: round $panel;
    }
    ChatMessage.-user {
        align-horizontal: right;
        background: $primary 10%;
        border: round $primary;
    }
    ChatMessage.-assistant {
        background: $panel;
    }
    ChatMessage .role-label {
        color: $text-muted;
        text-style: bold;
        height: 1;
    }
    ChatMessage .status-line {
        color: $warning;
        text-style: italic;
        height: auto;
    }
    """

    content: reactive[str] = reactive("", layout=True)
    status: reactive[str] = reactive("", layout=True)

    def __init__(self, role: str, text: str = "") -> None:
        super().__init__(classes=f"-{role}")
        self.role = role
        self.content = text

    def compose(self) -> ComposeResult:
        label = "Tú" if self.role == "user" else "Asistente"
        yield Static(label, classes="role-label")
        yield Static("", classes="status-line", id="status")
        # Durante el streaming usamos Static (plano, barato de actualizar).
        # Markdown.update() reconstruye sus widgets hijos en cada llamada,
        # y si un click llega en medio de esa reconstrucción, Textual crashea
        # (widget a medio montar sin contenedor resuelto). Por eso NO usamos
        # Markdown aquí mientras el texto sigue llegando token a token.
        yield Static(self.content, id="body")

    def append_text(self, chunk: str) -> None:
        """Añade un fragmento de texto (usado durante streaming)."""
        self.content += chunk
        self.query_one("#body", Static).update(self.content)
        self.scroll_visible()

    async def finalize(self) -> None:
        """Convierte el cuerpo a Markdown real. Llamar UNA VEZ, cuando el
        mensaje ya está completo (fin del streaming o mensaje histórico).
        A partir de aquí el contenido no vuelve a actualizarse, así que no
        hay más reconstrucciones del árbol interno -> click seguro.
        """
        old_body = self.query_one("#body")
        await old_body.remove()
        await self.mount(Markdown(self.content, id="body"))

    def set_status(self, text: str) -> None:
        self.query_one("#status", Static).update(f"⏳ {text}")

    def clear_status(self) -> None:
        self.query_one("#status", Static).update("")
