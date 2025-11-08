# app/prompts.py

# get_task_1_prompt remains unchanged
def get_task_1_prompt(transcript):
    """
    Returns the prompt for Task 1: Call Analysis.
    """
    return f"""
    Analyze the following call transcript and extract the required information.

    **CRITICAL INSTRUCTIONS:**
    1. For the `agent_performance` field, provide a detailed assessment of 2-3 sentences. You MUST consider the agent's professionalism, patience, problem-solving skills, and communication clarity.
    2. The timestamp for events MUST be in the "M:SS" format (e.g., "0:45", "2:15").
    3. Your response MUST be a single, valid JSON object and nothing else.
    4. Do NOT include any explanatory text, conversational wrappers, or markdown formatting like ```json.

    **Transcript:**
    {transcript}

    **Required JSON Structure:**
    {{
      "payment_attempted": <Boolean>,
      "customer_intent": <Boolean>,
      "customer_sentiment": {{
        "classification": "<Satisfied"|"Neutral"|"Frustrated"|"Hostile">,
        "description": "<String>"
      }},
      "agent_performance": "<A detailed 2-3 sentence assessment of the agent's performance>",
      "timestamped_events": [
        {{
          "timestamp": "M:SS",
          "event_type": "<'disclosure'|'offer_negotiation'|'payment_setup_attempt'|'consumer_frustration_or_hostility'>",
          "description": "<String>"
        }}
      ]
    }}
    """

def get_task_2_system_prompt():
    """
    Returns the system prompt for Task 2: Payment Validation.
    """
    return """
    You are an expert AI assistant performing a high-stakes task. Your goal is to extract payment credential details from a call transcript with 100% accuracy and then call the payment validation tool.

    **CRITICAL DATA FORMATTING RULES:**
    1.  **Convert Words to Digits:** You MUST convert all numbers spoken as words into their digit equivalents.
    2.  **No Dashes or Spaces:** Card numbers must be a continuous string of digits.
    3.  **Handle Monetary Values Precisely:** The `amount` field must be a number (integer or float). You MUST include cents as a decimal.
    4.  **CVV is a String:** The `cvv` code MUST be a string (e.g., "852").

    **CRITICAL LOGIC FOR MISSING DATA:**
    - If the `credentials` object is included, it MUST contain `cardholderName` and `cardNumber`.
    - If `cardholderName` or `cardNumber` are not mentioned in the transcript, you MUST use the string "N/A" as a placeholder for that required field.
    - For optional (nullable) fields like `cvv`, `expiryMonth`, and `expiryYear`, if they are not mentioned, **omit them entirely** from the `credentials` object.

    **Process:**
    1.  Read the transcript and apply all critical formatting and logic rules.
    2.  Determine the `failure_reason`. If no payment attempt was made or details were refused, use 'invalid_args'. If an attempt was made with flawed data, use the specific reason (e.g., 'invalid_card_length').
    3.  You MUST call the tool on every transcript. Construct the final tool call.

    **Failure Reasons List:**
    'expired_card', 'invalid_card_length', 'invalid_cvv_length', 'invalid_expiry_month', 'invalid_luhn', 'masked_card_number', 'data_mismatch', 'invalid_args'. If no failure is apparent, use 'none'.
    """