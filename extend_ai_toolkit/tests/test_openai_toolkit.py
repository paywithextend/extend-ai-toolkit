import inspect
import json
from unittest.mock import patch, Mock, AsyncMock

import pytest
from pydantic import BaseModel
from agents import FunctionTool

from extend_ai_toolkit.openai.toolkit import ExtendOpenAIToolkit
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
        mock_api_class.default_instance.return_value = mock_api_instance
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

    return mock_config


@pytest.fixture
def toolkit(mock_extend_api, mock_configuration):
    """Fixture that creates an ExtendOpenAIToolkit instance with mocks"""
    _, mock_api_instance = mock_extend_api
    toolkit = ExtendOpenAIToolkit(
        extend_api=mock_api_instance,
        configuration=mock_configuration
    )
    return toolkit


def test_get_tools_returns_correct_tools(toolkit, mock_configuration):
    """Test that get_tools returns the correct set of tools"""
    tools = toolkit.get_tools()
    
    # We configured mock_configuration to return 2 tools
    assert len(tools) == 2

    # Verify tool details
    assert tools[0].name == ExtendAPITools.GET_VIRTUAL_CARDS.value
    assert tools[0].description == "Get all virtual cards"
    assert tools[1].name == ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value
    assert tools[1].description == "Get details of a virtual card"


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
    input_str = json.dumps({"page": 0, "per_page": 10})
    result = await tool.on_invoke_tool(None, input_str)

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

    # Get the expected schema
    expected_schema = VirtualCardsSchema.model_json_schema()
    expected_schema["additionalProperties"] = False
    expected_schema["type"] = "object"
    if "description" in expected_schema:
        del expected_schema["description"]
    if "title" in expected_schema:
        del expected_schema["title"]
    if "properties" in expected_schema:
        for prop in expected_schema["properties"].values():
            if "title" in prop:
                del prop["title"]
            if "default" in prop:
                del prop["default"]

    # Verify the tool has the correct schema
    assert tool.params_json_schema == expected_schema 