import chatbot.manager as chatbot_manager


class FakeChatbot:
    """Sustituto de ModernChatbot para el test."""

    def __init__(self, user_id):
        self.user_id = user_id


def test_get_chatbot_creates_instance(monkeypatch):
    monkeypatch.setattr(
        chatbot_manager,
        "ModernChatbot",
        FakeChatbot
    )

    chatbot_manager.ChatbotManager.clear_all()

    chatbot = chatbot_manager.ChatbotManager.get_chatbot("carlos")

    assert isinstance(chatbot, FakeChatbot)
    assert chatbot.user_id == "carlos"


def test_get_chatbot_returns_same_instance(monkeypatch):
    monkeypatch.setattr(
        chatbot_manager,
        "ModernChatbot",
        FakeChatbot
    )

    chatbot_manager.ChatbotManager.clear_all()

    chatbot1 = chatbot_manager.ChatbotManager.get_chatbot("carlos")
    chatbot2 = chatbot_manager.ChatbotManager.get_chatbot("carlos")

    assert chatbot1 is chatbot2


def test_different_users_have_different_instances(monkeypatch):
    monkeypatch.setattr(
        chatbot_manager,
        "ModernChatbot",
        FakeChatbot
    )

    chatbot_manager.ChatbotManager.clear_all()

    chatbot1 = chatbot_manager.ChatbotManager.get_chatbot("carlos")
    chatbot2 = chatbot_manager.ChatbotManager.get_chatbot("juan")

    assert chatbot1 is not chatbot2
    assert chatbot1.user_id == "carlos"
    assert chatbot2.user_id == "juan"


def test_remove_chatbot(monkeypatch):
    monkeypatch.setattr(
        chatbot_manager,
        "ModernChatbot",
        FakeChatbot
    )

    chatbot_manager.ChatbotManager.clear_all()

    chatbot_manager.ChatbotManager.get_chatbot("carlos")

    chatbot_manager.ChatbotManager.remove_chatbot("carlos")

    assert "carlos" not in chatbot_manager.ChatbotManager._instances


def test_clear_all(monkeypatch):
    monkeypatch.setattr(
        chatbot_manager,
        "ModernChatbot",
        FakeChatbot
    )

    chatbot_manager.ChatbotManager.clear_all()

    chatbot_manager.ChatbotManager.get_chatbot("carlos")
    chatbot_manager.ChatbotManager.get_chatbot("juan")

    chatbot_manager.ChatbotManager.clear_all()

    assert chatbot_manager.ChatbotManager._instances == {}
