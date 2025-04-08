import os
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from extend_ai_toolkit.langchain.toolkit import ExtendLangChainToolkit
from extend_ai_toolkit.shared import Configuration, Scope, Product, Actions

# Load environment variables
load_dotenv()

# Get required environment variables
api_key = os.environ.get("EXTEND_API_KEY")
api_secret = os.environ.get("EXTEND_API_SECRET")

# Validate environment variables
if not all([api_key, api_secret]):
    raise ValueError("Missing required environment variables. Please set EXTEND_API_KEY and  EXTEND_API_SECRET")

llm = ChatOpenAI(
    model="gpt-4o",
)

extend_langchain_toolkit = ExtendLangChainToolkit(
    api_key,
    api_secret,
    Configuration(
      scope=[
        Scope(Product.VIRTUAL_CARDS, actions=Actions(read=True)),
        Scope(Product.CREDIT_CARDS, actions=Actions(read=True)),
        Scope(Product.TRANSACTIONS, actions=Actions(read=True)),
       ]
    )
)

tools = []
tools.extend(extend_langchain_toolkit.get_tools())

# Create the react agent
langgraph_agent_executor = create_react_agent(
    llm,
    tools
)

async def chat_with_agent():
    print("\nWelcome to the Extend AI Assistant!")
    print("You can ask me to:")
    print("- List all credit cards")
    print("- List all virtual cards")
    print("- Show details for a specific virtual card")
    print("- Show transactions for a specific period")
    print("- Show details for a specific transaction")
    print("\nType 'exit' to end the conversation.\n")
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nGoodbye!")
            break
            
        # Process the query
        result = await langgraph_agent_executor.ainvoke({
            "input": user_input,
            "messages": [
                SystemMessage(content="You are a helpful assistant that can interact with the Extend API to manage virtual cards, credit cards, and transactions."),
                HumanMessage(content=user_input)
            ]
        })
        
        # Extract and print the assistant's message
        for message in result.get('messages', []):
            if isinstance(message, AIMessage):
                print("\nAssistant:", message.content)

if __name__ == "__main__":
    asyncio.run(chat_with_agent())
