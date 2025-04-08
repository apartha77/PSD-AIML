
import boto3
from sagemaker.predictor import retrieve_default
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Set the SM Jumstart endpoint")
endpoint_name = "jumpstart-dft-deepseek-llm-r1-disti-20250401-105354"
predictor = retrieve_default(endpoint_name)
logger.info("Set the query")
payload = {
    "messages": [
        {
            "role": "user",
            "content": "what is 10+1."
        }
    ],
    "max_tokens": 128
}

response = predictor.predict(payload)
print(response)

# payload = {
#     "messages": [
#         {
#             "role": "user",
#             "content": "What is 1+1?"
#         },
#         {
#             "role": "assistant",
#             "content": "It's 2."
#         },
#         {
#             "role": "user",
#             "content": "Explain more!"
#         }
#     ],
#     "max_tokens": 128
# }
# response = predictor.predict(payload)
# print(response)
# payload = {
#     "messages": [
#         {
#             "role": "user",
#             "content": "Create a Flappy Bird game in Python."
#         }
#     ],
#     "max_tokens": 128
# }
# response = predictor.predict(payload)
# print(response)