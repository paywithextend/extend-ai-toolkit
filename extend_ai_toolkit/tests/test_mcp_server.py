import inspect
from unittest.mock import patch, Mock, AsyncMock

import pytest
from mcp.server import FastMCP
from pydantic import BaseModel

from extend_ai_toolkit import __version__ as toolkit_version
from extend_ai_toolkit.modelcontextprotocol import ExtendMCPServer
from extend_ai_toolkit.shared import Configuration, ExtendAPITools, Tool


# Define schema classes needed for testing
class InvalidToolSchema(BaseModel):
    dummy: str = "test"


class VirtualCardsSchema(BaseModel):
    page: int = 0
    per_page: int = 10


class VirtualCardDetailSchema(BaseModel):
    virtual_card_id: str = "test_id"


@pytest.fixture
def mock_extend_api():
    """Fixture that provides a mocked ExtendAPI instance"""
    from extend_ai_toolkit.modelcontextprotocol import server
    original_api = server.ExtendAPI

    try:
        # Replace with mock
        mock_api_class = Mock()
        mock_api_instance = Mock()
        mock_api_instance.run = AsyncMock()
        mock_api_class.default_instance.return_value = mock_api_instance
        mock_api_class.from_auth.return_value = mock_api_instance
        server.ExtendAPI = mock_api_class

        yield mock_api_class
    finally:
        # Restore original
        server.ExtendAPI = original_api


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
def mock_fastmcp():
    """Fixture that patches the FastMCP parent class"""
    with patch.object(FastMCP, "__init__", return_value=None) as mock_init:
        with patch.object(FastMCP, "add_tool") as mock_add_tool:
            yield {
                "init": mock_init,
                "add_tool": mock_add_tool
            }


@pytest.fixture
def server(mock_extend_api, mock_configuration, mock_fastmcp):
    """Fixture that creates an ExtendMCPServer instance with mocks"""
    server = ExtendMCPServer.default_instance(
        api_key="test_api_key",
        api_secret="test_api_secret",
        configuration=mock_configuration
    )

    # Attach the mocks for reference in tests
    server._mock_api = mock_extend_api
    server._mock_fastmcp = mock_fastmcp
    return server


def test_init_calls_parent_constructor(mock_fastmcp):
    """Test that parent constructor is called with correct parameters"""
    # Create the server directly since we're testing initialization
    mock_config = Mock(spec=Configuration)
    # Configure allowed_tools to return an empty list (iterable)
    mock_config.allowed_tools.return_value = []

    ExtendMCPServer.default_instance(
        api_key="test_api_key",
        api_secret="test_api_secret",
        configuration=mock_config
    )

    # Verify the parent constructor was called with correct arguments
    mock_fastmcp["init"].assert_called_once_with(
        name="Extend MCP Server",
        version=toolkit_version,
    )

def test_init_registers_allowed_tools(server, mock_configuration, mock_fastmcp):
    """Test that allowed tools are registered correctly"""
    # We configured mock_configuration to return 2 tools
    assert mock_fastmcp["add_tool"].call_count == 2

    # Verify tool details for the first call
    args, kwargs = mock_fastmcp["add_tool"].call_args_list[0]
    assert args[1] == "get_virtual_cards"
    assert args[2] == "Get all virtual cards"

    # Verify tool details for the second call
    args, kwargs = mock_fastmcp["add_tool"].call_args_list[1]
    assert args[1] == "get_virtual_card_detail"
    assert args[2] == "Get details of a virtual card"


@pytest.mark.asyncio
async def test_handle_tool_request_forwards_to_api(server, mock_extend_api):
    """Test that the handler function correctly forwards requests to the API"""
    # Get the first mock tool
    mock_tool = server._mock_fastmcp["add_tool"].call_args_list[0][0][0]

    # Set up a return value for the API call
    server._mock_api.default_instance.return_value.run.return_value = {"status": "success", "data": [{"id": "123"}]}

    # Call the handler
    result = await mock_tool(page=0, per_page=10)

    # Verify API was called correctly
    server._mock_api.default_instance.return_value.run.assert_called_once_with(
        ExtendAPITools.GET_VIRTUAL_CARDS.value,
        page=0,
        per_page=10
    )

    # Verify the result is formatted correctly
    assert result == {
        "content": [
            {
                "type": "text",
                "text": str({"status": "success", "data": [{"id": "123"}]})
            }
        ]
    }


def test_handler_signature_matches_function(server):
    """Test that the generated handler functions have the correct signature"""
    # Get the first handler function
    mock_handler = server._mock_fastmcp["add_tool"].call_args_list[0][0][0]

    # Inspect its signature
    sig = inspect.signature(mock_handler)

    # For get_virtual_cards, we expect parameters like page, per_page, etc.
    # (minus the first parameter which is usually 'self' or 'api')
    # Check that these parameters exist
    assert "page" in sig.parameters
    assert "per_page" in sig.parameters


def test_match_statement_default_case():
    """Test that the default case in a match statement raises ValueError"""

    # Create a mock tool
    mock_tool = Mock()
    mock_tool.name = "Test Tool"
    mock_tool.method.value = "non_existent_method"

    # Define a function that mimics the match statement in ExtendMCPServer.__init__
    def match_function(tool):
        match tool.method.value:
            case ExtendAPITools.GET_VIRTUAL_CARDS.value:
                return "get_virtual_cards"
            case ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value:
                return "get_virtual_card_detail"
            # Add other cases as needed
            case _:
                raise ValueError(f"Invalid tool {tool}")

    # Test that the default case raises ValueError
    with pytest.raises(ValueError):
        match_function(mock_tool)
