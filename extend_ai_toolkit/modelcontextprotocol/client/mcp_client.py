import argparse
import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.sse import sse_client

from extend_ai_toolkit.modelcontextprotocol.client import (
    ChatClient,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_client")


class MCPClient:
    """
    Client for interacting with Model Capability Protocol (MCP) servers
    using Server-Sent Events (SSE) transport and the OpenAI API.
    """

    def __init__(self, llm_client: ChatClient, model_name="gpt-4o", max_tokens=1000):
        self.session: Optional[ClientSession] = None
        self._session_context = None
        self._streams_context = None
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.llm_client = llm_client

    @asynccontextmanager
    async def connect(self, server_url: str):
        """
        Connect to MCP server with SSE transport as an async context manager.

        Args:
            server_url: URL of the SSE MCP server
        """
        try:
            # Connect to SSE server
            self._streams_context = sse_client(url=server_url)
            streams = await self._streams_context.__aenter__()

            # Create client session
            self._session_context = ClientSession(*streams)
            self.session = await self._session_context.__aenter__()

            # Initialize session
            await self.session.initialize()

            # List available tools (for logging purposes)
            await self.session.list_tools()
            logger.info("MCP client operation completed or failed; payload omitted")

            yield self

        except Exception:
            logger.error("MCP client operation completed or failed; payload omitted")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
            self._session_context = None

        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)
            self._streams_context = None

        self.session = None

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of available tools from the MCP server.

        Returns:
            List of tool dictionaries with name, description, and input schema
        """
        if not self.session:
            raise ConnectionError("Not connected to MCP server")

        response = await self.session.list_tools()
        return [
            {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
            for tool in response.tools
        ]

    async def process_query(self, query: str) -> str:
        """
        Process a query using OpenAI's ChatCompletion endpoint.

        Args:
            query: User query string

        Returns:
            Response text from the OpenAI API.
        """
        if not self.session:
            raise ConnectionError("Not connected to MCP server")

        messages = [{"role": "user", "content": query}]

        # Get available MCP tools and convert them into function definitions
        available_tools = await self.list_available_tools()
        functions = []
        for tool in available_tools:
            # Convert your tool's input_schema to a valid JSON schema if needed
            functions.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                }
            )

        final_text = []

        try:
            # Call the LLM API
            content, function_call = await self.llm_client.generate_completion(
                messages=messages,
                functions=functions,
                max_tokens=self.max_tokens,
            )

            if function_call:
                tool_name = function_call["name"]
                tool_arguments_str = function_call["arguments"]

                try:
                    # Convert the JSON string into a dictionary
                    tool_arguments = json.loads(tool_arguments_str) if tool_arguments_str else None
                except json.JSONDecodeError:
                    logger.error("MCP client operation completed or failed; payload omitted")
                    tool_arguments = None

                logger.info("MCP client operation completed or failed; payload omitted")

                # Call the corresponding tool on the MCP server
                tool_result = await self.session.call_tool(tool_name, tool_arguments)

                # Append the function call and tool result to the conversation history
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "function_call": {"name": tool_name, "arguments": tool_arguments_str},
                    }
                )
                messages.append(
                    {"role": "function", "name": tool_name, "content": tool_result.content}
                )

                # Make a follow-up API call including the tool result
                assistant_message = await self.llm_client.generate_with_tool_result(
                    messages=messages, max_tokens=self.max_tokens
                )

                final_text.append(assistant_message)
                return "\n".join(final_text)
            else:
                # No function call; return the assistant's message directly
                final_text.append(content)
                return "\n".join(final_text)

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error("MCP request failed")
            return error_msg

    async def chat_loop(self):
        """Run an interactive chat loop"""
        if not self.session:
            raise ConnectionError("Not connected to MCP server")

        print("\nExtend MCP Client Started!")
        print("Enter your queries or type 'quit' to exit.")

        while True:
            try:
                await asyncio.sleep(0.1)
                sys.stdout.flush()

                query = input("\nQuery: ").strip()

                if query.lower() in ("quit", "exit", "q"):
                    break

                print("Processing query...")
                response = await self.process_query(query)
                print("\nResponse:")
                print(response)

            except KeyboardInterrupt:
                print("\nExiting chat loop...")
                break

            except Exception as e:
                logger.error("MCP client operation completed or failed; payload omitted")
                print(f"\nError: {str(e)}")


async def main():
    """Main entry point for the MCP client"""

    parser = argparse.ArgumentParser(
        description="MCP Client for interacting with SSE-based servers."
    )
    parser.add_argument(
        "--llm-provider",
        type=str,
        choices=["openai", "anthropic"],
        default="openai",
        help="LLM Provider (e.g., openai)",
    )
    parser.add_argument(
        "--llm-model", type=str, help="LLM Model (e.g., gpt-4o, claude-3-5-sonnet-20240229)"
    )
    parser.add_argument(
        "--mcp-server-host", type=str, required=True, help="Server hostname (e.g., localhost)"
    )
    parser.add_argument(
        "--mcp-server-port", type=int, required=True, help="Server port (e.g., 8000)"
    )
    parser.add_argument(
        "--scheme",
        type=str,
        choices=["http", "https"],
        default="http",
        help="URL scheme (default: http)",
    )

    args = parser.parse_args()

    server_url = f"{args.scheme}://{args.mcp_server_host}:{args.mcp_server_port}/sse"
    print(f"Connecting to: {server_url}")

    if args.llm_provider == "openai":
        model = args.llm_model or "gpt-4o"
        from .openai_chat_client import OpenAIChatClient
        llm_client = OpenAIChatClient(model_name=model)
    else:
        model = args.llm_model or "claude-3-7-sonnet-20250219"
        from .anthropic_chat_client import AnthropicChatClient
        llm_client = AnthropicChatClient(model_name=model)

    try:
        async with MCPClient(llm_client=llm_client).connect(server_url=server_url) as client:
            await client.chat_loop()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        logger.error("MCP client operation completed or failed; payload omitted")
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
