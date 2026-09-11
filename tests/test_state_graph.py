from graph.state_graph import MemoryGraph
from memory.store import MemoryStore
from memory.extractor import MemoryExtractor
from langchain_core.messages import HumanMessage


def test_memory_graph():

    user_id = "test_user3"

    extractor = MemoryExtractor()
    store = MemoryStore(user_id)

    memory_graph = MemoryGraph(
        extractor=extractor,
        store=store
    )

    graph = memory_graph.compile()

    state = {
        "messages": [
            HumanMessage(
                content="Me llamo Carlos y estoy trabajando en un chat con LangChain y LangGraph"
            )
        ]
    }

    result = graph.invoke(state)

    print(result)
