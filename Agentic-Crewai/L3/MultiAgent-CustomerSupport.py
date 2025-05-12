""" L3: Multi-agent Customer Support - Provide support from the Website pages & KB
Six key elements Agents perform better:
1. Role Playing 2. Focus 3. Tools 4. Cooperation 5. Guardrails 6. Memory
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

#bedrock_MICRO_nova = LLM(model="bedrock/us.amazon.nova-micro-v1:0")
bedrock_LITE_nova = LLM(model="bedrock/us.amazon.nova-lite-v1:0")
#bedrock_PRO_nova = LLM(model="bedrock/us.amazon.nova-pro-v1:0")

"""Creating Agents - Define Agents, and provide them a role, goal and backstory.

"""
logger.info("Agent Creation")
# Agent Support Agent
# This agent can delegate work to another agent
support_agent = Agent(
    role="Senior Support Representative",
	goal="Be the most friendly and helpful "
        "support representative in your team",
	backstory=(
		"You work at crewAI (https://crewai.com) and "
        " are now working on providing "
		"support to {customer}, a super important customer "
        " for your company."
		"You need to make sure that you provide the best support!"
		"Make sure to provide full complete answers, "
        " and make no assumptions."
	),
	allow_delegation=False,
	llm = bedrock_LITE_nova,
	verbose=True
)


#Agent Quality Assurance
support_quality_assurance_agent = Agent(
	role="Support Quality Assurance Specialist",
	goal="Get recognition for providing the "
    "best support quality assurance in your team",
	backstory=(
		"You work at crewAI (https://crewai.com) and "
        "are now working with your team "
		"on a request from {customer} ensuring that "
        "the support representative is "
		"providing the best support possible.\n"
		"You need to make sure that the support representative "
        "is providing full"
		"complete answers, and make no assumptions."
	),
	llm = bedrock_LITE_nova,
	verbose=True
)

#Tools - Import Tools
from crewai_tools import SerperDevTool, \
                         ScrapeWebsiteTool, \
                         WebsiteSearchTool
                         
docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://docs.crewai.com/how-to/Creating-a-Crew-and-kick-it-off/"
)

#Tasks - Inquiry Resolution Tasks for Support Agent
inquiry_resolution = Task(
    description=(
        "{customer} just reached out with a super important ask:\n"
	    "{inquiry}\n\n"
        "{person} from {customer} is the one that reached out. "
		"Make sure to use everything you know "
        "to provide the best support possible."
		"You must strive to provide a complete "
        "and accurate response to the customer's inquiry."
    ),
    expected_output=(
	    "A detailed, informative response to the "
        "customer's inquiry that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
		"leaving no questions unanswered, and maintain a helpful and friendly "
		"tone throughout."
    ),
	tools=[docs_scrape_tool],
    agent=support_agent,
)

#Task for Quality Assurance Agent - It will review the work of Support Agent
quality_assurance_review = Task(
    description=(
        "Review the response drafted by the Senior Support Representative for {customer}'s inquiry. "
        "Ensure that the answer is comprehensive, accurate, and adheres to the "
		"high-quality standards expected for customer support.\n"
        "Verify that all parts of the customer's inquiry "
        "have been addressed "
		"thoroughly, with a helpful and friendly tone.\n"
        "Check for references and sources used to "
        " find the information, "
		"ensuring the response is well-supported and "
        "leaves no questions unanswered."
    ),
    expected_output=(
        "A final, detailed, and informative response "
        "ready to be sent to the customer.\n"
        "This response should fully address the "
        "customer's inquiry, incorporating all "
		"relevant feedback and improvements.\n"
		"Don't be too formal, we are a chill and cool company "
	    "but maintain a professional and friendly tone throughout."
    ),
    agent=support_quality_assurance_agent,
)

#from crewai import Memory
#objmemory = Memory()

#Create Crew
crew = Crew(
  agents=[support_agent, support_quality_assurance_agent],
  tasks=[inquiry_resolution, quality_assurance_review],
  verbose=True #,
  #memory=True
)

#Run Crew
inputs = {
    "customer": "DeepLearningAI",
    "person": "Andrew Ng",
    "inquiry": "I need help with setting up a Crew "
               "and kicking it off, specifically "
               "how can I add memory to my crew? "
               "Can you provide guidance?"
}
result = crew.kickoff(inputs=inputs)