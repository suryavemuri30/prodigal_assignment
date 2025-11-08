# AI System for Payment Processing Call Transcripts

This project is a Streamlit web application designed to analyze call center transcripts from debt collection workflows. It leverages the OpenAI API to extract structured insights and validate payment information using advanced LLM-driven Tool Calling, as per the assignment requirements.

## Demo


*(**Note:** You should replace the placeholder URL above with a real screenshot of your running application.)*

## Features

-   **Task 1: Comprehensive Call Analysis**: Automatically extracts key information from call transcripts, including:
    -   Whether a payment was attempted.
    -   The customer's genuine intent to pay.
    -   Customer sentiment classification (Satisfied, Neutral, Frustrated, Hostile) with a descriptive summary.
    -   A detailed, multi-sentence performance review of the agent based on professionalism, patience, and problem-solving.
    -   A list of key timestamped events like disclosures, negotiations, and payment attempts.

-   **Task 2: Intelligent Payment Validation**: Implements true **LLM-driven Tool Calling** to:
    -   Extract payment credentials (cardholder name, card number, CVV, expiry, amount) from the conversation.
    -   Autonomously decide whether the extracted details are valid or invalid and select the appropriate failure reason.
    -   Automatically call an external API to validate the extracted information against ground truth data.

-   **Dynamic & Efficient UI**:
    -   A seamless, single-button workflow that runs both analysis and validation tasks.
    -   Uses Streamlit's session state to cache results, preventing redundant API calls and ensuring a fast user experience.
    -   Provides clear, user-friendly feedback for successful analyses, expected model behavior (e.g., no payment attempt found), and technical errors.

## Tech Stack

-   **Backend**: Python 3.10+
-   **Web Framework**: Streamlit
-   **AI/LLM**: OpenAI API (`gpt-4o-mini`)
-   **API Communication**: Requests
-   **Environment Management**: python-dotenv, venv

## Project Structure

The project is organized into a modular `app` package to separate concerns, making the code clean and maintainable.

```
/payment-transcript-analyzer
|-- /app
|   |-- __init__.py         # Marks 'app' as a Python package
|   |-- main.py             # The Streamlit UI and application entry point
|   |-- logic.py            # Handles all backend logic and API calls (OpenAI, Payment API)
|   |-- prompts.py          # Contains all system prompts and instructions for the LLM
|   |-- utils.py            # Helper functions (e.g., transcript formatting)
|-- .env                    # Stores the secret OpenAI API key (ignored by Git)
|-- .env.example            # Template for the .env file
|-- .gitignore              # Specifies files and directories to be ignored by Git
|-- requirements.txt        # Lists all Python dependencies
|-- README.md               # This file
```

## Setup and Installation

Follow these steps to get the application running on your local machine.

#### **Prerequisites**

-   Python 3.10 or higher
-   Git
-   An OpenAI API key
-   (For macOS users) Homebrew for installing system dependencies:
    ```bash
    brew install apache-arrow
    ```

#### **Installation Steps**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Create the environment file:**
    Copy the example file and then add your OpenAI API key.
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and paste your secret key:
    ```
    OPENAI_API_KEY="sk-..."
    ```

3.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Streamlit application:**
    ```bash
    streamlit run app/main.py
    ```
    The application should now be open and running in your web browser.

## How to Use the Application

1.  **Launch the app** using the command above.
2.  **Upload a transcript** using the file uploader in the sidebar, or paste the raw JSON content into the text area.
3.  **Click the "Analyze and Validate Payment" button.**
4.  The application will perform both Task 1 and Task 2. The results will appear on the main page, including the extracted information and the final API validation response.

## Design Decisions & Prompt Engineering Journey

This project required significant iterative refinement of the prompts to handle the nuances of the assignment and the behavior of the `gpt-4o-mini` model.

1.  **Initial Challenge (JSON Formatting)**: Early prompts resulted in the LLM returning conversational text around the JSON object, causing parsing errors.
    -   **Solution**: Implemented OpenAI's **JSON Mode** (`response_format={"type": "json_object"}`) and added explicit instructions in the prompt to *only* return a valid JSON object.

2.  **Challenge (`invalid_args` Error)**: The API rejected requests when the LLM used invalid placeholders (like `0` for `expiryMonth`) for missing data.
    -   **Initial Solution**: Instructed the LLM to use *plausible* placeholders (e.g., `1` for month).
    -   **Final Solution**: After reviewing the API schema, I discovered that many fields were **`nullable`**. The prompt and tool definition were completely refactored to **omit optional fields** if they were not present in the transcript, which is a much cleaner and more robust solution.

3.  **Challenge (Data Type Mismatch)**: The API rejected requests because the LLM extracted the `cvv` as a number (`852`) instead of the required string (`"852"`).
    -   **Solution**: Added a "Critical Data Formatting Rule" to the prompt to enforce that the `cvv` must always be a string.

4.  **Challenge (Missing Required Fields)**: The API rejected requests when a *required* field within the `credentials` object (like `cardNumber`) was missing.
    -   **Solution**: The final prompt makes a clear distinction: omit missing *optional* fields, but use the string `"N/A"` for missing *required* fields to ensure the payload is always schema-compliant.

5.  **Workflow Efficiency**: To create a seamless user experience and minimize costs, `st.session_state` was used to store API results. This ensures that the expensive LLM calls are only run once per transcript when the user clicks the button, and the results persist on the screen across interactions.

## Potential Future Improvements

-   **Batch Processing**: Add functionality to upload and process a folder of multiple transcripts at once.
-   **Analytics Dashboard**: Create a dashboard to visualize aggregated data from multiple calls (e.g., common customer sentiments, average agent performance).
-   **Direct Audio Support**: Integrate a transcription service (like OpenAI's Whisper) to allow users to upload audio files directly.
-   **Cost Tracking**: Implement a simple cost estimator to show the user the approximate cost of their OpenAI API calls.
