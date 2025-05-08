"""" Create Agents to Research and Write an Article
using multi-agent crewAI framework.
install the following
!pip install crewai==0.28.8 crewai_tools==0.1.6 langchain_community==0.0.29
"""

# Warning control
import os
# import boto3
# import botocore
import logging
from crewai import LLM, Agent, Crew, Process, Task
#from crewai import Agent, Task, Crew

# import warnings
# warnings.filterwarnings('ignore')

# openai_api_key = get_openai_api_key()
# os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""Creating Agents - Define Agents, and provide them a role, goal and backstory.
It has been seen that LLMs perform better when they are role playing.
"""
logger.info("Assign LLMs")

bedrock_MICRO_nova = LLM(model="bedrock/us.amazon.nova-micro-v1:0")
bedrock_LITE_nova = LLM(model="bedrock/us.amazon.nova-lite-v1:0")
bedrock_PRO_nova = LLM(model="bedrock/us.amazon.nova-pro-v1:0")

logger.info("Planner Agent")
planner = Agent(
    role="Content Planner",
    goal="Plan engaging and factually accurate content on {topic}",
    backstory="You're working on planning a blog article "
              "about the topic: {topic}."
              "You collect information that helps the "
              "audience learn something "
              "and make informed decisions. "
              "Your work is the basis for "
              "the Content Writer to write an article on this topic.",
    allow_delegation=False,
    llm = bedrock_MICRO_nova,
	verbose=True
)

logger.info("Writer Agent")
writer = Agent(
    role="Content Writer",
    goal="Write insightful and factually accurate "
         "opinion piece about the topic: {topic}",
    backstory="You're working on a writing "
              "a new opinion piece about the topic: {topic}. "
              "You base your writing on the work of "
              "the Content Planner, who provides an outline "
              "and relevant context about the topic. "
              "You follow the main objectives and "
              "direction of the outline, "
              "as provide by the Content Planner. "
              "You also provide objective and impartial insights "
              "and back them up with information "
              "provide by the Content Planner. "
              "You acknowledge in your opinion piece "
              "when your statements are opinions "
              "as opposed to objective statements.",
    allow_delegation=False,
    llm = bedrock_LITE_nova, 
    verbose=True
)

logger.info("Editor Agent")
editor = Agent(
    role="Editor",
    goal="Edit a given blog post to align with "
         "the writing style of the organization. ",
    backstory="You are an editor who receives a blog post "
              "from the Content Writer. "
              "Your goal is to review the blog post "
              "to ensure that it follows journalistic best practices,"
              "provides balanced viewpoints "
              "when providing opinions or assertions, "
              "and also avoids major controversial topics "
              "or opinions when possible.",
    allow_delegation=False,
    llm = bedrock_PRO_nova,
    verbose=True
)

logger.info("Agents created")

""" Creating Tasks - Define Tasks for the agents, and provide them a description, expected_output and agent.
"""
logger.info("Creating Plan Tasks - for Planner Agent")
plan = Task(
    description=(
        "1. Prioritize the latest trends, key players, "
            "and noteworthy news on {topic}.\n"
        "2. Identify the target audience, considering "
            "their interests and pain points.\n"
        "3. Develop a detailed content outline including "
            "an introduction, key points, and a call to action.\n"
        "4. Include SEO keywords and relevant data or sources."
    ),
    expected_output="A comprehensive content plan document "
        "with an outline, audience analysis, "
        "SEO keywords, and resources.",
    agent=planner,
)

logger.info("Creating Write Tasks - for Planner Writer")
write = Task(
    description=(
        "1. Use the content plan to craft a compelling "
            "blog post on {topic}.\n"
        "2. Incorporate SEO keywords naturally.\n"
		"3. Sections/Subtitles are properly named "
            "in an engaging manner.\n"
        "4. Ensure the post is structured with an "
            "engaging introduction, insightful body, "
            "and a summarizing conclusion.\n"
        "5. Proofread for grammatical errors and "
            "alignment with the brand's voice.\n"
    ),
    expected_output="A well-written blog post "
        "in markdown format, ready for publication, "
        "each section should have 2 or 3 paragraphs.",
    agent=writer,
)

logger.info("Creating Edit Tasks - for Planner Editor")
edit = Task(
    description=("Proofread the given blog post for "
                 "grammatical errors and "
                 "alignment with the brand's voice."),
    expected_output="A well-written blog post in markdown format, "
                    "ready for publication, "
                    "each section should have 2 or 3 paragraphs.",
    agent=editor
)

logger.info("Tasks created")
logger.info("Creating Crew")
""" Now Create the Crew - crew of Agents, pass the tasks to be performed by those agents
"""
crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan, write, edit],
    process = Process.sequential,
    verbose= True
)


""" Running the Crew
"""
logger.info("Running the Crew")
topic = "role of agentic ai in insurance"
#result = crew.kickoff(inputs={"topic": "Artificial Intelligence"})
result = crew.kickoff(inputs={"topic": topic})
print(result)

