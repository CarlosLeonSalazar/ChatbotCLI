# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Módulo config
from config.config import DEFAULT_IA_MODEL

# Model
from .models import ExtractedMemory


# Clase para inicializar el sistema de extracción de memoria transversal
class MemoryExtractor:
    """Clase para inicializar el sistema de extracción de memoria transversal"""

    def __init__(self):
        self.llm = ChatOpenAI(model=DEFAULT_IA_MODEL, temperature=0)

        self._init_extraction_system()

    def _init_extraction_system(self):
        """Inicializa el sistema inteligente de extracción de memoria transversal"""

        try:
            self.structured_llm = self.llm.with_structured_output(
                ExtractedMemory)

            self.extraction_template = PromptTemplate(
                template="""Analiza el siguiente mensaje del usuario y determina si contiene información importante que deba recordarse.
    
                    Categorías disponibles:
                    - personal: Nombre, edad, ubicación, familia, etc.
                    - profesional: Trabajo, empresa, proyectos, habilidades
                    - preferencias: Gustos, disgustos, preferencias personales
                    - hechos_importantes: Información relevante que debe recordarse
                    - none: No contiene información relevante para recordar 
    
                    Mensaje del usuario: 
                    {user_message}
    
                    Si el mensaje contiene información importante, extrae UNA memoria, la más importante.
                    Si no contiene información relevante para recordar, responde con categoría "none".
                    """,
                input_variables=["user_message"]
            )

            self.extraction_chain = self.extraction_template | self.structured_llm

        except Exception as e:
            print(f'Error inicializando el sistema de extracción: {e}')
            self.extraction_chain = None

    def extract(self, user_message: str) -> ExtractedMemory:
        """Extrae una memoria estructurada del mensaje"""

        return self.extraction_chain.invoke(
            {
                "user_message": user_message
            }
        )
