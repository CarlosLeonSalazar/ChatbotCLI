# Python
import sqlite3

# Desde módulos app
from graph.state_graph import MemoryGraph, MemoryState
from memory.extractor import MemoryExtractor
from memory.store import MemoryStore
from config.config import DEFAULT_IA_MODEL, DEFAULT_TEMPERATURE
from chat.manager import ChatManager
from chat.checkpointer import Checkpointer

# LangChain
from langchain_core.messages import HumanMessage, AIMessage, trim_messages, RemoveMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver


class ModernChatbot:

    def __init__(self, user_id: str):
        self.user_id = user_id

        self.memory_extractor = MemoryExtractor()
        self.memory_store = MemoryStore(user_id)

        self.memory_graph = MemoryGraph(
            extractor=self.memory_extractor,
            store=self.memory_store
        )

        self.llm = ChatOpenAI(
            model=DEFAULT_IA_MODEL,
            temperature=DEFAULT_TEMPERATURE
        )

        # Template del sistema con contexto dinamico
        self.system_template = """Eres un asistente personal inteligente y amigable.

        Características de tu personalidad:
        - Eres útil, empático y conversacional
        - Recuerdas información importante de conversaciones anteriores
        - Adaptas tu estilo a las preferencias del usuario
        - Eres proactivo ofreciendo sugerencias relevantes
        - Mantienes un tono profesional pero cercano

        {context}

        Usa esta información para personalizar tus respuestas, pero no menciones explícitamente que tienes memoria a menos que sea relevante para la conversación."""

       # Configurar el trimming de mensajes para gestion del contexto
        self.message_trimmer = trim_messages(
            strategy="last",
            max_tokens=4000,
            token_counter=self.llm,
            start_on="human",
            include_system=True
        )

        self.chatmanager = ChatManager(user_id)
        self.checkpointer = Checkpointer(user_id)

        # Crear aplicacion de LangGraph
        self.graph = self._create_app()

    def _create_app(self):
        """Crea la aplicación de LangGraph"""

        workflow = StateGraph(state_schema=MemoryState)

        def context_optimization_node(state):
            """Nodo que optimiza el contexto usando trim_messages."""
            messages = state['messages']

            # Aplicar trimming inteligente
            trimmed_messages = self.message_trimmer.invoke(messages)

            return {"messages": trimmed_messages}

        def response_generation_node(state):
            """Nodo que genera la respuesta usando el contexto optimizado."""
            messages = state['messages']
            vector_memories = state.get('vector_memories', [])

            if not messages:
                return {"messages": []}

            # Construir contexto con memorias vectoriales
            if vector_memories:
                context_parts = [
                    "Informacion relevante que recuerdas del usuario:"]
                for memory in vector_memories:
                    context_parts.append(f"- {memory}")
                context = "\n".join(context_parts)
            else:
                context = "No hay informacion previa relevante disponible."

            # Crear el prompt con el contexto dinamico
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_template.format(context=context)),
                MessagesPlaceholder(variable_name="messages")
            ])

            # Generar la respuesta
            chain = prompt | self.llm
            response = chain.invoke({"messages": messages})

            return {"messages": response}

        # NODOS
        # Nodos de ModenrChatbot
        workflow.add_node("context_optimization",
                          context_optimization_node)
        workflow.add_node("response_generation",
                          response_generation_node)

        # Nodos de Memoria en state_graph.py
        workflow.add_node("memory_retrieval",
                          self.memory_graph.memory_retrieval_node)
        workflow.add_node("memory_extraction",
                          self.memory_graph.memory_extraction_node)
        workflow.add_node("memory_persistence",
                          self.memory_graph.memory_persistence_node)

        # EJES
        workflow.add_edge(START, "memory_retrieval")

        workflow.add_edge(
            "memory_retrieval",
            "context_optimization"
        )

        workflow.add_edge(
            "context_optimization",
            "response_generation"
        )

        workflow.add_edge(
            "response_generation",
            "memory_extraction"
        )

        workflow.add_edge(
            "memory_extraction",
            "memory_persistence"
        )

        workflow.add_edge(
            "memory_persistence",
            END
        )

        self.graph_async = workflow.compile(
            checkpointer=self.checkpointer.async_saver
        )

        return workflow.compile(
            checkpointer=self.checkpointer.saver
        )

    # Helper que reconstruye el "thread_id"

    def _get_thread_id(self, chat_id: str) -> str:
        """Construye el identificador de thread de LangGraph"""
        return f"user_{self.user_id}_chat_{chat_id}"

    # Método que orquesta una interacción completa:
    # recibe el mensaje, determina el thread_id, invoca el grafo y devuelve la respuesta.

    def chat(self, message: str, chat_id: str = "default"):
        """Envía un mensaje y obtiene respuesta del chatbot"""

        try:
            # Identifica de forma única la conversación en LangGraph
            thread_id = self._get_thread_id(chat_id)

            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            # Aqui ya obtiene chat_info, comprueba si None y si title es "Nuevo chat"
            # genera el title y lo actualiza
            self.chatmanager.update_title_from_message(chat_id, message)

            # Invocar el chatbot con el nuevo mensaje
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=message)]},
                config=config
            )

            # Extraer respuesta
            assistant_response = result["messages"][-1].content

            return {
                "success": True,
                "response": assistant_response,
                "error": None,
                "memories_used": len(result.get("vector_memories", [])),
                "context_optimized": True
            }

        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e),
                "memories_used": 0,
                "context_optimized": False
            }

    async def astream_events(self, text: str, chat_id: str = "default"):
        """Envía un mensaje y transmite (streaming) los eventos del grafo.

        Replica el mismo efecto colateral que chat() -- actualizar el título
        del chat a partir del primer mensaje -- para que un chat creado vía
        streaming no se quede indefinidamente con el título "Nuevo chat".
        """
        thread_id = self._get_thread_id(chat_id)
        config = {"configurable": {"thread_id": thread_id}}

        # Mismo efecto colateral que en chat(): genera/actualiza el título
        # la primera vez que el chat recibe un mensaje.
        self.chatmanager.update_title_from_message(chat_id, text)

        try:
            async for event in self.graph_async.astream_events(
                {"messages": [("user", text)]}, config=config, version="v2"
            ):
                yield event
        except Exception as e:
            # Igual que chat(), no relanzamos la excepción cruda hacia la UI:
            # emitimos un evento sintético que la UI ya sabe reconocer y mostrar
            # como error, en vez de romper el streaming a medias sin explicación.
            yield {
                "event": "on_astream_error",
                "data": {"error": str(e)},
            }

    # Método para obtener el historial de conversaciones de un chat

    def get_conversation_history(self, chat_id: str = "default", limit: int = 50):
        """Obtiene historial de conversaciones de un chat"""

        try:
            # Identifica de forma única la conversación en LangGraph
            thread_id = self._get_thread_id(chat_id)

            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            # Obtiene el estado del grafo
            state = self.graph.get_state(config)

            if not state.values or "messages" not in state.values:
                return []

            messages = state.values["messages"]

            history = []

            for message in messages[-limit:]:
                if isinstance(message, HumanMessage):
                    history.append(
                        {
                            "role": "user",
                            "content": message.content
                        }
                    )
                elif isinstance(message, AIMessage):
                    history.append(
                        {
                            "role": "assistant",
                            "content": message.content
                        }
                    )

            return history

        except Exception as e:
            print(f"Error obteniendo el historial: {e}")
            return []

    def clear_conversation(self, chat_id: str = "default") -> bool:
        """Limpia el historial de conversación de un chat."""

        try:
            thread_id = self._get_thread_id(chat_id)

            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            state = self.graph.get_state(config)

            messages = state.values.get("messages", [])

            if not messages:
                return True

            self.graph.update_state(
                config,
                {
                    "messages": [
                        RemoveMessage(id=message.id)
                        for message in messages
                    ]
                })

            return True

        except Exception as e:
            print(f"Error limpiando conversación: {e}")
            return False

    def delete_chat_from_langgraph(self, chat_id: str) -> bool:
        """Elimina el estado persistido de un chat en LangGraph."""

        try:
            thread_id = self._get_thread_id(chat_id)

            self.checkpointer.saver.delete_thread(thread_id)

            return True

        except Exception as e:
            print(f"Error eliminando chat de LangGraph: {e}")
            return False

    def delete_chat(self, chat_id: str) -> bool:
        """Elimina completamente un chat, tanto los metadatos (json) como langgraph.db
        y es este método el que interactúa con la UI"""

        try:
            if self.chatmanager.get_chat_info(chat_id) is None:
                return False

            if not self.delete_chat_from_langgraph(chat_id):
                return False

            if not self.chatmanager.delete_chat(chat_id):
                return False

            return True

        except Exception as e:
            print(f"Error eliminando chat: {e}")
            return False
