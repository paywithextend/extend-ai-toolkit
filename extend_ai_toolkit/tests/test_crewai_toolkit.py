import inspect
import json
import re
from unittest.mock import patch, Mock, AsyncMock

import pytest
from pydantic import BaseModel
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool

from extend_ai_toolkit.crewai.toolkit import ExtendCrewAIToolkit
from extend_ai_toolkit.shared import Configuration, ExtendAPITools, Tool, ExtendAPI


# Define schema classes needed for testing
class VirtualCardsSchema(BaseModel):
    page: int = 0
    per_page: int = 10


class VirtualCardDetailSchema(BaseModel):
    virtual_card_id: str = "test_id"


@pytest.fixture
def mock_extend_api():
    """Fixture that provides a mocked ExtendAPI instance"""
    with patch('extend_ai_toolkit.shared.agent_toolkit.ExtendAPI') as mock_api_class:
        mock_api_instance = Mock(spec=ExtendAPI)
        mock_api_instance.run = AsyncMock()
        mock_api_class.return_value = mock_api_instance
        yield mock_api_class, mock_api_instance


@pytest.fixture
def mock_configuration():
    """Fixture that provides a mocked Configuration instance with controlled tool permissions"""
    mock_config = Mock(spec=Configuration)

    # Create a list of allowed tools for testing
    allowed_tools = [
        Tool(
            name="Get Virtual Cards",
            method=ExtendAPITools.GET_VIRTUAL_CARDS,
            description="Get all virtual cards",
            args_schema=VirtualCardsSchema,
            required_scope=[]
        ),
        Tool(
            name="Get Virtual Card Details",
            method=ExtendAPITools.GET_VIRTUAL_CARD_DETAIL,
            description="Get details of a virtual card",
            args_schema=VirtualCardDetailSchema,
            required_scope=[]
        )
    ]

    # Configure the mock to return our controlled list of tools
    mock_config.allowed_tools.return_value = allowed_tools

    # Add org_id property
    mock_config.org_id = "test_org_id"

    return mock_config


@pytest.fixture
def toolkit(mock_extend_api, mock_configuration):
    """Fixture that creates an ExtendCrewAIToolkit instance with mocks"""
    mock_api_class, mock_api_instance = mock_extend_api
    toolkit = ExtendCrewAIToolkit(
        org_id="test_org_id",
        api_key="test_api_key",
        api_secret="test_api_secret",
        configuration=mock_configuration
    )
    return toolkit


def test_init_creates_extend_api(toolkit, mock_extend_api):
    """Test that ExtendAPI is initialized with correct credentials"""
    mock_api_class, _ = mock_extend_api
    mock_api_class.assert_called_once_with(
        org_id="test_org_id",
        api_key="test_api_key",
        api_secret="test_api_secret"
    )


def test_get_tools_returns_correct_tools(toolkit, mock_configuration):
    """Test that get_tools returns the correct set of tools"""
    tools = toolkit.get_tools()
    
    # We configured mock_configuration to return 2 tools
    assert len(tools) == 2

    # Verify tool details
    assert tools[0].name == ExtendAPITools.GET_VIRTUAL_CARDS.value
    assert "Tool Name: get_virtual_cards" in tools[0].description
    assert "Tool Description: Get all virtual cards" in tools[0].description
    assert tools[1].name == ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value
    assert "Tool Name: get_virtual_card_detail" in tools[1].description
    assert "Tool Description: Get details of a virtual card" in tools[1].description


@pytest.mark.asyncio
async def test_tool_execution_forwards_to_api(toolkit, mock_extend_api):
    """Test that tool execution correctly forwards requests to the API"""
    # Get the first tool
    tool = toolkit.get_tools()[0]

    # Set up a return value for the API call
    _, mock_api_instance = mock_extend_api
    mock_response = {"status": "success", "data": [{"id": "123"}]}
    mock_api_instance.run.return_value = mock_response

    # Call the tool
    result = await tool._arun(page=0, per_page=10)

    # Verify API was called correctly
    mock_api_instance.run.assert_called_once_with(
        ExtendAPITools.GET_VIRTUAL_CARDS.value,
        page=0,
        per_page=10
    )

    # Verify the result matches the mock response
    assert result == mock_response


def test_tool_sync_execution_works(toolkit, mock_extend_api):
    """Test that synchronous tool execution works by creating an event loop"""
    # Get the first tool
    tool = toolkit.get_tools()[0]

    # Set up a return value for the API call
    _, mock_api_instance = mock_extend_api
    mock_response = {"status": "success", "data": [{"id": "123"}]}
    mock_api_instance.run.return_value = mock_response

    # Call the tool synchronously
    result = tool._run(page=0, per_page=10)

    # Verify API was called correctly
    mock_api_instance.run.assert_called_once_with(
        ExtendAPITools.GET_VIRTUAL_CARDS.value,
        page=0,
        per_page=10
    )

    # Verify the result matches the mock response
    assert result == mock_response


def test_tool_schema_matches_expected(toolkit):
    """Test that the tool has the correct schema"""
    # Get the first tool
    tool = toolkit.get_tools()[0]

    # Verify the tool has the correct schema class
    assert tool.args_schema == VirtualCardsSchema


def test_configure_llm(toolkit):
    """Test that LLM configuration works correctly"""
    toolkit.configure_llm(
        model="test-model",
        api_key="test-api-key",
        temperature=0.7
    )
    
    assert toolkit._llm is not None
    assert isinstance(toolkit._llm, LLM)
    assert toolkit._llm.model == "test-model"
    assert toolkit._llm.api_key == "test-api-key"
    assert toolkit._llm.temperature == 0.7


def test_create_agent_requires_llm(toolkit):
    """Test that creating an agent without configuring LLM raises an error"""
    with pytest.raises(ValueError, match=re.escape("No LLM configured. Call configure_llm() first.")):
        toolkit.create_agent(
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory"
        )


def test_create_agent_with_llm(toolkit):
    """Test that agent creation works correctly with configured LLM"""
    toolkit.configure_llm(model="test-model", api_key="test-api-key")
    
    agent = toolkit.create_agent(
        role="Test Role",
        goal="Test Goal",
        backstory="Test Backstory",
        verbose=True
    )
    
    assert isinstance(agent, Agent)
    assert agent.role == "Test Role"
    assert agent.goal == "Test Goal"
    assert agent.backstory == "Test Backstory"
    assert agent.verbose is True
    assert len(agent.tools) == 2  # From our mock configuration


def test_create_task(toolkit):
    """Test that task creation works correctly"""
    toolkit.configure_llm(model="test-model", api_key="test-api-key")
    agent = toolkit.create_agent(
        role="Test Role",
        goal="Test Goal",
        backstory="Test Backstory"
    )
    
    task = toolkit.create_task(
        description="Test Description",
        agent=agent,
        expected_output="Test Output",
        async_execution=True
    )
    
    assert isinstance(task, Task)
    assert task.description == "Test Description"
    assert task.agent == agent
    assert task.expected_output == "Test Output"
    assert task.async_execution is True


def test_create_crew(toolkit):
    """Test that crew creation works correctly"""
    toolkit.configure_llm(model="test-model", api_key="test-api-key")
    agent = toolkit.create_agent(
        role="Test Role",
        goal="Test Goal",
        backstory="Test Backstory"
    )
    task = toolkit.create_task(
        description="Test Description",
        agent=agent,
        expected_output="Test Output"
    )
    
    crew = toolkit.create_crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    assert isinstance(crew, Crew)
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1
    assert crew.verbose is True 