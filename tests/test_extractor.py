import memory.extractor as extractor_module

from memory.extractor import MemoryExtractor
from memory.models import ExtractedMemory

from langchain_core.runnables import RunnableLambda


class FakeLLM:

    def __init__(self, result):
        self.result = result

    def with_structured_output(self, schema):
        return RunnableLambda(
            lambda _: self.result
        )

# PRIMER TEST


def test_extract_personal_memory(monkeypatch):
    expected = ExtractedMemory(
        category="personal",
        content="El usuario se llama Carlos",
        importance=5
    )

    monkeypatch.setattr(
        extractor_module,
        "ChatOpenAI",
        lambda **kwargs: FakeLLM(expected)
    )

    extractor = MemoryExtractor()

    result = extractor.extract("Me llamo Carlos.")

    assert isinstance(result, ExtractedMemory)
    assert result.category == "personal"
    assert result.content == "El usuario se llama Carlos"
    assert result.importance == 5


# SEGUNDO TEST - probar "none"

def test_extract_none_memory(monkeypatch):
    expected = ExtractedMemory(
        category="none",
        content="",
        importance=1
    )

    monkeypatch.setattr(
        extractor_module,
        "ChatOpenAI",
        lambda **kwargs: FakeLLM(expected)
    )

    extractor = MemoryExtractor()

    result = extractor.extract("¿Qué tiempo hace hoy?")

    assert isinstance(result, ExtractedMemory)
    assert result.category == "none"
    assert result.importance == 1


# TERCER TEST - probar "preferencias"

def test_extract_preference_memory(monkeypatch):
    expected = ExtractedMemory(
        category="preferencias",
        content="El usuario prefiere Python frente a Java",
        importance=3
    )

    monkeypatch.setattr(
        extractor_module,
        "ChatOpenAI",
        lambda **kwargs: FakeLLM(expected)
    )

    extractor = MemoryExtractor()

    result = extractor.extract("Prefiero Python antes que Java.")

    assert result.category == "preferencias"
    assert result.content == "El usuario prefiere Python frente a Java"
    assert result.importance == 3
