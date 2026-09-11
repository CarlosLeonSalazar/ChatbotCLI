# Chat - Chatbot CLI con LangChain y LangGraph

Una aplicación de chatbot interactivo con interfaz de línea de comandos (TUI) construida con **Textual**, **LangChain**, **LangGraph** y **ChromaDB**. Soporta múltiples usuarios, gestión de conversaciones persistentes y un sistema avanzado de memoria.

## 📋 Requisitos

- **Python 3.13** (exactamente, versiones superiores pueden causar problemas con LangChain y LangGraph)
- **uv** (gestor de paquetes recomendado)
- **API Key de OpenAI** (para usar GPT-4o-mini)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd chat
```

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv .venv
```

**En Windows:**
```bash
.venv\Scripts\activate
```

**En macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias con uv (RECOMENDADO)

```bash
uv sync
```

**Alternativa con pip (no recomendado):**

```bash
pip install -e .
```

### 4. Configurar API Key de OpenAI

Crea un archivo `.env` en la raíz del proyecto:

```
OPENAI_API_KEY=tu_api_key_aqui
```

O configúralo como variable de entorno:

```bash
export OPENAI_API_KEY=tu_api_key_aqui
```

## 📱 Uso

### Ejecutar la aplicación CLI

Tras instalar correctamente el proyecto con `uv sync`, puedes ejecutar desde cualquier ubicación del sistema en cualquier terminal (PowerShell, cmd, Git Bash, bash, etc.):

```bash
chatbotcli
```

### Alternativas de ejecución

**Con uv desde el directorio del proyecto:**

```bash
uv run python -m ui.app
```

**Con servidor de Textual (requiere entorno virtual activado):**

```bash
textual server "python -m ui.app"
```

Esto inicia un servidor de desarrollo de Textual que permite inspeccionar la aplicación.

### Flujo de la aplicación

1. **LoginScreen**: Ingresa tu ID de usuario (se crea automáticamente si no existe)
2. **ChatListScreen**: Visualiza y gestiona tus conversaciones
3. **ChatScreen**: Interactúa con el chatbot en una conversación específica

### Características principales

- 💬 **Conversaciones multi-usuario**: Cada usuario tiene sus propios chats
- 🧠 **Sistema de memoria**: Extracción automática de información clave de las conversaciones
- 💾 **Persistencia**: Todas las conversaciones se guardan localmente en ChromaDB y SQLite
- 🔄 **Checkpoints**: Restauración de estado del chatbot usando LangGraph
- 🎯 **Contexto inteligente**: El chatbot recuerda información importante de conversaciones anteriores

## 📁 Estructura del Proyecto

```
chat/
├── ui/                          # Interfaz de usuario (Textual TUI)
│   ├── app.py                   # Aplicación principal
│   ├── app.tcss                 # Estilos CSS de Textual
│   ├── screens/                 # Pantallas de la interfaz
│   │   ├── login_screen.py      # Autenticación de usuario
│   │   ├── chat_list_screen.py  # Lista de conversaciones
│   │   └── chat_screen.py       # Pantalla de chat
│   └── widgets/                 # Componentes reutilizables
│       └── *.py                 # Widgets personalizados de Textual
│
├── chatbot/                     # Gestión de instancias de chatbot
│   ├── __init__.py
│   └── manager.py               # ChatbotManager (singleton por usuario)
│
├── graph/                       # Lógica del chatbot (LangGraph)
│   ├── __init__.py
│   ├── modern_chatbot.py        # Implementación del chatbot
│   └── state_graph.py           # Definición del grafo de estado
│
├── chat/                        # Gestión de conversaciones
│   ├── __init__.py
│   ├── manager.py               # ChatManager (CRUD de chats)
│   └── checkpointer.py          # Persistencia de checkpoints (SQLite)
│
├── memory/                      # Sistema de memoria
│   ├── __init__.py
│   ├── models.py                # Modelos de datos (MemoryBlock, etc.)
│   ├── store.py                 # Almacenamiento en ChromaDB
│   └── extractor.py             # Extracción de información del contexto
│
├── user/                        # Gestión de usuarios
│   ├── __init__.py
│   └── manager.py               # UserManager (CRUD de usuarios)
│
├── config/                      # Configuración
│   ├── __init__.py
│   └── config.py                # Variables de configuración central
│
├── tests/                       # Tests unitarios
│   ├── test_*.py                # Tests con pytest
│   └── test_*_nopytest.py       # Tests sin pytest (standalone)
│
├── pyproject.toml               # Configuración del proyecto Python
├── .python-version              # Versión de Python (3.13)
└── README.md                    # Este archivo
```

## 🧪 Testing

