# AI Toolkit for Extend

The Extend AI Toolkit enables Model Context Protocol and LangChain agent framework to integrate with Extend APIs
through function calling.

### Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package run:

```sh
pip install extend_ai_toolkit --extra-index-url https://<GITHUB_USERNAME>:<GITHUB_TOKEN>@pypi.pkg.github.com/paywithextend
```

#### Requirements

- Python 3.10+

### Usage

The library needs to be configured with your api key and api secret.

#### Model Context Protocol

The Extend AI Toolkit also supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.com/).

To run the Extend MCP server in the inspector during development use the following command:

```bash
npx @modelcontextprotocol/inspector python extend_ai_toolkit/modelcontextprotocol/main.py --tools=virtual_cards.read,credit_cards.read
```

Make sure to set `EXTEND_API_KEY` and `EXTEND_API_SECRET` in your environment variables.

To run the Extend MCP server using npx, use the following command:

```
TODO
```

Alternatively, you can set up your own MCP server. For example:

```
import os
import sys

from dotenv import load_dotenv

from extend_ai_toolkit.modelcontextprotocol.server import ExtendMCPServer
from extend_ai_toolkit.shared import Configuration

load_dotenv()

server = ExtendMCPServer(
    host=os.environ.get("API_HOST"),
    version=os.environ.get("API_VERSION"),
    api_key=os.environ.get("EXTEND_API_KEY"),
    api_secret=s.environ.get("EXTEND_API_SECRET"),
    configuration=Configuration(
        actions={
            "get_virtual_cards": {
                "read": True,
            },
            "create_virtual_cards": {
                "create": True,
            }
        }
    )
)

if __name__ == "__main__":
    try:
        server.run(transport='stdio')
    except Exception as e:
        sys.stderr.write(f"{str(e)}\n")
```

#### LangChain

The toolkit works with LangChain and can be passed as a list of tools. For example:

```
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from extend_ai_toolkit.langchain.toolkit import ExtendLangChainToolkit

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
)

extend_langchain_toolkit = ExtendLangChainToolkit(
    api_key="apik_...",
    api_secret="...",
    configuration=Configuration(
        actions={
            "get_virtual_cards": {
                "read": True,
            },
            "create_virtual_cards": {
                "create": True,
            }
        }
    )
)

tools = []
tools.extend(stripe_agent_toolkit.get_tools())

langgraph_agent_executor = create_react_agent(llm, tools)
```
