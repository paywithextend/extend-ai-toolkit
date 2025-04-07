import os
from agents import Agent, Runner
from dotenv import load_dotenv

from extend_ai_toolkit.openai.toolkit import ExtendOpenAIToolkit
from extend_ai_toolkit.shared import Configuration, Scope, Product, Actions
    
# Load environment variables
load_dotenv()

api_key = os.environ.get("EXTEND_API_KEY")
api_secret = os.environ.get("EXTEND_API_SECRET")

async def main():
    extend_openai_toolkit = ExtendOpenAIToolkit(
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

    extend_agent = Agent(
        name="Extend Agent",
        instructions="You are an expert at integrating with Extend. You can help users manage virtual cards, view credit cards, and check transactions.",
        tools=extend_openai_toolkit.get_tools(),
        model="gpt-4o",
    )

    # Example interaction with the agent
    print("Welcome to the Extend OpenAI Agent! Type 'quit' to exit.")
    while True:
        user_input = input("\nYour question: ").strip()
        if user_input.lower() == 'quit':
            break
            
        response = await Runner.run(extend_agent, user_input)
        print("Agent response:", response.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
