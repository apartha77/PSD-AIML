# Basic operation with Bedrock using Converse API - without any interface
"""
Shows how to use the Converse API with Anthropic Claude 3 to generate conversation without any interface
"""

import logging
import boto3

from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Generate conversion using converse api
def generate_conversation(bedrock_client,
                          model_id,
                          system_prompts,
                          messages, tool_list):

    logger.info("Generating message with model %s", model_id)

    # Inference parameters to use.
    temperature = 0.5
    top_k = 200

    # Base inference parameters to use.
    inference_config = {"temperature": temperature}
    # Additional inference parameters to use.
    additional_model_fields = {"top_k": top_k}

    # Send the message.
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        #toolConfig={"tools": tool_list},
        additionalModelRequestFields=additional_model_fields
    )
    
    
    # Print token usage information
    if 'usage' in response:
        print("\nToken Usage:")
        print(f"Input tokens: {response['usage']['inputTokens']}")
        print(f"Output tokens: {response['usage']['outputTokens']}")
        print(f"Total tokens: {response['usage']['totalTokens']}")

    # Log token usage.
    token_usage = response['usage']
    logger.info("Input tokens: %s", token_usage['inputTokens'])
    logger.info("Output tokens: %s", token_usage['outputTokens'])
    logger.info("Total tokens: %s", token_usage['totalTokens'])
    logger.info("Stop reason: %s", response['stopReason'])

    return response

def create_bedrock_client(region_name="us-east-1"):
    """Create a Bedrock Runtime client"""
    session = boto3.Session()
    return session.client('bedrock-runtime', region_name=region_name)

# added teh tools in the basic to check how it can create the output as per the tool.
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

def main():
    """
    Entrypoint for model
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    model_id = "anthropic.claude-3-sonnet-20240229-v1:0" #can use any other model of choice
    
    # Get the tool list
    tool_list = get_tool_list()

    # Setup the system prompts and messages to send to the model.
    #system_prompts = [{"text": "You are an app that creates playlists for a radio station that plays rock and pop music. Only return song names and the artist."}]
    system_prompts = [{"text": "You are an AI assistant capable of creating Lambda functions and performing mathematical calculations. Use the provided tools when necessary."}]
    # Messae List for the conversation
    message_1 = {
        "role": "user",
        "content": [{"text":"Create a lamda function for dynamic list in python"}]#[{"text": "Create a list of 3 pop songs."}]
    }
    message_2 = {
        "role": "user",
        "content": [{"text": "Make sure the songs are by artists from the United Kingdom."}]
    }
    messages = []

    try:

        #bedrock_client = boto3.client(service_name='bedrock-runtime')
        bedrock_client = create_bedrock_client()

        # Start the conversation with the 1st message.
        messages.append(message_1)
        response = generate_conversation(
            bedrock_client, model_id, system_prompts, messages, tool_list)

        # Add the response message to the conversation.
        output_message = response['output']['message']
        messages.append(output_message)

        # Continue the conversation with the 2nd message.
        messages.append(message_2)
        response = generate_conversation(
            bedrock_client, model_id, system_prompts, messages, tool_list)

        output_message = response['output']['message']
        messages.append(output_message)

        # Show the complete conversation.
        for message in messages:
            print(f"Role: {message['role']}")
            for content in message['content']:
                print(f"Text: {content['text']}")
            print()

    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error("A client error occurred: %s", message)
        print(f"A client error occured: {message}")

    else:
        print(
            f"Finished generating text with model {model_id}.")


if __name__ == "__main__":
    main()
