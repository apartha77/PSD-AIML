# wher is the code 

import boto3

def create_bedrock_client(region_name="us-east-1"):
    """
    Create an Amazon Bedrock runtime client.
    
    Args:
        region_name (str): AWS region name where Bedrock is available
        
    Returns:
        boto3.client: Bedrock runtime client
    """
    print(boto3.__version__) 
    # Create a session with AWS credentials
    session = boto3.Session()
   
    
    # Create the Bedrock runtime client
    bedrock = session.client(
        service_name='bedrock-runtime',
        region_name=region_name
    )
    
    return bedrock

# Example usage:
if __name__ == "__main__":
    try:
        bedrock_client = create_bedrock_client()
        print("Successfully created Bedrock runtime client")
    except Exception as e:
        print(f"Error creating Bedrock client: {e}")


#----------------
