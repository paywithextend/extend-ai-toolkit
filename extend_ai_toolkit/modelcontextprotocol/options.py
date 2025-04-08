import os


def validate_options(cls):
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # Perform validation after initialization
        if not self.api_key:
            raise ValueError(
                'Extend API key not provided. Please either pass it as an argument --api-key=$KEY or set the EXTEND_API_KEY environment variable.'
            )
        elif not self.api_key.startswith("apik_"):
            raise ValueError('Extend API key must start with "apik_".')

        if not self.api_secret:
            raise ValueError(
                'Extend API key not provided. Please either pass it as an argument --api-key=$KEY or set the EXTEND_API_SECRET environment variable.'
            )

        if not self.tools:
            raise ValueError('The --tools argument must be provided.')

    cls.__init__ = new_init
    return cls


@validate_options
class Options:
    ACCEPTED_ARGS = ['api-key', 'api-secret', 'tools']

    def __init__(self, tools, api_key, api_secret):
        self.tools = tools
        self.api_key = api_key
        self.api_secret = api_secret

    @staticmethod
    def from_args(args: list[str], valid_tools: list[str]) -> "Options":
        tools = ""
        api_key = None
        api_secret = None

        for arg in args:
            if arg.startswith("--"):
                arg_body = arg[2:]
                if "=" not in arg_body:
                    raise ValueError(f"Argument {arg} is not in --key=value format.")
                key, value = arg_body.split("=", 1)
                match key:
                    case "tools":
                        tools = value
                    case "api-key":
                        api_key = value
                    case "api-secret":
                        api_secret = value
                    case _:
                        raise ValueError(
                            f"Invalid argument: {key}. Accepted arguments are: {', '.join(Options.ACCEPTED_ARGS)}"
                        )

        for tool in tools.split(","):
            if tool.strip() == "all":
                continue
            if tool.strip() not in valid_tools:
                raise ValueError(
                    f"Invalid tool: {tool}. Accepted tools are: {', '.join(valid_tools)}"
                )

        api_key = api_key or os.environ.get("EXTEND_API_KEY")
        api_secret = api_secret or os.environ.get("EXTEND_API_SECRET")

        return Options(tools, api_key, api_secret)
