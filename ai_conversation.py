import ollama
from termcolor import colored
import datetime
import tiktoken  # Used for token counting

class AIConversation:
    def __init__(
        self,
        model_1,
        model_2,
        system_prompt_1,
        system_prompt_2,
        ollama_endpoint,
        max_tokens=4000, 
    ):
        # Initialize conversation parameters and Ollama client
        self.model_1 = model_1
        self.model_2 = model_2
        self.system_prompt_1 = system_prompt_1
        self.system_prompt_2 = system_prompt_2
        self.current_model = self.model_1
        self.messages_1 = [{"role": "system", "content": system_prompt_1}]
        self.messages_2 = [{"role": "system", "content": system_prompt_2}]
        self.client = ollama.Client(ollama_endpoint)
        self.ollama_endpoint = ollama_endpoint
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.max_tokens = max_tokens

    def count_tokens(self, messages):
        # Count the total number of tokens in the messages
        return sum(len(self.tokenizer.encode(msg["content"])) for msg in messages)

    def trim_messages(self, messages):
        # Trim messages to stay within the token limit
        if self.count_tokens(messages) > self.max_tokens:
            print(colored(f"[SYSTEM] Max tokens reached. Sliding context window...", "magenta"))
            
            # Keep the system prompt (first message)
            system_prompt = messages[0]
            messages = messages[1:]
            
            # Remove messages from the beginning until we're under the token limit
            while self.count_tokens([system_prompt] + messages) > self.max_tokens:
                if messages:
                    messages.pop(0)  # Remove the oldest message
                else:
                    break  # Avoid removing all messages
            
            # Add the system prompt back at the beginning
            messages.insert(0, system_prompt)
        
        return messages

    def start_conversation(self, initial_message, num_exchanges=0, options=None):
        # Main conversation loop
        current_message = initial_message
        color_1, color_2 = "cyan", "yellow"
        conversation_log = []

        # Add initial message to system prompts
        self.messages_1[0]["content"] += f"\n\nInitial message: {current_message}"
        self.messages_2[0]["content"] += f"\n\nInitial message: {current_message}"

        print(colored(f"Starting conversation with: {current_message}", "green"))
        print(colored("Press CTRL+C to stop the conversation.", "red"))
        print()

        try:
            i = 0
            active_ai = 1  # Starting with AI 1
            while num_exchanges == 0 or i < num_exchanges:
                # Set up current AI's parameters
                name = "AI 1" if active_ai == 0 else "AI 2"
                messages = self.messages_1 if active_ai == 0 else self.messages_2
                other_messages = self.messages_2 if active_ai == 0 else self.messages_1
                color = color_1 if active_ai == 0 else color_2

                # Add user message to conversation history
                messages.append({"role": "user", "content": current_message})
                other_messages.append({"role": "assistant", "content": current_message})

                # Trim messages and get token count
                messages = self.trim_messages(messages)
                token_count = self.count_tokens(messages)
                print(colored(f"Context token count: {token_count}", "magenta"))

                # Generate AI response
                response = self.client.chat(
                    model=self.current_model,
                    messages=messages,
                    options=options,
                )
                response_content = response["message"]["content"]

                # Post-process to remove repetition
                response_content = self.remove_repetition(response_content)

                # Format and print the response with a bubble
                model_name = f"{self.current_model.upper()} ({name}):"
                formatted_response = model_name + "|:> " + response_content
                print(colored(formatted_response, color))
                conversation_log.append(
                    {"role": "assistant", "content": formatted_response}
                )

                # Update conversation history
                messages.append({"role": "assistant", "content": response_content})
                other_messages.append({"role": "user", "content": response_content})

                current_message = response_content

                # Switch to the other AI for the next turn
                self.current_model = self.model_2 if active_ai == 1 else self.model_1
                active_ai = 1 if active_ai == 0 else 0

                print(colored("---", "magenta"))
                print()

                # Check for conversation end condition
                if current_message.strip().endswith("{{end_conversation}}"):
                    print(colored("Conversation ended by the AI.", "green"))
                    break

                i += 1

        except KeyboardInterrupt:
            print(colored("\nConversation stopped by user.", "red"))

        print(colored("Conversation ended.", "green"))
        self.save_conversation_log(conversation_log)

    def save_conversation_log(self, messages, filename=None):
        # Save the conversation log to a file
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_log_{timestamp}.txt"

        log_content = f"Conversation Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        log_content += f"Ollama Endpoint: {self.ollama_endpoint}\n"
        log_content += f"Model 1: {self.model_1}\n"
        log_content += f"Model 2: {self.model_2}\n"
        log_content += f"System Prompt 1:\n{self.system_prompt_1}\n\n"
        log_content += f"System Prompt 2:\n{self.system_prompt_2}\n\n"
        log_content += "Conversation:\n\n"

        for message in messages:
            log_content += f"{message['role'].upper()}:\n{message['content']}\n\n"

        with open(filename, "w") as f:
            f.write(log_content)

        print(f"Conversation log saved to {filename}")

    def remove_repetition(self, text):
        # Remove repeated sentences while preserving order
        split_tokens = [".", "!", "?"]
        sentences = []
        current_sentence = ""
        for char in text:
            current_sentence += char
            if char in split_tokens:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        if current_sentence:  # Add any remaining text
            sentences.append(current_sentence.strip())

        # Remove duplicates while preserving order
        unique_sentences = []
        for sentence in sentences:
            if sentence not in unique_sentences:
                unique_sentences.append(sentence)

        # Join the sentences back together
        return " ".join(unique_sentences)
