import uuid

import pytest
from langchain_core.messages import HumanMessage

from graph.modern_chatbot import ModernChatbot
from memory.models import ExtractedMemory


async def _close(chatbot: ModernChatbot) -> None:
    """Cierra las conexiones del checkpointer tras un test."""
    await chatbot.checkpointer.async_conn.close()
    chatbot.checkpointer.conn.close()


async def test_modern_chatbot_initialization():
    chatbot = ModernChatbot("test_user")

    assert chatbot.memory_graph is not None
    assert chatbot.memory_extractor is not None
    assert chatbot.memory_store is not None
    assert chatbot.graph is not None
    assert chatbot.graph_async is not None

    await _close(chatbot)


async def test_modern_chatbot_graph():
    chatbot = ModernChatbot("test_user")

    result = chatbot.graph.invoke({
        "messages": [
            HumanMessage(
                content="Estoy desarrollando una aplicación con Python y LangGraph"
            )
        ]
    }, config={
        "configurable": {
            "thread_id": "test_thread"
        }
    })

    assert result["messages"]
    assert isinstance(result["extracted_memory"], ExtractedMemory)

    await _close(chatbot)


async def test_get_conversation_history():
    chatbot = ModernChatbot("test_user")
    chat_id = f"history_test_{uuid.uuid4()}"

    chatbot.chat("Estoy trabajando con Python", chat_id=chat_id)
    chatbot.chat("También estoy trabajando con LangGraph", chat_id=chat_id)

    history = chatbot.get_conversation_history(chat_id=chat_id)

    assert history
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Estoy trabajando con Python"
    assert history[1]["role"] == "assistant"
    assert history[2]["role"] == "user"
    assert history[2]["content"] == "También estoy trabajando con LangGraph"
    assert history[3]["role"] == "assistant"

    await _close(chatbot)


async def test_get_conversation_history_limit():
    chatbot = ModernChatbot("test_user")
    chat_id = f"history_test_{uuid.uuid4()}"

    chatbot.chat("Primer mensaje", chat_id=chat_id)
    chatbot.chat("Segundo mensaje", chat_id=chat_id)

    history = chatbot.get_conversation_history(chat_id=chat_id, limit=2)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Segundo mensaje"
    assert history[1]["role"] == "assistant"

    await _close(chatbot)


async def test_get_conversation_history_empty():
    chatbot = ModernChatbot("test_user")

    history = chatbot.get_conversation_history(chat_id="non_existing_chat")

    assert history == []

    await _close(chatbot)


async def test_clear_conversation():
    chatbot = ModernChatbot("test_user4")
    chat_id = f"history_test_{uuid.uuid4()}"

    chatbot.chat("Estoy trabajando con Python", chat_id=chat_id)

    history = chatbot.get_conversation_history(chat_id)
    assert history

    result = chatbot.clear_conversation(chat_id)
    assert result is True

    history = chatbot.get_conversation_history(chat_id)
    assert history == []

    await _close(chatbot)


async def test_delete_chat_from_langgraph():
    chatbot = ModernChatbot("test_user")
    chat_id = f"history_test_{uuid.uuid4()}"

    chatbot.chat("Estoy probando la eliminación de un chat", chat_id=chat_id)

    history = chatbot.get_conversation_history(chat_id)
    assert history

    result = chatbot.delete_chat_from_langgraph(chat_id)
    assert result is True

    history = chatbot.get_conversation_history(chat_id)
    assert history == []

    await _close(chatbot)


async def test_delete_chat():
    chatbot = ModernChatbot("test_user")

    chat_id = chatbot.chatmanager.create_new_chat("Chat que vamos a eliminar")

    chatbot.chat("Este chat será eliminado", chat_id=chat_id)

    assert chatbot.chatmanager.get_chat_info(chat_id) is not None
    assert chatbot.get_conversation_history(chat_id)

    result = chatbot.delete_chat(chat_id)
    assert result is True

    assert chatbot.chatmanager.get_chat_info(chat_id) is None
    assert chatbot.get_conversation_history(chat_id) == []

    await _close(chatbot)


# --- Tests nuevos para astream_events / graph_async ---

async def test_astream_events_produces_response():
    chatbot = ModernChatbot("test_user")
    chat_id = f"astream_test_{uuid.uuid4()}"

    events = []
    async for event in chatbot.astream_events(
        "Estoy probando el streaming del chatbot", chat_id=chat_id
    ):
        events.append(event)

    stream_events = [e for e in events if e["event"] == "on_chat_model_stream"]
    assert len(stream_events) > 0

    full_response = "".join(
        e["data"]["chunk"].content
        for e in stream_events
        if e["data"]["chunk"].content
    )
    assert len(full_response) > 0
    assert not any(e["event"] == "on_astream_error" for e in events)

    await _close(chatbot)


async def test_astream_events_shares_thread_id_with_chat():
    chatbot = ModernChatbot("test_user")
    chat_id = f"astream_shared_{uuid.uuid4()}"

    async for _ in chatbot.astream_events("Primer mensaje async", chat_id=chat_id):
        pass

    history = chatbot.get_conversation_history(chat_id=chat_id)

    assert history
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Primer mensaje async"

    await _close(chatbot)
