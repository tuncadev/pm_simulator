import streamlit as st
import openai
from openai import OpenAI
import time

# Load API key and assistant ID from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]
assistant_id = st.secrets["openai"]["assistant_id"]

# Function to get response from OpenAI assistant
def get_assistant_response(prompt):
    client = OpenAI(api_key=api_key)

    # Create a new thread
    thread = client.beta.threads.create()

    # Add user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    # Create a new run for the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    # Wait for the run to complete
    while run.status != "completed":
        time.sleep(1)  # Sleep for a while before checking the status again
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    # Retrieve messages from the thread
    message_response = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    messages = message_response.data
    latest_message = next((m for m in messages if m.role == "assistant"), None)

    if latest_message:
        response_content = latest_message.content[0].text.value  # Access the text content
        return response_content
    else:
        return "No response from the assistant."

st.title("HYS Enterprise - PM Training Simulator", anchor=False)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your message here"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    response = get_assistant_response(prompt)

    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Display assistant message in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)