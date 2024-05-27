from typing import Optional
from ollama import Client

from modules.tokenisers import get_tokeniser_and_context_window


class OllamaChat:
    def __init__(self, client: Client, model_name: str, system_prompt: Optional[str]):
        self.client = client
        self.model_name = model_name
        self.message_history = []

        self.tokeniser, self.ctx_window, _, self.num_token_func = (
            get_tokeniser_and_context_window(model_name)
        )

        if not model_name:
            raise ValueError("Model name required")
        if not client:
            raise ValueError("Client required")
        if system_prompt:
            self.append_message("system", system_prompt)

    @property
    def conv_no_tokens(self):
        return self.num_token_func(self.message_history)

    @staticmethod
    def wrap_message(role, content):
        return {"role": role, "content": content}

    def append_message(self, role, content):
        self.message_history.append(OllamaChat.wrap_message(role, content))

    def pop_last_message(self):
        self.message_history.pop()

    def invoke(self, stream=False):
        """
        Invokes the chatbot with the given model and message history, and returns the chatbot's response.

        Args:
            stream (bool, optional): Whether to stream the chatbot's response. Defaults to False.

        Returns:
            dict or Iterator[dict]: The chatbot's response. If `stream` is True, returns an iterator of dictionaries containing the chatbot's response in chunks. Otherwise, returns a dictionary containing the entire chatbot's response.

        Raises:
            ValueError: If the message history does not end with a user message.
        """

        if not self.message_history or self.message_history[-1]["role"] != "user":
            raise ValueError("Message history must end with a user message")

        return self.client.chat(
            model=self.model_name,
            messages=self.message_history,
            stream=stream,
            options={"num_ctx": self.ctx_window},
        )

    def invoke_and_append_generated_message(self, stream=False):
        """
        Invokes the chatbot with the given model and message history, and appends the generated message to the message history.

        Args:
            stream (bool, optional): Whether to stream the chatbot's response. Defaults to False.

        Yields:
            str: A string representing the generated message.

        Raises:
            ValueError: If the message history does not end with a user message.

        Returns:
            None
        """
        res = self.invoke(stream)
        res_stream = ""

        if stream:
            for chunk in res:
                res_stream += chunk["message"]["content"]
                yield res_stream
        else:
            res_stream = res["message"]["content"]

        self.append_message("assistant", res_stream)
        yield res_stream