### Ejecutar todos los tests

**Con uv (recomendado):**

```bash
uv run pytest
```

**Con entorno virtual activado:**

```bash
pytest
```

### Ejecutar tests específicos

```bash
uv run pytest tests/test_memory.py
```

### Tests sin pytest (standalone)

Algunos tests pueden ejecutarse sin pytest:

```bash
uv run python tests/test_memory_nopytest.py
```

## 🔧 Desarrollo

### Estructura de dependencias

**Dependencias principales:**

- **langchain** ^1.3.14 - Framework de LLMs
- **langchain-openai** ^1.4.3 - Integración con OpenAI
- **langgraph** ^1.2.10 - Construcción de grafos de chatbot
- **langgraph-checkpoint-sqlite** ^3.1.1 - Persistencia de estado
- **chromadb** ^1.5.9 - Base de datos vectorial para memoria
- **textual** ^8.2.8 - Framework de TUI
- **streamlit** ^1.61.1 - (Opcional) Interfaz web alternativa
- **aiosqlite** ^0.22.1 - Base de datos SQLite asíncrona

**Dependencias de desarrollo:**

- **pytest** ^9.1.1 - Framework de testing
- **pytest-asyncio** ^1.4.0 - Soporte para tests asíncronos

### Puntos de entrada del proyecto

- **Una vez instalado ejecutar en terminal**: uv tool install --editable . Para poder usar comando global `chatbotcli`
- **Comando global (recomendado)**: `chatbotcli` - Funciona desde cualquier ubicación y terminal tras instalar correctamente
- **Con uv**: `uv run python -m ui.app` - Desde el directorio del proyecto
- **Punto de entrada instalado**: `chatbotcli = "ui.app:main"` (definido en `pyproject.toml`)

## Clonar el repositorio

- **Tener "uv" instalado** (Recomendado)
- `git clone <repositorio> chat`
- `uv sync`
- `uv tool install --editable .`
- Ejecutar comando `chatbotcli` desde cualquier ubicación en PowerShell, cmd, Bash, Git

## Activar y desactivar entorno virtual

- Windows: `.venv\Scripts\activate`
- Linux: `source .venv\bin\activate`

- Desactivar: `deactivate`

## 🗄️ Persistencia

El proyecto utiliza dos sistemas de persistencia:

1. **ChromaDB**: Almacena embeddings de memoria y contexto
2. **SQLite (aiosqlite)**: Almacena checkpoints del estado del chatbot

Los datos se guardan en directorios locales (generalmente en la raíz del proyecto o en directorios configurados en `config/config.py`).

## 🔐 Configuración

La configuración se centraliza en `config/config.py`. Puedes customizar:

- Ruta de base de datos ChromaDB
- Ruta de checkpoints SQLite
- Parámetros del modelo (temperatura, max_tokens, etc.)
- Claves de API

## 📝 Notas de desarrollo

### Ciclo de vida de la aplicación

1. `ChatApp` (en `ui.app`) inicia `LoginScreen`
2. `LoginScreen` valida/crea usuario vía `UserManager`
3. Se inicializa `ChatbotManager` y se carga el `ModernChatbot`
4. Se navega a `ChatListScreen` para gestionar conversaciones
5. Al salir, se cierran las conexiones de Checkpointer

### Async/await

El proyecto usa programación asíncrona. Asegúrate de:

- Usar `await` para operaciones de I/O
- Revisar la configuración en `pyproject.toml`: `asyncio_mode = "auto"`

## 🐛 Troubleshooting

### Errores de LangChain o LangGraph

Verifica que estés usando **Python 3.13 exactamente**. Versiones superiores pueden causar incompatibilidades.

```bash
python --version
```

### Error de conexión a ChromaDB

Asegúrate de que la ruta de base de datos existe y es escribible.

### Terminal rota después de salir

Esto sucede si no se cierran correctamente las conexiones. El código en `ui.app.on_unmount()` lo maneja automáticamente.

### API Key de OpenAI no encontrada

Verifica que la variable de entorno `OPENAI_API_KEY` esté configurada correctamente.

### Comando "chatbotcli" no encontrado

Asegúrate de que:
1. Instalaste el proyecto correctamente con `uv sync`
2. El entorno virtual está activado (si aplica)
3. Ejecutas desde cualquier terminal soportada (PowerShell, cmd, Git Bash, bash, etc.)

## 📄 Licencia

(Especificar licencia según corresponda)

## 👨‍💻 Autor

Carlos León Salazar

APP creada a partir de Curso de LangChain - LangGraph de Santiago Hernández

---

**¿Preguntas?** Revisa el código fuente o consulta la documentación en los comentarios del código.
