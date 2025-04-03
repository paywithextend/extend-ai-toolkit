# Extend AI Toolkit 

## Overview

The [Extend](https://www.paywithextend.com) AI Toolkit provides a python based implementation of tools to integrate with Extend APIs for multiple AI frameworks including Anthropic's [Model Context Protocol (MCP)](https://modelcontextprotocol.com/), [OpenAI](https://github.com/openai/openai-agents-python), [LangChain](https://github.com/langchain-ai/langchain), and [CrewAI](https://github.com/joaomdmoura/crewAI). It enables users to delegate certain actions in the spend management flow to AI agents or MCP-compatible clients like Claude desktop.

These tools are designed for existing Extend users with API keys. If you are not signed up with Extend and would like to learn more about our modern, easy-to-use virtual card and spend management platform for small- and medium-sized businesses, you can check us out at [paywithextend.com](https://www.paywithextend.com/).

## Features

- **Multiple AI Framework Support**: Works with Anthropic Model Context Protocol, OpenAI Agents, LangChain LangGraph & ReAct, and CrewAI frameworks 
- **Comprehensive Tool Set**: Supports all of Extend's major API functionalities, spanning our Credit Card, Virtual Card, Transaction & Expense Management endpoints

## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package run:

```sh
pip install extend_ai_toolkit@git+https://github.com/paywithextend/extend-ai-toolkit@development
```

### Requirements

- **Python**: Version 3.10 or higher
- **Extend API Key**: Sign up at [paywithextend.com](https://paywithextend.com) to obtain an API key
- **Framework-specific Requirements**:
  - LangChain: `langchain` and `langchain-openai` packages
  - OpenAI: `openai` package
  - CrewAI: `crewai` package
  - Anthropic: `anthropic` package (for Claude)

## Configuration

The library needs to be configured with your Extend API key and API, either through environment variables or command line arguments:

```
--api-key=your_api_key_here --api-secret=your_api_secret_here 
```

or via environment variables:
```
EXTEND_API_KEY=your_api_key_here
EXTEND_API_SECRET=your_api_secret_here
```

## Available Tools

The toolkit provides a comprehensive set of tools organized by functionality:

### Virtual Cards
- `get_virtual_cards`: Fetch virtual cards with optional filters
- `get_virtual_card_detail`: Get detailed information about a specific virtual card

### Credit Cards
- `get_credit_cards`: List all credit cards
- `get_credit_card_detail`: Get detailed information about a specific credit card

### Transactions
- `get_transactions`: Fetch transactions with various filters
- `get_transaction_detail`: Get detailed information about a specific transaction
- `update_transaction_expense_data`: Update expense-related data for a transaction

### Expense Management
- `get_expense_categories`: List all expense categories
- `get_expense_category`: Get details of a specific expense category
- `get_expense_category_labels`: Get labels for an expense category
- `create_expense_category`: Create a new expense category
- `create_expense_category_label`: Add a label to an expense category
- `update_expense_category`: Modify an existing expense category

## Usage Examples

### Model Context Protocol

The toolkit provides resources in the `extend_ai_toolkit.modelcontextprotocol` package to help you build an MCP server.

#### Development

Test Extend MCP server locally using MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python extend_ai_toolkit/modelcontextprotocol/main.py --tools=virtual_cards.read,credit_cards.read
```

#### Claude Desktop Integration

Add this tool as an MCP server to Claude Desktop by editing the config file:

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "extend-mcp": {
    "command": "python",
    "args": [
      "-m",
      "extend_ai_toolkit.modelcontextprotocol.main",
      "--tools=all"
    ],
    "env": {
      "EXTEND_API_KEY": "apik_XXXX",
      "EXTEND_API_SECRET": "XXXXX"
    }
  }
}
```

#### Direct Execution

For advanced scenarios, you can execute the server directly:

STDIO Transport:
```bash
python -m extend_ai_toolkit.modelcontextprotocol.main --tools=virtual_cards.read,credit_cards.read
```

SSE Transport:
```bash
python -m extend_ai_toolkit.modelcontextprotocol.main_sse --tools=credit_cards.read --api-key="apikey" --api-secret="apisecret"

```

Connect using the MCP terminal client:
```bash
python -m extend_ai_toolkit.modelcontextprotocol.client.mcp_client --mcp-server-host localhost --mcp-server-port 8000 --llm-provider=anthropic --llm-model=claude-3-5-sonnet-20241022
```

### OpenAI

```python
import os
from langchain_openai import ChatOpenAI
from extend_ai_toolkit.openai.toolkit import ExtendOpenAIToolkit
from extend_ai_toolkit.shared import Configuration, Scope, Product, Actions

# Initialize the OpenAI toolkit
extend_openai_toolkit = ExtendOpenAIToolkit(
    api_key=os.environ.get("EXTEND_API_KEY"),
    api_secret=os.environ.get("EXTEND_API_SECRET"),
    configuration=Configuration(
        scope=[
            Scope(Product.VIRTUAL_CARDS, actions=Actions(read=True)),
            Scope(Product.CREDIT_CARDS, actions=Actions(read=True)),
            Scope(Product.TRANSACTIONS, actions=Actions(read=True)),
        ]
    )
)

# Create an agent with the tools
extend_agent = Agent(
    name="Extend Agent",
    instructions="You are an expert at integrating with Extend",
    tools=extend_openai_toolkit.get_tools()
)
```

### LangChain

```python
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from extend_ai_toolkit.langchain.toolkit import ExtendLangChainToolkit
from extend_ai_toolkit.shared import Configuration, Scope, Product, Actions

# Initialize the LangChain toolkit
extend_langchain_toolkit = ExtendLangChainToolkit(
    api_key=os.environ.get("EXTEND_API_KEY"),
    api_secret=os.environ.get("EXTEND_API_SECRET"),
    configuration=Configuration(
        scope=[
            Scope(Product.VIRTUAL_CARDS, actions=Actions(read=True)),
            Scope(Product.CREDIT_CARDS, actions=Actions(read=True)),
            Scope(Product.TRANSACTIONS, actions=Actions(read=True)),
        ]
    )
)

# Create tools for the agent
tools = extend_langchain_toolkit.get_tools()

# Create the agent executor
langgraph_agent_executor = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools
)
```

### CrewAI

```python
import os
from extend_ai_toolkit.crewai.toolkit import ExtendCrewAIToolkit
from extend_ai_toolkit.shared import Configuration, Scope, Product, Actions

# Initialize the CrewAI toolkit
toolkit = ExtendCrewAIToolkit(
    api_key=os.environ.get("EXTEND_API_KEY"),
    api_secret=os.environ.get("EXTEND_API_SECRET"),
    configuration=Configuration(
        scope=[
            Scope(Product.VIRTUAL_CARDS, actions=Actions(read=True)),
            Scope(Product.CREDIT_CARDS, actions=Actions(read=True)),
            Scope(Product.TRANSACTIONS, actions=Actions(read=True)),
        ]
    )
)

# Configure the LLM (using Claude)
toolkit.configure_llm(
    model="claude-3-opus-20240229",
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Create the Extend agent
extend_agent = toolkit.create_agent(
    role="Extend Integration Expert",
    goal="Help users manage virtual cards, view credit cards, and check transactions efficiently",
    backstory="You are an expert at integrating with Extend, with deep knowledge of virtual cards, credit cards, and transaction management.",
    verbose=True
)

# Create a task for handling user queries
query_task = toolkit.create_task(
    description="Process and respond to user queries about Extend services",
    agent=extend_agent,
    expected_output="A clear and helpful response addressing the user's query",
    async_execution=True
)

# Create a crew with the agent and task
crew = toolkit.create_crew(
    agents=[extend_agent],
    tasks=[query_task],
    verbose=True
)

# Run the crew
result = crew.kickoff()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
