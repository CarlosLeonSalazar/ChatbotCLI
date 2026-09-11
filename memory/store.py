# Python
import uuid

# LangChain
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# módulos propios
from .models import ExtractedMemory
from config.config import EMBEDDING_MODEL, USERS_DIR


class MemoryStore:
    """Clase que maneja el almacenamiento en memoria vectorial"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.user_dir = USERS_DIR / user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)

        # Base de datos Vectorial ChromaDB para memoria transversal
        self.chroma_path = self.user_dir / "chromadb"

        # Función para inicializar db vectorial
        self._init_vector_db()

    def _init_vector_db(self):
        """Inicializa la base de datos vectorial chromadb"""
        try:
            self.vectorstore = Chroma(
                collection_name=f'memoria_{self.user_id}',
                embedding_function=self.embedding,
                persist_directory=self.chroma_path
            )

        except Exception as e:
            print(f"Error inicializando Chromadb: {e}")
            self.vectorstore = None

    def save(self, memory: ExtractedMemory):
        """Transforma lo extraido por extract de MemortExtractor en obj Document"""
        memory_id = str(uuid.uuid4())

        document = Document(
            page_content=memory.content,
            metadata={
                "category": memory.category,
                "importance": memory.importance
            }
        )

        self.vectorstore.add_documents([document], ids=[memory_id])

        return memory_id

    def search(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k
        )

    def delete(self, memory_id: str):
        self.vectorstore.delete(
            ids=[memory_id]
        )

    def get_all(self) -> list[Document]:
        result = self.vectorstore.get()

        return [Document(
            page_content=content,
            metadata=metadata
        )
            for content, metadata in zip(
            result["documents"],
            result["metadatas"]
        )
        ]
