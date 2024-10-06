import os
import json
from dotenv import load_dotenv, set_key
from ai_conversation import AIConversation

def load_system_prompt(filename):
    """Load the system prompt from a file."""
    with open(filename, "r") as file:
        return file.read().strip()

def load_options_from_json(filename):
    """Load options from a JSON file."""
    with open(filename, "r") as file:
        return json.load(file)

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

    # Load options from JSON file
    options = load_options_from_json("options.json")
    print(f"Options: {options}")

    # Initialize the AI conversation object
    conversation = AIConversation(
        model_1, model_2, system_prompt_1, system_prompt_2, ollama_endpoint, max_tokens
    )


    # Run the appropriate interface based on command-line arguments
    run_cli(conversation, initial_prompt, options)

def run_cli(conversation, initial_prompt, options):
    """Run the conversation in command-line interface mode."""
    load_dotenv()
    conversation.start_conversation(initial_prompt, num_exchanges=0, options=options)


if __name__ == "__main__":
    main()
