"""Objective is to run the code through the command line, no interface is needed.
We'll use Amazon Bedrock's Converse API to build an agentic workflow with multiple tools.
"""
import json
import math
import os
from typing import List

import boto3
import utils as lambda_helpers
from botocore.exceptions import ClientError

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("LAMBDA_ROLE"))
# Assign the environment variables for testing 
""" put the variables and values in .env file and access the by using 
from dotenv import load_dotenv
load_dotenv()
"""
# Retrieve environment variables
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
#LAMBDA_ROLE = os.environ["LAMBDA_ROLE"]
#S3_BUCKET = os.environ["S3_BUCKET"]
LAMBDA_ROLE = os.getenv("LAMBDA_ROLE")
S3_BUCKET = os.getenv("S3_BUCKET")
REGION = "us-east-1"

def create_bedrock_client(region_name="us-east-1"):
    """Create a Bedrock Runtime client"""
    session = boto3.Session()
    return session.client('bedrock-runtime', region_name=region_name)


def initialize_clients():
    """Initialize and return the Lambda, and S3 clients."""
    session = boto3.Session()
    lambda_client = session.client("lambda", region_name=REGION)
    s3 = session.client("s3", region_name=REGION)
    return lambda_client, s3


def get_tool_list():
    """Define and return the tool list for the LLM to use. These tools will be created dynamically, 
    example crete lambda function and deploy python code will be dynamically generated """
    return [
        {
            "toolSpec": {
                "name": "cosine",
                "description": "Calculate the cosine of x.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "number",
                                "description": "The number to pass to the function.",
                            }
                        },
                        "required": ["x"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "create_lambda_function",
                "description": "Create and deploy a Lambda function.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Python code for the Lambda function.",
                            },
                            "function_name": {
                                "type": "string",
                                "description": "The name of the Lambda function.",
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of the Lambda function.",
                            },
                            "has_external_python_libraries": {
                                "type": "boolean",
                                "description": "Whether the function uses external Python libraries.",
                            },
                            "external_python_libraries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of external Python libraries to include.",
                            },
                        },
                        "required": [
                            "code",
                            "function_name",
                            "description",
                            "has_external_python_libraries",
                            "external_python_libraries",
                        ],
                    }
                },
            }
        },
    ]


def query_llm(tools, message_list, system_prompt, count):
    """ call bedrock-runtime.converse api and provide the required parameters. This function handles communication with the LLM (Claude 3 Sonnet) through Amazon Bedrock, allowing for:
1. Conversation management 2. Tool usage 3. System prompt configuration  """
    try:
        # Initialize the Bedrock Runtime client
        client = create_bedrock_client()
        
        # Format the messages according to the API structure
        # messages = [
        #     {
        #         "role": "user",
        #         "content": [
        #             {
        #                 "text": "Create a Lambda function that calculates the factorial of a number."
        #             }
        #         ]
        #     }
        # ]
        
        # Set up inference configuration
        inference_config = {
            "temperature": 0.7,
            "topP": 0.9,
            "maxTokens": 1000 #512
        }
        
        
        print(f"reached???{count}")
        print(json.dumps(tools, indent=4))
       
    
        # Call the converse operation
        response = client.converse(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Use appropriate model ID anthropic.claude-3-5-sonnet-20241022-v2:0
            messages=message_list,
            inferenceConfig=inference_config,
            toolConfig={"tools": tools},
            system=[{"text": system_prompt}]
        )
        
        """ Printing the output message, can pass the response and print it from the called function too """
        # Extract and print the response
        if response and 'output' in response:
            assistant_message = response['output']['message']
            response_text = assistant_message['content'][0]['text']
            #print(f"From Response --> Print Assistnat Message{assistant_message}")
            #print(f"From Response --> Assistant's response:", response_text)
            
            # Print token usage information
            if 'usage' in response:
                print("\nToken Usage:")
                print(f"Input tokens: {response['usage']['inputTokens']}")
                print(f"Output tokens: {response['usage']['outputTokens']}")
                print(f"Total tokens: {response['usage']['totalTokens']}")
        
        return response
        
    except Exception as e:
        print(f"Error during conversation: {e}")
        

