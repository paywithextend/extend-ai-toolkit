import os
import sys

from colorama import Fore
from dotenv import load_dotenv

from extend_ai_toolkit.modelcontextprotocol.server import ExtendMCPServer
from extend_ai_toolkit.shared import Configuration

load_dotenv()

ACCEPTED_ARGS = ['api-key', 'api-secret', 'tools']
ACCEPTED_TOOLS = [
    'test.create',
    'virtual_cards.create',
    'virtual_cards.update',
    'virtual_cards.read',
    'credit_cards.read',
    'transactions.read',
]


class Options:
    def __init__(self, tools=None, api_key=None, api_secret=None):
        self.tools = tools
        self.api_key = api_key
        self.api_secret = api_secret


def parse_args(args):
    """
    Parses command-line arguments in the format --key=value.
    Valid keys are 'tools', 'api-key', and 'stripe-account'.
    """
    options = Options()
    for arg in args:
        if arg.startswith("--"):
            # Remove the leading '--' and split on '='
            arg_body = arg[2:]
            if "=" not in arg_body:
                raise ValueError(f"Argument {arg} is not in --key=value format.")
            key, value = arg_body.split("=", 1)
            if key == "tools":
                options.tools = value.split(",")
            elif key == "api-key":
                if not value.startswith("apik_"):
                    raise ValueError('API key must start with "apik_".')
                options.api_key = value
            elif key == "api-secret":
                options.api_secret = value
            else:
                raise ValueError(
                    f"Invalid argument: {key}. Accepted arguments are: {', '.join(ACCEPTED_ARGS)}"
                )
    if not options.tools:
        raise ValueError('The --tools argument must be provided.')

    for tool in options.tools:
        if tool.strip() == "all":
            continue
        if tool.strip() not in ACCEPTED_TOOLS:
            raise ValueError(
                f"Invalid tool: {tool}. Accepted tools are: {', '.join(ACCEPTED_TOOLS)}"
            )

    api_key = options.api_key or os.environ.get("EXTEND_API_KEY")
    if not api_key:
        raise ValueError(
            'Extend API key not provided. Please either pass it as an argument --api-key=$KEY or set the EXTEND_API_KEY environment variable.'
        )
    options.api_key = api_key

    api_secret = options.api_secret or os.environ.get("EXTEND_API_SECRET")
    if not api_secret:
        raise ValueError(
            'Stripe API key not provided. Please either pass it as an argument --api-key=$KEY or set the EXTEND_API_SECRET environment variable.'
        )
    options.api_secret = api_secret

    return options


def handle_error(error):
    """
    Outputs error messages using colored text.
    """
    sys.stderr.write(f"\n{Fore.RED}🚨  Error initializing Extend MCP server:\n")
    sys.stderr.write(f"{Fore.YELLOW}   {str(error)}\n")


def build_server():
    options = parse_args(sys.argv[1:])
    selected_tools = options.tools
    configuration = Configuration(actions={})

    if "all" in selected_tools:
        for tool in ACCEPTED_TOOLS:
            product, action = tool.split(".")
            if product in configuration.actions:
                configuration.actions[product][action] = True
            else:
                configuration.actions[product] = {action: True}
    else:
        for tool in selected_tools:
            product, action = tool.split(".")
            configuration.actions[product] = {action: True}

    host = os.getenv("API_HOST")
    version = os.getenv("API_VERSION")

    return ExtendMCPServer(
        host=host,
        version=version,
        api_key=options.api_key,
        api_secret=options.api_secret,
        configuration=configuration
    )


server = build_server()

if __name__ == "__main__":
    try:
        server.run(transport='stdio')
        print("Extend MCP server is running.")
    except Exception as e:
        handle_error(e)
