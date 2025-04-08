import sys

from colorama import Fore
from dotenv import load_dotenv

from extend_ai_toolkit.modelcontextprotocol import ExtendMCPServer, Options
from extend_ai_toolkit.shared import Configuration
from extend_ai_toolkit.shared.configuration import VALID_SCOPES

load_dotenv()


def build_server():
    options = Options.from_args((sys.argv[1:]), VALID_SCOPES)
    selected_tools = options.tools
    configuration = Configuration.from_tool_str(selected_tools)

    return ExtendMCPServer(
        api_key=options.api_key,
        api_secret=options.api_secret,
        configuration=configuration
    )


def handle_error(error):
    sys.stderr.write(f"{Fore.YELLOW}   {str(error)}\n")


server = build_server()

if __name__ == "__main__":
    try:
        server.run(transport='stdio')
        print("Extend MCP server is running.")
    except Exception as e:
        handle_error(e)
