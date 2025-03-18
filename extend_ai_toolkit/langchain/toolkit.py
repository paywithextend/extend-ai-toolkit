from typing import List

from agents import FunctionTool
from pydantic import PrivateAttr

from extend_ai_toolkit.shared import Configuration, ExtendAgentToolkit, Agent
from .tool import LangChainTool


class ExtendLangChainToolkit(ExtendAgentToolkit[LangChainTool._Tool, LangChainTool]):
    _tools: List[FunctionTool] = PrivateAttr(default=[])

    def __init__(
            self, api_key: str, api_secret: str, configuration: Configuration = Configuration.allTools()
    ):
        super().__init__(
            tool_class=LangChainTool,
            agent=Agent.LANGCHAIN,
            api_key=api_key,
            api_secret=api_secret,
            configuration=configuration
        )
