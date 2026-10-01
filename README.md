# Snap & Study AI

Snap & Study AI helps students understand study questions. Type a question or upload an image, get a plain-language explanation from Gemini, then email the explanation to yourself.

## Features

- Accepts text questions and uploaded study images.
- Generates step-by-step explanations with Gemini.
- Sends the latest explanation by Gmail.

## Requirements

- Python 3.11 or later
- A Gemini API key
- A Gmail App Password for the sending account

## Setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml` and add your own credentials:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"

   [gmail]
   address = "your-sending-gmail-address"
   app_password = "your-gmail-app-password"
   ```

   Use a Gmail App Password, not your regular Gmail password. Never commit `secrets.toml` or share its contents.

4. Start the app:

   ```powershell
   streamlit run app.py
   ```

## Project files

- `app.py` — Streamlit app and Gemini/email actions
- `prompts.py` — Study assistant prompt and welcome message
- `requirements.txt` — Python dependencies
- `.streamlit/secrets.toml.example` — Credential template; contains no real credentials