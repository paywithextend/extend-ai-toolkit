"""
Example implementation of an AI agent using the CrewAI framework.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file, overriding any existing variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path, override=True)

import asyncio
from extend_ai_toolkit.crewai.toolkit import ExtendCrewAIToolkit
from extend_ai_toolkit.shared import Configuration, Scope, Product, Actions


def validate_env_vars() -> tuple[str, str, str]:
    """Validate required environment variables.
    
    Returns:
        Tuple of (api_key, api_secret)
        
    Raises:
        ValueError: If any required environment variables are missing
    """
    api_key = os.environ.get("EXTEND_API_KEY")
    api_secret = os.environ.get("EXTEND_API_SECRET")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not all([api_key, api_secret, anthropic_key]):
        missing = []
        if not api_key: missing.append("EXTEND_API_KEY")
        if not api_secret: missing.append("EXTEND_API_SECRET")
        if not anthropic_key: missing.append("ANTHROPIC_API_KEY")
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
    return api_key, api_secret


async def main():
    try:
        # Validate environment variables
        api_key, api_secret = validate_env_vars()
        
        # Initialize the CrewAI toolkit
        toolkit = ExtendCrewAIToolkit(
            api_key=api_key,
            api_secret=api_secret,
            configuration=Configuration(
                scope=[
                    Scope(Product.VIRTUAL_CARDS, actions=Actions(read=True)),
                    Scope(Product.CREDIT_CARDS, actions=Actions(read=True)),
                    Scope(Product.TRANSACTIONS, actions=Actions(read=True)),
                ]
            )
        )

        # Configure the LLM
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

        # Example interaction with the agent
        print("Welcome to the Extend CrewAI Agent! Type 'quit' to exit.")
        while True:
            try:
                user_input = input("\nYour question: ").strip()
                if user_input.lower() == 'quit':
                    break
                
                # Update task description with user input
                query_task.description = f"Process and respond to this user query: {user_input}"
                
                # Run the crew
                result = crew.kickoff()
                print("Agent response:", result)
                
            except Exception as e:
                print(f"Error processing query: {str(e)}")
                print("Please try again or type 'quit' to exit.")
                
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")
        return


if __name__ == "__main__":
    asyncio.run(main())