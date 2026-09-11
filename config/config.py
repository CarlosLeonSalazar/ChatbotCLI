from pathlib import Path

# Configuración de directorios
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
USERS_DIR = BASE_DIR / "users"

# Creación de directorios
for _dir in (DATA_DIR, USERS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Configuración del modelo
DEFAULT_IA_MODEL = 'gpt-4o-mini'
DEFAULT_TEMPERATURE = 0.3
EMBEDDING_MODEL = 'text-embedding-3-large'

# Configuración memoria
MAX_VECTOR_RESULTS = 3  # para retriever
MEMORY_CATEGORIES = [
    'personal',
    'profesional',
    'preferencias',
    'hechos_importantes'
]

# Configuración UI -Streamilit
PAGE_TITLE = "Chat Multiusuario con Memoria Avanzada"
PAGE_ICON = '🤖'
