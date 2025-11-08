import sys
import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.prompts import get_task_1_prompt, get_task_2_system_prompt
from app.utils import format_transcript

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PAYMENT_API_URL = "https://se-payment-verification-api.service.external.usea2.aws.prodigaltech.com/api/validate-payment"

def analyze_call_transcript(transcript_content):
    """
    Task 1: Analyzes the call transcript using OpenAI API.
    """
    formatted_transcript = format_transcript(transcript_content)
    prompt = get_task_1_prompt(formatted_transcript)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# app/logic.py (replace the two Task 2 functions)

def validate_payment_api_call(transcript_id, payment_valid, failure_reason, credentials, amount):
    """
    This is the actual tool function that the LLM will call.
    The patch is no longer needed as we now handle nullable fields correctly.
    """
    api_payload = {
        "id": transcript_id,
        "student_id": "70472200142",
        "payment_valid": payment_valid,
        "failure_reason": failure_reason,
        "credentials": credentials,
        "amount": amount,
    }
    
    headers = {"Content-Type": "application/json"}
    try:
        api_response = requests.post(PAYMENT_API_URL, json=api_payload, headers=headers)
        return {
            "api_response": api_response.json(),
            "status_code": api_response.status_code
        }
    except requests.RequestException as e:
        return {
            "api_response": {"error": "API request failed", "details": str(e)},
            "status_code": 500
        }

def run_payment_validation_flow(transcript_content, transcript_id):
    """
    Task 2: Orchestrates the LLM tool-calling flow.
    """
    formatted_transcript = format_transcript(transcript_content)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "validate_payment_api_call",
                "description": "Validates the extracted payment credentials by calling the external payment verification API.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transcript_id": {"type": "string"},
                        "payment_valid": {"type": "boolean"},
                        "failure_reason": {"type": "string"},
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "cardholderName": {"type": "string"},
                                "cardNumber": {"type": "string"},
                                "cvv": {"type": "string"},
                                "expiryMonth": {"type": "integer"},
                                "expiryYear": {"type": "integer"},
                            },
                            # REMOVED THE 'required' LIST HERE TO ALLOW OMITTING FIELDS
                        },
                        "amount": {"type": "number"},
                    },
                    "required": ["transcript_id", "payment_valid", "failure_reason", "credentials", "amount"]
                },
            },
        }
    ]

    messages = [
        {"role": "system", "content": get_task_2_system_prompt()},
        {"role": "user", "content": f"The transcript ID is '{transcript_id}'.\n\nTranscript:\n{formatted_transcript}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "validate_payment_api_call":
                api_result = validate_payment_api_call(**function_args)
                
                return {
                    "extracted_data": function_args,
                    **api_result
                }
        
        return {"error": "The LLM did not request a tool call."}

    except Exception as e:
        return {"error": str(e)}