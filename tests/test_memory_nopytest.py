from memory.store import MemoryStore
from memory.models import ExtractedMemory


def main():
    user_id = 'test_user'

    store = MemoryStore('test_delete')

    memory = ExtractedMemory(
        category="preferencias",
        content="El usuario prefiere Python frente a Java",
        importance=3
    )

    # Guardar
    memory_id = store.save(memory)

    print("Memoria guardada")
    print(memory_id)

    # Buscar
    results = store.search('Qué lenguaje de programación prefiere')

    print('\nResultados de la búsqueda:')
    for document, score in results:
        print('Contenido:', document.page_content)
        print('Metadata:', document.metadata)
        print('Score:', score)

    # Obtener todas
    memories = store.get_all()

    print('\nTodas las memorias:')
    for memory in memories:
        print(memory)


if __name__ == '__main__':
    main()
