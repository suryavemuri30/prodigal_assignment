# app/main.py (replace the entire file for clarity)

import sys
import os
import streamlit as st
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.logic import analyze_call_transcript, run_payment_validation_flow

st.set_page_config(layout="wide")

# Initialize session state
if 'task1_results' not in st.session_state:
    st.session_state.task1_results = None
if 'task2_results' not in st.session_state:
    st.session_state.task2_results = None
if 'current_transcript' not in st.session_state:
    st.session_state.current_transcript = ""
# ADD THIS LINE to store the transcript ID
if 'transcript_id' not in st.session_state:
    st.session_state.transcript_id = ""

st.title("AI Systems for Payment Processing Call Transcripts")

st.sidebar.header("Upload Transcript")
uploaded_file = st.sidebar.file_uploader("Choose a JSON transcript file", type="json")
transcript_content_area = st.sidebar.text_area("Or paste transcript content here", height=300)

transcript_content = ""
transcript_id = ""

if uploaded_file is not None:
    transcript_content = uploaded_file.getvalue().decode("utf-8")
    # Extract the filename without the .json extension
    transcript_id = os.path.splitext(uploaded_file.name)[0]
else:
    transcript_content = transcript_content_area
    # Provide a default ID for pasted text
    transcript_id = "pasted-transcript-test"

# If a new transcript is loaded, clear the previous results
if transcript_content and transcript_content != st.session_state.current_transcript:
    st.session_state.task1_results = None
    st.session_state.task2_results = None
    st.session_state.current_transcript = transcript_content
    st.session_state.transcript_id = transcript_id # Store the new ID
    st.rerun()

if st.session_state.current_transcript:
    st.header("Call Transcript")
    try:
        transcript_json = json.loads(st.session_state.current_transcript)
        st.json(transcript_json)
    except (json.JSONDecodeError, TypeError):
        st.text(st.session_state.current_transcript)

    st.header("Run Analysis")
    if st.button("Analyze and Validate Payment", type="primary"):
        with st.spinner("Performing call analysis (Task 1)..."):
            st.session_state.task1_results = analyze_call_transcript(st.session_state.current_transcript)
        
        with st.spinner("LLM is processing and calling the validation tool (Task 2)..."):
            # Pass the transcript ID to the logic function
            st.session_state.task2_results = run_payment_validation_flow(
                st.session_state.current_transcript,
                st.session_state.transcript_id
            )

# --- Display Results ---
if st.session_state.task1_results:
    # ... (This part remains the same)
    st.header("Task 1: Call Analysis Results")
    if "error" in st.session_state.task1_results:
        st.error(f"An error occurred in Task 1: {st.session_state.task1_results['error']}")
    else:
        st.json(st.session_state.task1_results)

if st.session_state.task2_results:
    # ... (This part remains the same)
    st.header("Task 2: Payment Validation Results")
    if "error" in st.session_state.task2_results:
        if "did not request a tool call" in st.session_state.task2_results['error']:
            st.info("✅ Analysis Complete: No payment attempt was detected in this transcript, so the validation API was not called.")
        else:
            st.error(f"An error occurred in Task 2: {st.session_state.task2_results['error']}")
    else:
        st.subheader("LLM Extracted Information (Arguments for Tool Call)")
        st.json(st.session_state.task2_results.get("extracted_data", {}))
        st.subheader("API Validation Response")
        api_response = st.session_state.task2_results.get("api_response", {})
        if st.session_state.task2_results.get("status_code") == 200 and api_response.get("success"):
            st.success("Correct")
        else:
            st.error("Incorrect")
        st.json(api_response)

st.sidebar.markdown("---")
st.sidebar.info("This app is a solution to the assignment. For more details, visit the [GitHub Repository](https://github.com/your-repo-link).")