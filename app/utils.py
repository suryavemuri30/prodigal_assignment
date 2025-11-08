# app/utils.py
import json

def format_transcript(transcript_json):
    """
    Formats the JSON transcript into a readable string.
    """
    try:
        transcript_data = json.loads(transcript_json)
        formatted_lines = []
        for entry in transcript_data:
            formatted_lines.append(f"{entry['role']}: {entry['utterance']}")
        return "\n".join(formatted_lines)
    except (json.JSONDecodeError, TypeError):
        return transcript_json # Return as is if not a valid JSON string