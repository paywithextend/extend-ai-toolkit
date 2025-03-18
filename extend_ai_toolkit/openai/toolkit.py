from typing import List

from agents import FunctionTool
from pydantic import PrivateAttr

from extend_ai_toolkit.shared import Configuration, ExtendAgentToolkit, Agent
from .tool import OpenAITool


class ExtendOpenAIToolkit(ExtendAgentToolkit[FunctionTool, OpenAITool]):
    _tools: List[FunctionTool] = PrivateAttr(default=[])

    def __init__(
            self, api_key: str, api_secret: str, configuration: Configuration = Configuration.allTools()
    ):
        super().__init__(
            tool_class=OpenAITool,
            agent=Agent.OPENAI,
            api_key=api_key,
            api_secret=api_secret,
            configuration=configuration
        )
