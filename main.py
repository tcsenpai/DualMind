import os
import argparse
from dotenv import load_dotenv, set_key
from ai_conversation import AIConversation

def load_system_prompt(filename):
    """Load the system prompt from a file."""
    with open(filename, "r") as file:
        return file.read().strip()

def main():
    # Load environment variables
    load_dotenv()

    # Retrieve configuration from environment variables
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
    model_1 = os.getenv("MODEL_1")
    model_2 = os.getenv("MODEL_2")
    system_prompt_1 = load_system_prompt("system_prompt_1.txt")
    system_prompt_2 = load_system_prompt("system_prompt_2.txt")
    initial_prompt = os.getenv(
        "INITIAL_PROMPT",
        "Let's discuss the future of AI. What are your thoughts on its potential impact on society?",
    )
    max_tokens = int(os.getenv("MAX_TOKENS", 4000))
    print(f"Max tokens: {max_tokens}")

    # Initialize the AI conversation object
    conversation = AIConversation(
        model_1, model_2, system_prompt_1, system_prompt_2, ollama_endpoint, max_tokens
    )

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="AI Conversation")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument(
        "--streamlit", action="store_true", help="Run in Streamlit mode"
    )
    args = parser.parse_args()

    # Run the appropriate interface based on command-line arguments
    if args.cli:
        run_cli(conversation, initial_prompt)
    elif args.streamlit:
        run_streamlit(conversation, initial_prompt)
    else:
        print("Please specify either --cli or --streamlit mode.")

def run_cli(conversation, initial_prompt):
    """Run the conversation in command-line interface mode."""
    load_dotenv()
    conversation.start_conversation(initial_prompt, num_exchanges=0)

def run_streamlit(conversation, initial_prompt):
    """Run the conversation in Streamlit interface mode."""
    import streamlit as st
    from streamlit_app import streamlit_interface

    streamlit_interface(conversation, initial_prompt)

if __name__ == "__main__":
    main()