def create_lambda_function(
    lambda_client,
    s3,
    code: str,
    function_name: str,
    description: str,
    has_external_python_libraries: bool,
    external_python_libraries: List[str],
) -> str:
    """
    Creates and deploys a Lambda Function, based on what the customer requested.
    Returns the name of the created Lambda function
    """
    runtime = "python3.12"
    handler = "lambda_function.handler"

    # Create a zip file for the code
    if has_external_python_libraries:
        zipfile = lambda_helpers.create_deployment_package_with_dependencies(
            code, function_name, f"{function_name}.zip", external_python_libraries
        )
    else:
        zipfile = lambda_helpers.create_deployment_package_no_dependencies(
            code, function_name, f"{function_name}.zip"
        )

    try:
        # Upload zip file
        zip_key = f"lambda_resources/{function_name}.zip"
        # Upload the file in S3
        s3.upload_file(zipfile, S3_BUCKET, zip_key)
        print(f"Uploaded zip to {S3_BUCKET}/{zip_key}")
        
        #print(f"before lambda create function-----------$$$-->")
        #Create the lambda function based on the code zip uploaded in S3
        response = lambda_client.create_function(
            Code={
                "S3Bucket": S3_BUCKET,
                "S3Key": zip_key,
            },
            Description=description,
            FunctionName="psd"+function_name,
            Handler=handler,
            Timeout=30,
            Publish=True,
            Role=LAMBDA_ROLE,
            Runtime=runtime,
        )
        print("Lambda function created successfully")
        #print(f" The response from lambda client creation function ----$$$----> {response}")
        #Create the final response for user along with the lambda function details
        deployed_function = response["FunctionName"]
        user_response = f"The function {deployed_function} has been deployed to the customer's AWS account. I will now provide my final answer to the customer on how to invoke the {deployed_function} function with boto3 and print the result."
        return user_response
    except ClientError as e:
        print(e)
        return f"Error: {e}\n Let me try again..."


def process_llm_response(response_message, lambda_client, s3):
    """Process the LLM's response, handling tool usage and text output.
    gets the response from llm, creates the required function based on the tools - 
    here two tools 1. calculate cosine 2. lambda function.
    """
    response_content_blocks = response_message["content"]
    follow_up_content_blocks = []

    for content_block in response_content_blocks:
        if "toolUse" in content_block:
            tool_use_block = content_block["toolUse"]
            tool_use_name = tool_use_block["name"]
            print(f"Using tool {tool_use_name}")
            if tool_use_name == "cosine":
                tool_result_value = math.cos(tool_use_block["input"]["x"])
                print(f"Cosine result: {tool_result_value}")
                follow_up_content_blocks.append(
                    {
                        "toolResult": {
                            "toolUseId": tool_use_block["toolUseId"],
                            "content": [{"json": {"result": tool_result_value}}],
                        }
                    }
                )
            elif tool_use_name == "create_lambda_function":
                result = create_lambda_function(
                    lambda_client,
                    s3,
                    tool_use_block["input"]["code"],
                    tool_use_block["input"]["function_name"],
                    tool_use_block["input"]["description"],
                    tool_use_block["input"]["has_external_python_libraries"],
                    tool_use_block["input"]["external_python_libraries"],
                )
                print(f"Lambda function creation result: {result}")
                follow_up_content_blocks.append(
                    {
                        "toolResult": {
                            "toolUseId": tool_use_block["toolUseId"],
                            "content": [{"json": {"result": result}}],
                        }
                    }
                )
        elif "text" in content_block:
            print(f"LLM response: {content_block['text']}")

    return follow_up_content_blocks


def main():
    # Initialize the AWS clients
    lambda_client, s3 = initialize_clients()
    #print("initialize_clients executed")
    # Get the tool list
    tool_list = get_tool_list()
    #print("tool list executed")
    #Create the initial message, will add more to the list. 
    message_list  = [
        {
            "role": "user",
            "content": [
                {
                    "text": "Create a Lambda function that calculates the factorial of a number."
                }
            ]
        }
        #,
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "text": "What is the cosine of 45 degrees?"
        #             }
        #     ]
        # }
    ]

    # Set the system prompt
    #system_prompt = "You are an AI assistant capable of creating Lambda functions and performing mathematical calculations. Use the provided tools when necessary."
    system_prompt = "You are an assistant capable of creating responses"
    #Make the initial request to the LLM
    response = query_llm(tool_list,message_list, system_prompt,"first")
    response_message = response["output"]["message"]
    print(json.dumps(response_message, indent=4))
    message_list.append(response_message)
    
    #follow_up_content_blocks=""

    # Process the LLM's response
    follow_up_content_blocks = process_llm_response(response_message, lambda_client, s3)
    
    #print(f" check follow_up_content_blocks before follow-up --------------> print the follow up{follow_up_content_blocks}" )

    # If there are follow-up content blocks, make another request to the LLM
    if follow_up_content_blocks:
        follow_up_message = {
            "role": "user",
            "content": follow_up_content_blocks,
        }
        message_list.append(follow_up_message)
        response = query_llm(tool_list, message_list, system_prompt,"second")
        response_message = response["output"]["message"]
        print(json.dumps(response_message, indent=4))
        message_list.append(response_message)
        # Process the final response
        process_llm_response(response_message, lambda_client, s3)
    
    #finally all working

if __name__ == "__main__":
    main()
