import ollama
from termcolor import colored
import datetime

class AIConversation:
    def __init__(self, model_1, model_2, system_prompt_1, system_prompt_2, ollama_endpoint):
        self.model_1 = model_1
        self.model_2 = model_2
        self.system_prompt_1 = system_prompt_1
        self.system_prompt_2 = system_prompt_2
        self.current_model = self.model_1
        self.messages_1 = [{"role": "system", "content": system_prompt_1}]
        self.messages_2 = [{"role": "system", "content": system_prompt_2}]
        self.client = ollama.Client(ollama_endpoint)
        self.ollama_endpoint = ollama_endpoint

    def start_conversation(self, initial_message, num_exchanges=0):
        current_message = initial_message
        color_1 = "cyan"
        color_2 = "yellow"
        conversation_log = []

        # Appending the initial message to the conversation log in the system prompt
        self.messages_1[0]["content"] += f"\n\nInitial message: {current_message}"
        self.messages_2[0]["content"] += f"\n\nInitial message: {current_message}"

        print(colored(f"Starting conversation with: {current_message}", "green"))
        print(colored("Press CTRL+C to stop the conversation.", "red"))
        print()

        try:
            i = 0
            active_ai = 1 # Starting with AI 1
            while num_exchanges == 0 or i < num_exchanges:
                

                if active_ai == 0:
                    name = "AI 1"
                    messages = self.messages_1
                    other_messages = self.messages_2
                    color = color_1
                else:
                    name = "AI 2"
                    messages = self.messages_2
                    other_messages = self.messages_1
                    color = color_2

                messages.append({"role": "user", "content": current_message})
                other_messages.append({"role": "assistant", "content": current_message})

                #print(colored(f"Conversation with {name} ({self.current_model})", "blue"))
                response = self.client.chat(model=self.current_model, messages=messages)
                response_content = response['message']['content']

                model_name = f"{self.current_model.upper()} ({name}):"
                formatted_response = f"{model_name}\n{response_content}\n"

                print(colored(formatted_response, color))
                conversation_log.append({"role": "assistant", "content": formatted_response})

                messages.append({"role": "assistant", "content": response_content})
                other_messages.append({"role": "user", "content": response_content})

                current_message = response_content
                self.current_model = self.model_2 if active_ai == 1 else self.model_1
                active_ai = 1 if active_ai == 0 else 0

                print(colored("---", "magenta"))
                print()

                if current_message.strip().endswith("{{end_conversation}}"):
                    print(colored("Conversation ended by the AI.", "green"))
                    break

                i += 1

        except KeyboardInterrupt:
            print(colored("\nConversation stopped by user.", "red"))

        print(colored("Conversation ended.", "green"))
        self.save_conversation_log(conversation_log)


    def save_conversation_log(self, messages, filename=None):
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
