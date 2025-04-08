# test_options.py
import os

import pytest

from extend_ai_toolkit.modelcontextprotocol import Options, validate_options


@pytest.fixture(autouse=True)
def clear_environment_variables():
    """Clear relevant environment variables before each test"""
    for var in ["EXTEND_API_KEY", "EXTEND_API_SECRET"]:
        if var in os.environ:
            del os.environ[var]
    yield


def test_initialization():
    """Test basic initialization with valid arguments"""
    options = Options(
        tools="tool1,tool2",
        api_key="apik_12345",
        api_secret="secret123"
    )
    assert options.tools == "tool1,tool2"
    assert options.api_key == "apik_12345"
    assert options.api_secret == "secret123"


def test_missing_api_key():
    """Test validation when api_key is missing"""
    with pytest.raises(ValueError, match="Extend API key not provided"):
        Options(
            tools="tool1,tool2",
            api_key=None,
            api_secret="secret123"
        )


def test_invalid_api_key_format():
    """Test validation when api_key has invalid format"""
    with pytest.raises(ValueError, match='Extend API key must start with "apik_"'):
        Options(
            tools="tool1,tool2",
            api_key="invalid_key",
            api_secret="secret123"
        )


def test_missing_api_secret():
    """Test validation when api_secret is missing"""
    with pytest.raises(ValueError, match="Extend API key not provided"):
        Options(
            tools="tool1,tool2",
            api_key="apik_12345",
            api_secret=None
        )


def test_missing_tools():
    """Test validation when tools is missing"""
    with pytest.raises(ValueError, match="The --tools argument must be provided"):
        Options(
            tools=None,
            api_key="apik_12345",
            api_secret="secret123"
        )


def test_from_args_with_env_vars(monkeypatch):
    """Test from_args using environment variables"""
    monkeypatch.setenv("EXTEND_API_KEY", "apik_env")
    monkeypatch.setenv("EXTEND_API_SECRET", "env_secret")

    options = Options.from_args(["--tools=tool1,tool2"], ["tool1", "tool2"])
    assert options.tools == "tool1,tool2"
    assert options.api_key == "apik_env"
    assert options.api_secret == "env_secret"


def test_from_args_with_cli_args():
    """Test from_args using command line arguments"""
    options = Options.from_args([
        "--api-key=apik_cli",
        "--api-secret=cli_secret",
        "--tools=tool1,tool2"
    ], ["tool1", "tool2"])

    assert options.tools == "tool1,tool2"
    assert options.api_key == "apik_cli"
    assert options.api_secret == "cli_secret"


def test_from_args_invalid_tool():
    """Test from_args with invalid tool"""
    with pytest.raises(ValueError, match="Invalid tool: invalid_tool"):
        Options.from_args(["--tools=invalid_tool"], ["tool1", "tool2"])


def test_from_args_all_tools():
    """Test from_args with 'all' as tool"""
    options = Options.from_args([
        "--api-key=apik_12345",
        "--api-secret=secret123",
        "--tools=all"
    ], ["tool1", "tool2"])
    assert options.tools == "all"


def test_from_args_invalid_format():
    """Test from_args with invalid argument format"""
    with pytest.raises(ValueError, match="is not in --key=value format"):
        Options.from_args(["--api-key"], ["tool1", "tool2"])


def test_from_args_invalid_argument():
    """Test from_args with invalid argument name"""
    with pytest.raises(ValueError, match="Invalid argument: invalid"):
        Options.from_args(["--invalid=value"], ["tool1", "tool2"])


def test_validate_options_decorator():
    """Test the validate_options decorator"""

    @validate_options
    class TestClass:
        def __init__(self, tools, api_key, api_secret):
            self.tools = tools
            self.api_key = api_key
            self.api_secret = api_secret

    # Should run without errors
    instance = TestClass(
        tools="tool1,tool2",
        api_key="apik_12345",
        api_secret="secret123"
    )

    # Check that validation errors are raised
    with pytest.raises(ValueError):
        TestClass(
            tools=None,
            api_key="apik_12345",
            api_secret="secret123"
        )


if __name__ == "__main__":
    pytest.main()
