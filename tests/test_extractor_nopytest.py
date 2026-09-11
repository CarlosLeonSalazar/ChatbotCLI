from memory.extractor import MemoryExtractor


def main():
    extractor = MemoryExtractor()

    messages = [
        "Me llamo Carlos y vivo en Madrid.",
        "Trabajo desarrollando aplicaciones con Python.",
        "Prefiero Python antes que Java.",
        "¿Qué tiempo hace hoy?",
    ]

    for message in messages:
        memory = extractor.extract(message)

        print(f"\nMensaje: {message}")
        print(f"Memoria: {memory}")


if __name__ == "__main__":
    main()
