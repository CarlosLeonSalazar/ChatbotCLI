# Python
import sqlite3
import aiosqlite

# LangGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # <-- NUEVO
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

# módulo config
import config.config as config


class Checkpointer:
    """Clase que maneja estado/historial de la conversación con LangGraph"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db_path = config.USERS_DIR / user_id / "langgraphmemory.db"

        # Crear directorio si no existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        serde = JsonPlusSerializer(
            allowed_msgpack_modules=[("memory.models", "ExtractedMemory")]
        )

        self.saver = SqliteSaver(self.conn, serde=serde)

        # --- NUEVO: conexión ASÍNCRONA, mismo fichero .db, para astream_events ---
        # aiosqlite.connect() no bloquea: arranca su propio hilo interno y
        # puede llamarse fuera de una función async sin problema.
        self.async_conn = aiosqlite.connect(self.db_path)
        self.async_saver = AsyncSqliteSaver(self.async_conn, serde=serde)
