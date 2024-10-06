from ollama_client import OllamaClient
from termcolor import colored
import datetime


class AIConversation:
    def __init__(
        self, ollama_endpoint, model_1, model_2, system_prompt_1, system_prompt_2
    ):
        self.ollama_client = OllamaClient(ollama_endpoint)
        self.model_1 = model_1
        self.model_2 = model_2
        self.system_prompt_1 = system_prompt_1
        self.system_prompt_2 = system_prompt_2
        self.current_model = self.model_1
        self.current_system_prompt = self.system_prompt_1

    def start_conversation(self, initial_message, num_exchanges=0):
        current_message = initial_message
        current_model = self.model_1
        current_system_prompt = self.system_prompt_1
        color_1 = "cyan"
        color_2 = "yellow"
        messages = []

        print(colored(f"Starting conversation with: {current_message}", "green"))
        print(colored("Press CTRL+C to stop the conversation.", "red"))
        print()

        try:
            i = 0
            while num_exchanges == 0 or i < num_exchanges:
                response = self.ollama_client.generate(
                    current_model, current_message, current_system_prompt
                )

                model_name = f"{current_model.upper()}:"
                formatted_response = f"{model_name}\n{response}\n"

                if current_model == self.model_1:
                    print(colored(formatted_response, color_1))
                else:
                    print(colored(formatted_response, color_2))

                messages.append({"role": "assistant", "content": formatted_response})

                current_message = response
                if current_model == self.model_1:
                    current_model = self.model_2
                    current_system_prompt = self.system_prompt_2
                else:
                    current_model = self.model_1
                    current_system_prompt = self.system_prompt_1

                print(colored("---", "magenta"))
                print()

                i += 1

        except KeyboardInterrupt:
            print(colored("\nConversation stopped by user.", "red"))

        print(colored("Conversation ended.", "green"))
        self.save_conversation_log(messages)

    def stream_conversation(self, current_message):
        response = self.ollama_client.generate(
            self.current_model, current_message, self.current_system_prompt
        )

        model_name = f"{self.current_model.upper()}:"
        formatted_response = f"{model_name}\n{response}\n"

        yield formatted_response

        if self.current_model == self.model_1:
            self.current_model = self.model_2
            self.current_system_prompt = self.system_prompt_2
        else:
            self.current_model = self.model_1
            self.current_system_prompt = self.system_prompt_1

        yield "---\n"

    def get_conversation_response(self, current_message):
        response = self.ollama_client.generate(
            self.current_model, current_message, self.current_system_prompt
        )

        model_name = f"{self.current_model.upper()}:"
        formatted_response = f"{model_name}\n{response}\n"

        if self.current_model == self.model_1:
            self.current_model = self.model_2
            self.current_system_prompt = self.system_prompt_2
        else:
            self.current_model = self.model_1
            self.current_system_prompt = self.system_prompt_1

        return formatted_response

    def save_conversation_log(self, messages, filename=None):
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_log_{timestamp}.txt"

        log_content = f"Conversation Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        log_content += f"Ollama Endpoint: {self.ollama_client.endpoint}\n"
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