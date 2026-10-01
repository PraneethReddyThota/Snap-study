import streamlit as st
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE


# Page configuration
st.set_page_config(
    page_title="Snap & Study AI",
    page_icon="📚",
    layout="centered",
)


# Gemini client
@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_gemini_client()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
        }
    ]


# Page title
st.title("📚 Snap & Study AI")
st.caption("Upload a question, diagram, or notes and learn it in simple language.")


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message["content"] != WELCOME_MESSAGE
        ):
            with st.expander("Copy explanation"):
                st.code(message["content"], language="markdown")


# Chat input
prompt = st.chat_input(
    "Ask a study question...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)


if prompt:
    user_text = prompt.text
    uploaded_file = prompt.files[0] if prompt.files else None

    # Display and save the user's text
    if user_text:
        with st.chat_message("user"):
            st.markdown(user_text)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_text,
            }
        )

    # Prepare content for Gemini
    contents = [
        types.Part.from_text(text=SYSTEM_PROMPT),
    ]

    if user_text:
        contents.append(types.Part.from_text(text=user_text))

    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=uploaded_file.type,
            )
        )

    # Ask Gemini once
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=contents,
                )
                answer = response.text or "Gemini returned an empty response."

            st.markdown(answer)

    except Exception as error:
        if "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error):
            st.error(
                "Gemini's request limit has been reached. "
                "Wait for it to reset, then try again."
            )
        else:
            st.error("Gemini couldn't answer. Please try again later.")
        st.stop()

    # Save the new explanation for chat history and email
    st.session_state.latest_answer = answer
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# Email the latest explanation
if st.session_state.get("latest_answer"):
    with st.expander("Email this explanation"):
        with st.form("email_explanation_form"):
            recipient = st.text_input("Recipient email address")
            send_email = st.form_submit_button("Send explanation")

        if send_email:
            if not recipient.strip():
                st.error("Enter a recipient email address.")
            else:
                try:
                    import smtplib
                    import ssl
                    from email.message import EmailMessage
                    from markdown_it import MarkdownIt

                    gmail_address = st.secrets["gmail"]["address"]
                    gmail_app_password = st.secrets["gmail"]["app_password"]

                    explanation = st.session_state.latest_answer
                    html_explanation = MarkdownIt(
                        "commonmark",
                        {"html": False},
                    ).render(explanation)

                    message = EmailMessage()
                    message["Subject"] = "Your Snap & Study explanation"
                    message["From"] = gmail_address
                    message["To"] = recipient.strip()
                    message.set_content(explanation)
                    message.add_alternative(
                        html_explanation,
                        subtype="html",
                    )

                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(
                        "smtp.gmail.com",
                        465,
                        context=context,
                    ) as smtp:
                        smtp.login(gmail_address, gmail_app_password)
                        smtp.send_message(message)

                    st.success("Explanation sent.")

                except KeyError:
                    st.error(
                        "Email is not configured yet. Add your Gmail address "
                        "and App Password to .streamlit/secrets.toml."
                    )
                except Exception:
                    st.error(
                        "Email could not be sent. Check your Gmail settings "
                        "and recipient address, then try again."
                    )