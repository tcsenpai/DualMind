import os
import argparse
from dotenv import load_dotenv, set_key
from ai_conversation import AIConversation

def load_system_prompt(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

def main():
    parser = argparse.ArgumentParser(description="AI Conversation")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--streamlit", action="store_true", help="Run in Streamlit mode")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    elif args.streamlit:
        run_streamlit()
    else:
        print("Please specify either --cli or --streamlit mode.")

def run_cli():
    load_dotenv()
    
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
    model_1 = os.getenv("MODEL_1")
    model_2 = os.getenv("MODEL_2")

    system_prompt_1_file = os.getenv("CUSTOM_SYSTEM_PROMPT_1", "system_prompt_1.txt")
    system_prompt_2_file = os.getenv("CUSTOM_SYSTEM_PROMPT_2", "system_prompt_2.txt")
        
    system_prompt_1 = load_system_prompt(system_prompt_1_file)
    system_prompt_2 = load_system_prompt(system_prompt_2_file)
    
    initial_prompt = os.getenv("INITIAL_PROMPT", "Let's discuss the future of AI. What are your thoughts on its potential impact on society?")
    
    conversation = AIConversation(ollama_endpoint, model_1, model_2, system_prompt_1, system_prompt_2)
    conversation.start_conversation(initial_prompt, num_exchanges=0)

def run_streamlit():
    import streamlit as st
    from streamlit_app import streamlit_interface

    load_dotenv()
    
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
    model_1 = os.getenv("MODEL_1")
    model_2 = os.getenv("MODEL_2")
    
    system_prompt_1 = load_system_prompt("system_prompt_1.txt")
    system_prompt_2 = load_system_prompt("system_prompt_2.txt")
    
    initial_prompt = os.getenv("INITIAL_PROMPT", "Let's discuss the future of AI. What are your thoughts on its potential impact on society?")
    
    conversation = AIConversation(ollama_endpoint, model_1, model_2, system_prompt_1, system_prompt_2)
    streamlit_interface(conversation, initial_prompt)

if __name__ == "__main__":
    main()