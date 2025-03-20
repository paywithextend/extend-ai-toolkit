import argparse
import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from mypy.util import json_dumps
from openai import AsyncOpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_client")

load_dotenv()

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class MCPClient:
    """
    Client for interacting with Model Capability Protocol (MCP) servers
    using Server-Sent Events (SSE) transport and the OpenAI API.
    """

    def __init__(self, model_name="gpt-4o", max_tokens=1000):
        self.session: Optional[ClientSession] = None
        self._session_context = None
        self._streams_context = None
        self.model_name = model_name
        self.max_tokens = max_tokens

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
            response = await self.session.list_tools()
            tool_names = [tool.name for tool in response.tools]
            logger.info(f"Connected to server with tools: {tool_names}")

            yield self

        except Exception as e:
            logger.error(f"Error connecting to SSE server: {str(e)}")
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
        return [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

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
            functions.append({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            })

        final_text = []

        try:
            # Call the OpenAI API
            response = await aclient.chat.completions.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                messages=messages,
                functions=functions
            )

            choice = response.choices[0]

            # Check if the assistant wants to call a function
            if choice.finish_reason == "function_call":
                func_call = choice.message.function_call
                tool_name = func_call.name  # This should match one of the sanitized tool names
                tool_arguments_str = func_call.arguments  # This is a JSON string

                try:
                    # Convert the JSON string into a dictionary
                    tool_arguments = json.loads(tool_arguments_str) if tool_arguments_str else None
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing tool arguments: {str(e)}")
                    tool_arguments = None

                logger.info(f"Routing function call to tool: {tool_name} with args: {json_dumps(tool_arguments)}")

                # Call the corresponding tool on the MCP server
                tool_result = await self.session.call_tool(tool_name, tool_arguments)

                # Append the function call and tool result to the conversation history
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": tool_name,
                        "arguments": tool_arguments_str
                    }
                })
                messages.append({
                    "role": "function",
                    "name": tool_name,
                    "content": tool_result.content
                })

                # Make a follow-up API call including the tool result
                follow_up = await aclient.chat.completions.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    messages=messages,
                )

                assistant_message = follow_up.choices[0].message.content
                # final_text.append(tool_result.content[0].text)
                final_text.append(assistant_message)
                return "\n".join(final_text)
            else:
                # No function call; return the assistant's message directly
                assistant_message = choice.message.content
                final_text.append(assistant_message)
                return "\n".join(final_text)

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def chat_loop(self):
        """Run an interactive chat loop"""
        if not self.session:
            raise ConnectionError("Not connected to MCP server")

        print("\nExtend MCP Client Started!")
        print("Enter your queries or type 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() in ('quit', 'exit', 'q'):
                    break

                print("Processing query...")
                response = await self.process_query(query)
                print("\nResponse:")
                print(response)

            except KeyboardInterrupt:
                print("\nExiting chat loop...")
                break

            except Exception as e:
                logger.error(f"Error in chat loop: {str(e)}")
                print(f"\nError: {str(e)}")


async def main():
    """Main entry point for the MCP client"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <URL of SSE MCP server (e.g., http://localhost:8080/sse)>")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="MCP Client for interacting with SSE-based servers.")
    parser.add_argument("--server-host", type=str, required=True, help="Server hostname (e.g., localhost)")
    parser.add_argument("--server-port", type=int, required=True, help="Server port (e.g., 8000)")
    parser.add_argument("--scheme", type=str, choices=["http", "https"], default="http",
                        help="URL scheme (default: http)")

    args = parser.parse_args()

    server_url = f"{args.scheme}://{args.server_host}:{args.server_port}/sse"
    print(f"Connecting to: {server_url}")

    try:
        async with MCPClient().connect(server_url=server_url) as client:
            await client.chat_loop()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
