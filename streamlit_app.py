import streamlit as st
import os
import datetime
from dotenv import load_dotenv


# Function to load and apply custom CSS
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Function to set page configuration
def set_page_config():
    st.set_page_config(
        page_title="DualMind",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def streamlit_interface(conversation, initial_prompt):
    set_page_config()
    load_css("style/custom.css")

    st.markdown(
        '<h1 class="main-title">🤖 DualMind</h1>', unsafe_allow_html=True
    )

    # Sidebar for customization
    st.sidebar.title("🛠️ Settings")

    # Load default values from .env
    load_dotenv()
    default_endpoint = os.getenv("OLLAMA_ENDPOINT")
    default_model_1 = os.getenv("MODEL_1")
    default_model_2 = os.getenv("MODEL_2")

    # Sidebar for customization
    ollama_endpoint = st.sidebar.text_input("Ollama Endpoint", value=default_endpoint)

    # Update the OllamaClient endpoint
    conversation.ollama_client.endpoint = ollama_endpoint

    # Fetch available models
    try:
        available_models = conversation.ollama_client.get_available_models()
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        available_models = []

    # Model selection dropdowns
    model_1 = st.sidebar.selectbox(
        "Model 1",
        options=available_models,
        index=(
            available_models.index(default_model_1)
            if default_model_1 in available_models
            else 0
        ),
    )
    model_2 = st.sidebar.selectbox(
        "Model 2",
        options=available_models,
        index=(
            available_models.index(default_model_2)
            if default_model_2 in available_models
            else 0
        ),
    )

    # System prompt customization
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Customize System Prompt 1"):
            system_prompt_1 = st.text_area(
                "System Prompt 1", value=conversation.system_prompt_1, height=150
            )
            if st.button("Save Prompt 1"):
                with open("system_prompt_1.txt", "w") as f:
                    f.write(system_prompt_1)
                st.success("System Prompt 1 saved!")

    with col2:
        with st.expander("Customize System Prompt 2"):
            system_prompt_2 = st.text_area(
                "System Prompt 2", value=conversation.system_prompt_2, height=150
            )
            if st.button("Save Prompt 2"):
                with open("system_prompt_2.txt", "w") as f:
                    f.write(system_prompt_2)
                st.success("System Prompt 2 saved!")

    # Update conversation with new settings
    conversation.model_1 = model_1
    conversation.model_2 = model_2
    conversation.system_prompt_1 = system_prompt_1
    conversation.system_prompt_2 = system_prompt_2

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_message" not in st.session_state:
        st.session_state.current_message = initial_prompt

    # Add this new section for customizing the initial message
    initial_message = st.text_area(
        "Customize initial message:", value=st.session_state.current_message
    )
    if st.button("Set Initial Message"):
        st.session_state.current_message = initial_message
        st.success("Initial message updated!")

    if "exchange_count" not in st.session_state:
        st.session_state.exchange_count = 0

    # Update the chat message display
    for message in st.session_state.messages:
        with st.chat_message(
            message["role"], avatar="🧑" if message["role"] == "user" else "🤖"
        ):
            st.markdown(
                f'<div class="chat-message {"user-message" if message["role"] == "user" else "assistant-message"}">{message["content"]}</div>',
                unsafe_allow_html=True,
            )

    num_exchanges = st.number_input(
        "Number of exchanges", min_value=1, max_value=10, value=3
    )

    if st.button("Generate Responses"):
        with st.spinner("Generating responses..."):
            for _ in range(num_exchanges):
                response = conversation.get_conversation_response(
                    st.session_state.current_message
                )
                model_name, content = response.split("\n", 1)

                avatar = "🔵" if model_name == model_1 else "🟢"
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"**{model_name}**\n\n{content}",
                        "avatar": avatar,
                    }
                )
                st.session_state.current_message = content
                st.session_state.exchange_count += 1

                with st.chat_message("assistant", avatar=avatar):
                    st.markdown(f"**{model_name}**\n\n{content}")

    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.current_message = (
            initial_message  # Use the customized initial message here
        )
        st.session_state.exchange_count = 0
        conversation.current_model = conversation.model_1
        conversation.current_system_prompt = conversation.system_prompt_1

    st.write(f"Total exchanges: {st.session_state.exchange_count}")

    user_input = st.text_input("Your message:", key="user_input")
    if st.button("Send"):
        if user_input:
            st.session_state.messages.append(
                {"role": "user", "content": user_input, "avatar": "🧑‍💻"}
            )
            st.session_state.current_message = user_input
            with st.spinner("Processing your message..."):
                st.experimental_rerun()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "💾 Save Conversation",
            key="save_button",
            help="Save the current conversation",
            use_container_width=True,
        ):
            log_content = create_conversation_log(
                conversation, st.session_state.messages
            )
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_log_{timestamp}.txt"

            with open(filename, "w") as f:
                f.write(log_content)

            st.success(f"Conversation saved as {filename}")
            st.balloons()  # Add a celebratory animation when saving
            st.experimental_rerun()  # Rerun the app to update the saved conversations list

    # Add collapsible section for saved conversations
    with st.sidebar.expander("📚 Saved Conversations"):
        saved_conversations = get_saved_conversations()
        if saved_conversations:
            for conv_file in saved_conversations:
                if st.button(f"📥 {conv_file}", key=f"download_{conv_file}"):
                    with open(conv_file, "r") as f:
                        content = f.read()
                    st.download_button(
                        label=f"📥 Download {conv_file}",
                        data=content,
                        file_name=conv_file,
                        mime="text/plain",
                        key=f"download_button_{conv_file}",
                    )
        else:
            st.info("No saved conversations found.")

    # Add a footer
    st.markdown(
        """
        <footer>
            <p>Made with ❤️ by <a href="https://github.com/tcsenpai">TCSenpai</a></p>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def create_conversation_log(conversation, messages):
    log = f"Conversation Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    log += f"Ollama Endpoint: {conversation.ollama_client.endpoint}\n"
    log += f"Model 1: {conversation.model_1}\n"
    log += f"Model 2: {conversation.model_2}\n"
    log += f"System Prompt 1:\n{conversation.system_prompt_1}\n\n"
    log += f"System Prompt 2:\n{conversation.system_prompt_2}\n\n"
    log += "Conversation:\n\n"

    for message in messages:
        log += f"{message['role'].capitalize()}: {message['content']}\n\n"

    return log


def get_saved_conversations():
    return [
        f
        for f in os.listdir()
        if f.startswith("conversation_log_") and f.endswith(".txt")
    ]
