from langchain_core.documents import Document

import memory.store as store_module
from memory.models import ExtractedMemory


class FakeVectorStore:
    """Vector store simulado para los tests."""

    def __init__(self, *args, **kwargs):
        self.documents = {}

    def add_documents(self, documents, ids):
        for document_id, document in zip(ids, documents):
            self.documents[document_id] = document

    def similarity_search_with_score(self, query, k):
        documents = list(self.documents.values())[:k]

        return [
            (document, 0.1)
            for document in documents
        ]

    def delete(self, ids):
        for document_id in ids:
            self.documents.pop(document_id, None)

    def get(self):
        documents = list(self.documents.values())

        return {
            "documents": [
                document.page_content
                for document in documents
            ],
            "metadatas": [
                document.metadata
                for document in documents
            ]
        }


class FakeEmbeddings:
    """Embeddings simulados."""

    pass


def create_store(tmp_path, monkeypatch):
    """Crea un MemoryStore aislado para los tests."""

    monkeypatch.setattr(
        store_module,
        "USERS_DIR",
        tmp_path
    )

    monkeypatch.setattr(
        store_module,
        "OpenAIEmbeddings",
        lambda **kwargs: FakeEmbeddings()
    )

    monkeypatch.setattr(
        store_module,
        "Chroma",
        FakeVectorStore
    )

    return store_module.MemoryStore("carlos")


def test_memory_store_creates_user_directory(
    tmp_path,
    monkeypatch
):
    store = create_store(tmp_path, monkeypatch)

    user_dir = tmp_path / "carlos"

    assert user_dir.exists()
    assert user_dir.is_dir()


def test_save_memory(tmp_path, monkeypatch):
    store = create_store(tmp_path, monkeypatch)

    memory = ExtractedMemory(
        category="profesional",
        content="Trabajo desarrollando aplicaciones con Python",
        importance=4
    )

    memory_id = store.save(memory)

    assert memory_id is not None
    assert len(store.vectorstore.documents) == 1

    document = next(
        iter(store.vectorstore.documents.values())
    )

    assert document.page_content == (
        "Trabajo desarrollando aplicaciones con Python"
    )

    assert document.metadata["category"] == "profesional"
    assert document.metadata["importance"] == 4


def test_search_memory(tmp_path, monkeypatch):
    store = create_store(tmp_path, monkeypatch)

    memory = ExtractedMemory(
        category="preferencias",
        content="El usuario prefiere Python frente a Java",
        importance=3
    )

    store.save(memory)

    results = store.search(
        query="Python",
        k=5
    )

    assert len(results) == 1

    document, score = results[0]

    assert isinstance(document, Document)
    assert document.page_content == (
        "El usuario prefiere Python frente a Java"
    )
    assert score == 0.1


def test_delete_memory(tmp_path, monkeypatch):
    store = create_store(tmp_path, monkeypatch)

    memory = ExtractedMemory(
        category="personal",
        content="El usuario vive en Madrid",
        importance=4
    )

    memory_id = store.save(memory)

    assert len(store.vectorstore.documents) == 1

    store.delete(memory_id)

    assert len(store.vectorstore.documents) == 0


def test_get_all_memories(tmp_path, monkeypatch):
    store = create_store(tmp_path, monkeypatch)

    memory1 = ExtractedMemory(
        category="profesional",
        content="Trabajo desarrollando aplicaciones con Python",
        importance=4
    )

    memory2 = ExtractedMemory(
        category="preferencias",
        content="Prefiero Python frente a Java",
        importance=3
    )

    store.save(memory1)
    store.save(memory2)

    memories = store.get_all()

    assert len(memories) == 2

    contents = [
        memory.page_content
        for memory in memories
    ]

    assert (
        "Trabajo desarrollando aplicaciones con Python"
        in contents
    )

    assert (
        "Prefiero Python frente a Java"
        in contents
    )
