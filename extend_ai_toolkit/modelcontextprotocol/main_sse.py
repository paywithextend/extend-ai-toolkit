"""The unauthenticated SSE service has been retired."""


def main():
    raise SystemExit(
        "Unauthenticated SSE is disabled. Use python -m extend_ai_toolkit.modelcontextprotocol.main with local stdio. Remote hosting requires a separately reviewed authenticated service."
    )


if __name__ == "__main__":
    main()
