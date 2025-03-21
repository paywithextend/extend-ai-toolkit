# AI Toolkit for Extend

## Overview

The Extend AI Toolkit provides a python based implementation of tools to integrate with Extend APIs for both the [OpenAI](https://github.com/openai/openai-agents-python) and [LangChain](https://github.com/langchain-ai/langchain) agent frameworks, as well [Model Context Protocol (MCP)](https://modelcontextprotocol.com/). It enables users to delegate certain actions in the spend management flow to AI agents or MCP-compatible clients like Claude desktop.

These tools are designed for existing Extend users with API keys. If you are not signed up with Extend and are interested in a cutting edge spend management tool, you can check us out at [paywithextend.com](https://www.paywithextend.com/).

## Features

- **Tools**:
- - `get_virtual_cards`: Fetch virtual cards with optional filters for status, recipient (ID), and search_term
  - `get_transaction_detail`: Fetch detailed information about a specific transaction by its ID.
  - `get_transactions`: Fetch transactions with optional filters for start_date, end_date, virtual_card_id, min_amount_cents, and max_amount_cents
  - `get_transaction_detail`: Fetch detailed information about a specific transaction by its ID.- 
- **Asynchronous API Calls**: Uses `httpx` for efficient, non-blocking requests to the Extend API.
- **Environment Variable Support**: Securely manage your API key and API secret via a `.env` file.

## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package run:

```sh
pip install extend_ai_toolkit@git+https://github.com/paywithextend/extend-ai-toolkit@development
```

### Requirements

- **Python**: Version 3.10 or higher.
- **Extend API Key**: Sign up at [paywithextend.com](https://paywithextend.com) to obtain an API key.

## Usage

The library needs to be configured with your Extend api key and api secret either through environment variables or command line arguments
```
EXTEND_API_KEY=your_api_key_here
EXTEND_API_SECRET=your_api_secret_here
```

### Model Context Protocol 
The toolkit provides a variety of resources in the modelcontextprotocol package (`extend_ai_toolkit.modelcontextprotocol`) to help you build an MCP server. 

#### Development

Test Extend MCP server locally using MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python extend_ai_toolkit/modelcontextprotocol/main.py --tools=virtual_cards.read,credit_cards.read
```

Make sure to set `EXTEND_API_KEY` and `EXTEND_API_SECRET` in your environment variables.

#### Claude Desktop

Add this tool as an MCP server to Claude Desktop by editing the Claude config file.

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
  "extend-mcp": {
    "command": "python",
    "args": [
      "-m",
      "extend_ai_toolkit.modelcontextprotocol.main",
      "--tools=all" // or a subset, e.g. "virtual_cards.read,credit_cards.read"
    ],
    "env": {
      "EXTEND_API_KEY": "apik_XXXX",
      "EXTEND_API_SECRET": "XXXXX"
    }
  }
```

#### Direct Execution

For advanced scenarios like custom deployments or running without Claude, you can execute your server directly:


STDIO Transport:
```
python -m extend_ai_toolkit.modelcontextprotocol.main --tools=virtual_cards.read,credit_cards.read --api-key=apik_XXXX --api-secret=XXXX
```

SSE Transport:
```
python -m extend_ai_toolkit.modelcontextprotocol.main_sse --tools=virtual_cards.read,credit_cards.read --api-key=apik_XXXX --api-secret=XXXX
```

Additionally, You can connect to your SSE server using our custom MCP terminal client

```
python -m extend_ai_toolkit.modelcontextprotocol.mcp_client 
```

Example of setting up your own MCP server:

```
import os
import sys

from dotenv import load_dotenv

from extend_ai_toolkit.modelcontextprotocol.server import ExtendMCPServer
from extend_ai_toolkit.shared import Configuration, ProductPermissions, Product, Permissions

load_dotenv()

server = ExtendMCPServer(    
    api_key=os.environ.get("EXTEND_API_KEY"),
    api_secret=s.environ.get("EXTEND_API_SECRET"),
    configuration=Configuration(
        product_permissions=[
            ProductPermissions(Product.VIRTUAL_CARDS, permissions=Permissions(create=True, update=True, read=True)),
            ProductPermissions(Product.CREDIT_CARDS, permissions=Permissions(read=True)),
            ProductPermissions(Product.TRANSACTIONS, permissions=Permissions(read=True)),
        ]
    )
)

if __name__ == "__main__":
    try:
        server.run(transport='stdio')
    except Exception as e:
        sys.stderr.write(f"{str(e)}\n")
```

### OpenAI

TODO


### LangChain

The toolkit works with LangChain and can be passed as a list of tools. For example:

```
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from extend_ai_toolkit.langchain.toolkit import ExtendLangChainToolkit
from extend_ai_toolkit.shared import Configuration, ProductPermissions, Product, Permissions

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
)

extend_langchain_toolkit = ExtendLangChainToolkit(
    api_key="apik_...",
    api_secret="...",
    configuration=Configuration(
        product_permissions=[
            ProductPermissions(Product.VIRTUAL_CARDS, permissions=Permissions(create=True, update=True, read=True)),
            ProductPermissions(Product.CREDIT_CARDS, permissions=Permissions(read=True)),
            ProductPermissions(Product.TRANSACTIONS, permissions=Permissions(read=True)),
        ]
    )
)
)

tools = []
tools.extend(extend_agent_toolkit.get_tools())

langgraph_agent_executor = create_react_agent(llm, tools)
```
