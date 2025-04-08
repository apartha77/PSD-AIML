import os
import re
import json
import logging
from dotenv import load_dotenv
load_dotenv()

from sagemaker.predictor import retrieve_default

endpoint_name = "jumpstart-dft-deepseek-llm-r1-disti-20250408-101531"
predictor = retrieve_default(endpoint_name)
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

payload = {
    "messages": [
        {
            "role": "user",
            "content": "What is 1+1?"
        },
        {
            "role": "assistant",
            "content": "It's 2."
        },
        {
            "role": "user",
            "content": "Explain more!"
        }
    ],
    "max_tokens": 128
}
response = predictor.predict(payload)
print(response)

payload = {
    "messages": [
        {
            "role": "user",
            "content": "Create a Flappy Bird game in Python."
        }
    ],
    "max_tokens": 128
}
response = predictor.predict(payload)
print(response)