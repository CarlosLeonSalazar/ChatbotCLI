# Pydantic
from pydantic import BaseModel, Field


# Modelo para salida estructurada de memoria
class ExtractedMemory(BaseModel):
    """Modelo para memoria extraida estructurada"""
    category: str = Field(
        description="Categoría: personal, profesional, preferencias, hechos importantes")
    content: str = Field(description="Contenido de la memoria")
    importance: int = Field(description="Importancia del 1 al 5", ge=1, le=5)
