import chat.manager as chat_manager
from types import SimpleNamespace

from langchain_core.runnables import RunnableLambda


def fake_llm():
    return RunnableLambda(
        lambda _: SimpleNamespace(
            content="Python y LangGraph"
        )
    )


class FakeResponse:
    """Respuesta simulada del LLM."""

    content = "Python y LangGraph"


class FakeLLM:
    """Sustituto del LLM para los tests."""

    def invoke(self, input):
        return FakeResponse()


def test_get_user_chats_when_no_file_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)

    manager = chat_manager.ChatManager("carlos")

    assert manager.get_user_chats() == []


def test_create_new_chat(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat_id = manager.create_new_chat(
        "Estoy desarrollando una aplicación con Python"
    )

    assert chat_id is not None

    chat = manager.get_chat_info(chat_id)

    assert chat is not None
    assert chat["chat_id"] == chat_id
    assert chat["title"] == "Python y LangGraph"
    assert chat["message_count"] == 0
    assert "created_at" in chat
    assert "updated_at" in chat


def test_get_user_chats_returns_chats_sorted_by_updated_at(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat1 = manager.create_new_chat()
    chat2 = manager.create_new_chat()

    chats = manager.get_user_chats()

    assert len(chats) == 2

    # El último creado debe aparecer primero
    assert chats[0]["chat_id"] == chat2
    assert chats[1]["chat_id"] == chat1


def test_update_chat_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat_id = manager.create_new_chat()

    manager.update_chat_metadata(
        chat_id,
        title="Mi proyecto",
        increment_messages=True
    )

    chat = manager.get_chat_info(chat_id)

    assert chat["title"] == "Mi proyecto"
    assert chat["message_count"] == 1
    assert "updated_at" in chat


def test_update_chat_metadata_multiple_messages(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat_id = manager.create_new_chat()

    manager.update_chat_metadata(
        chat_id,
        increment_messages=True
    )

    manager.update_chat_metadata(
        chat_id,
        increment_messages=True
    )

    chat = manager.get_chat_info(chat_id)

    assert chat["message_count"] == 2


def test_delete_chat(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat_id = manager.create_new_chat()

    assert manager.get_chat_info(chat_id) is not None

    result = manager.delete_chat(chat_id)

    assert result is True
    assert manager.get_chat_info(chat_id) is None


def test_get_chat_info_for_nonexistent_chat(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)

    manager = chat_manager.ChatManager("carlos")

    assert manager.get_chat_info("chat-inexistente") is None


def test_update_title_from_message(tmp_path, monkeypatch):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat_id = manager.create_new_chat()

    # create_new_chat() sin mensaje crea "Nuevo chat"
    chat = manager.get_chat_info(chat_id)
    assert chat["title"] == "Nuevo chat"

    manager.update_title_from_message(
        chat_id,
        "Estoy desarrollando una aplicación con Python"
    )

    chat = manager.get_chat_info(chat_id)

    assert chat["title"] == "Python y LangGraph"


def test_update_title_from_message_does_not_change_existing_title(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(chat_manager, "USERS_DIR", tmp_path)
    monkeypatch.setattr(
        chat_manager,
        "ChatOpenAI",
        lambda **kwargs: fake_llm()
    )

    manager = chat_manager.ChatManager("carlos")

    chat_id = manager.create_new_chat()

    manager.update_chat_metadata(
        chat_id,
        title="Mi proyecto"
    )

    manager.update_title_from_message(
        chat_id,
        "Este mensaje habla de Python"
    )

    chat = manager.get_chat_info(chat_id)

    assert chat["title"] == "Mi proyecto"
