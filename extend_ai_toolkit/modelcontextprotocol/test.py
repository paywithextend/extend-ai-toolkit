import os
import sys

from dotenv import load_dotenv

from extend_ai_toolkit.modelcontextprotocol.server import ExtendMCPServer
from extend_ai_toolkit.shared import Configuration

load_dotenv()

server = ExtendMCPServer(
    host=os.environ.get("API_HOST"),
    version=os.environ.get("API_VERSION"),
    api_key=os.environ.get("EXTEND_API_KEY"),
    api_secret=s.environ.get("EXTEND_API_SECRET"),
    configuration=Configuration(
        actions={
            "get_virtual_cards": {
                "read": True,
            },
            "create_virtual_cards": {
                "create": True,
            }
        }
    )
)

if __name__ == "__main__":
    try:
        server.run(transport='stdio')
    except Exception as e:
        sys.stderr.write(f"{str(e)}\n")
