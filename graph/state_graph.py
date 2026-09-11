# Python
from typing import Annotated
from typing_extensions import TypedDict

# Langchain
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# LangGraph
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

# Modelo
from memory.models import ExtractedMemory

# Clases desde extractor y desde store
from memory.extractor import MemoryExtractor
from memory.store import MemoryStore


# Estado extendido que combina mensajes con memoria vectorial
class MemoryState(TypedDict, total=False):
    """Estado del grafo del chatbot"""
    messages: Annotated[list[BaseMessage], add_messages]
    vector_memories: list[str]  # memorias recuperadas de ChromaDB
    extracted_memory: ExtractedMemory | None  # memoria extraida del último mensaje


class MemoryGraph:
    """Clase donde se definen los nodos del grafo"""

    def __init__(self, extractor: MemoryExtractor, store: MemoryStore):
        self.extractor = extractor
        self.store = store

    # helper: función que recibe estado y devuelve último mensaje del usuario
    def _get_last_user_message(self, state: MemoryState) -> HumanMessage | None:
        """Devuelve el último mensaje del usuario"""
        for msg in reversed(state.get("messages", [])):
            if isinstance(msg, HumanMessage):
                return msg
        return None

    # PRIMER NODO: Función para nodo de recuperación de mensajes relevantes
    def memory_retrieval_node(self, state: MemoryState):
        """Recupera memorias relevantes para el último mensaje del usuario"""

        last_user_message = self._get_last_user_message(state)

        if last_user_message is None:
            return {"vector_memories": []}

        # Buscar memorias relevantes en ChromaDB
        # devuelve: list[tuple[Document, float]] (MemoryStore.search(query: str, k: int =5))
        results = self.store.search(
            query=last_user_message.content
        )

        return {"vector_memories": [
            document.page_content
            for document, score in results
        ]}

    # SEGUNDO NODO: Función qie extrae una memoria del último mensaje del usuario
    def memory_extraction_node(self, state: MemoryState):
        """Extrae una memoria del último mensaje del usuario."""

        last_user_message = self._get_last_user_message(state)

        if last_user_message is None:
            return {"extracted_memory": None}

        # Extraer la memoria
        extracted_memory = self.extractor.extract(
            last_user_message.content
        )

        return {
            "extracted_memory": extracted_memory
        }

    # TERCER NODO: Guarda la memoria si es relevante
    def memory_persistence_node(self, state: MemoryState):
        """Guarda en ChromaDB la memoria extraída si es relevante."""

        memory = state.get("extracted_memory")

        if memory is None:
            return {}

        if memory.category != "none" and memory.importance >= 2:
            self.store.save(memory)

        return {}

    # COMPILE: creamos los nodos, las aristas y compilamos
    # Este flujo solo se ejecuta en este archivo, no se ejecuta en la app.
    # El flujo completo se ejecuta y compila por ModernChatbot.
    def compile(self):

        # Instancia StateGraph
        workflow = StateGraph(MemoryState)

        # nodos
        workflow.add_node("memory_retrieval", self.memory_retrieval_node)
        workflow.add_node("memory_extraction", self.memory_extraction_node)
        workflow.add_node("memory_persistence", self.memory_persistence_node)

        # ejes o aristas
        workflow.add_edge(START, "memory_retrieval")
        workflow.add_edge("memory_retrieval", "memory_extraction")
        workflow.add_edge("memory_extraction", "memory_persistence")
        workflow.add_edge("memory_persistence", END)

        return workflow.compile()
