# tests/test_checkpointer.py
import config.config as config
from chat.checkpointer import Checkpointer


async def test_checkpointer_initialization(tmp_path, monkeypatch):
    """
    Testea que Checkpointer crea correctamente la base de datos
    y que SqliteSaver/AsyncSqliteSaver se inicializan sin errores.
    """

    # 1. Crear directorio temporal que simula USERS_DIR
    fake_users_dir = tmp_path / "users"
    fake_users_dir.mkdir()

    # 2. Parchear USERS_DIR para que apunte al directorio temporal
    monkeypatch.setattr(config, "USERS_DIR", fake_users_dir)

    # 3. Crear un user_id de prueba
    user_id = "testuser2"

    # 4. Instanciar Checkpointer (la clase ya crea el directorio)
    #    Necesita un event loop activo por AsyncSqliteSaver -> por eso
    #    el test es async (pytest-asyncio, asyncio_mode = "auto").
    cp = Checkpointer(user_id)

    # 5. Verificar que la ruta de la DB es correcta
    expected_db_path = fake_users_dir / user_id / "langgraphmemory.db"
    assert cp.db_path == expected_db_path
    assert expected_db_path.exists(), "La base de datos debería existir"

    # 6. Verificar que la conexión SQLite síncrona funciona
    cursor = cp.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master")
    tables = cursor.fetchall()
    assert isinstance(tables, list)

    # 7. Verificar que SqliteSaver está inicializado
    assert cp.saver is not None

    # 8. Verificar que AsyncSqliteSaver / la conexión aiosqlite existen
    assert cp.async_saver is not None
    assert cp.async_conn is not None

    # aiosqlite.connect() es "perezoso": el objeto Connection se crea al
    # instante, pero la conexión SQLite real no se abre hasta hacer
    # `await` sobre él (o usarlo como `async with`). AsyncSqliteSaver
    # hace esto internamente antes de operar, pero aquí usamos la
    # conexión en crudo, así que lo disparamos explícitamente.
    await cp.async_conn

    # 9. Verificar que la conexión asíncrona funciona de verdad
    #    (no solo que el objeto existe, sino que puede ejecutar una query)
    async with cp.async_conn.execute("SELECT name FROM sqlite_master") as cursor_async:
        rows = await cursor_async.fetchall()
        assert isinstance(rows, list)

    # 10. Ambas conexiones (sync y async) apuntan al mismo fichero .db
    #     -- verificamos escribiendo por un lado y leyendo por el otro
    cp.conn.execute("CREATE TABLE IF NOT EXISTS _sanity_check (id INTEGER)")
    cp.conn.commit()

    async with cp.async_conn.execute(
        "SELECT name FROM sqlite_master WHERE name = '_sanity_check'"
    ) as cursor_async:
        result = await cursor_async.fetchone()
        assert result is not None, (
            "La conexión async no ve una tabla creada por la conexión sync "
            "-- ¿apuntan realmente al mismo fichero .db?"
        )

    # Limpieza
    await cp.async_conn.close()
    cp.conn.close()
