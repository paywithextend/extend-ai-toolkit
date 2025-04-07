from typing import List, Optional
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool

from extend_ai_toolkit.shared import (
    AgentToolkit,
    Configuration,
    ExtendAPI,
    Tool
)
from .extend_tool import ExtendCrewAITool


class ExtendCrewAIToolkit(AgentToolkit[BaseTool]):
    """Toolkit for integrating Extend API with CrewAI."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        configuration: Optional[Configuration] = None
    ):
        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            configuration=configuration
        )
        self._llm = None

    def configure_llm(
        self,
        model: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> None:
        """Configure the LLM for use with agents.
        
        Args:
            model: The model identifier to use (e.g., 'gpt-4', 'claude-3-opus-20240229')
            api_key: Optional API key for the model provider
            **kwargs: Additional arguments to pass to the LLM constructor
        """
        self._llm = LLM(
            model=model,
            api_key=api_key,
            **kwargs
        )

    def tool_for_agent(self, api: ExtendAPI, tool: Tool) -> BaseTool:
        """Convert an Extend tool to a CrewAI tool."""
        return ExtendCrewAITool(api, tool)

    def create_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[BaseTool]] = None,
        verbose: bool = True
    ) -> Agent:
        """Create a CrewAI agent with Extend tools."""
        if tools is None:
            tools = self.get_tools()
        
        if self._llm is None:
            raise ValueError("No LLM configured. Call configure_llm() first.")
        
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            verbose=verbose,
            llm=self._llm
        )

    def create_task(
        self,
        description: str,
        agent: Agent,
        expected_output: Optional[str] = None,
        async_execution: bool = True
    ) -> Task:
        """Create a CrewAI task."""
        return Task(
            description=description,
            agent=agent,
            expected_output=expected_output,
            async_execution=async_execution
        )

    def create_crew(
        self,
        agents: List[Agent],
        tasks: List[Task],
        verbose: bool = True
    ) -> Crew:
        """Create a CrewAI crew with agents and tasks."""
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=verbose
        )
