"""
Example implementation of an AI agent using the CrewAI framework.
"""

from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connecting to an OpenAI-compatible LLM
openai_llm = LLM(
    model="gpt-4",
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_base="https://api.openai.com/v1"
)

# Create a researcher agent
researcher_agent = Agent(
    role="Senior Data Researcher",
    goal="Uncover cutting-edge developments in AI",
    backstory="A seasoned researcher with a knack for uncovering the latest developments in AI.",
    verbose=True,
    llm=openai_llm
)

# Create a task for the researcher
research_task = Task(
    description="Conduct comprehensive research on the latest AI developments.",
    expected_output="A summary report highlighting key advancements in AI.",
    agent=researcher_agent,
    async_execution=True
)

# Create a crew with the researcher and task
crew = Crew(
    agents=[researcher_agent],
    tasks=[research_task],
    verbose=True
)

# Run the crew
result = crew.kickoff()
print(result)