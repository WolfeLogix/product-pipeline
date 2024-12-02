"""This is a utility class for interacting with the OpenAI API to generate chat completions."""
from os import getenv
from typing import Optional
from typing import Type
import httpx

from requests import get
from openai import OpenAI
from pydantic import BaseModel


class AiUtil:
    """
    AiUtil is a utility class for interacting with the OpenAI API to generate chat completions.
    Note: Only compatible with gpt-4o-mini-2024-07-18 and later, gpt-4o-2024-08-06 and later
    Attributes:
        api_key (str): The API key for authenticating with the OpenAI API.
        model (str): The model to use for generating completions. Default is "gpt-4o-2024-08-06".
        temperature (float): The sampling temperature to use. Default is 0.7.
        max_response_len (int): The maximum length of the response in tokens. Default is None.
        frequency_penalty (float): The penalty for repeated tokens. Default is 0.
    Methods:
        __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-2024-08-06", temperature: float = 0.7, max_response_len: Optional[int] = None, frequency_penalty: float = 0):
            Initializes the AiUtil instance with the provided parameters.
        chat(self, messages: list, output_model: Type[BaseModel]):
            Generates a chat completion based on the provided messages and returns the content of the first choice.
            Args:
                messages (list): A list of messages to send to the model.
                output_model (Type[BaseModel]): The model to use for formatting the response.
            Returns:
                str: The content of the first message choice from the completion.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: str = "gpt-4o-2024-08-06",
            temperature: float = 0.7,
            max_response_len: Optional[int] = None,
            frequency_penalty: float = 0
    ):
        if not api_key:
            self.api_key = getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_response_len = max_response_len
        self.client = OpenAI(http_client=httpx.Client(proxies={}))
        self.frequency_penalty = frequency_penalty

    def chat(self, messages: list, output_model: Type[BaseModel]):
        """
        Sends a list of messages to the chat model and returns the response.
        Args:
            messages (list): A list of messages to be sent to the chat model.
            output_model (Type[BaseModel]): The pydantic model type for the response format.
        Returns:
            str: The content of the response message.
        """

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_response_len,
            frequency_penalty=self.frequency_penalty,
            response_format=output_model
        )
        return completion.choices[0].message.content

    def status_check(self):
        """
        Checks the status of the OpenAI API.
        Returns:
            str: The status of the OpenAI API.
        """
        get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10
        ).raise_for_status()
        return "OK"


if __name__ == "__main__":
    # Example usage:
    ai = AiUtil()

    class Joke(BaseModel):
        """Pydantic model for a joke."""
        setup: str
        punchline: str

    class JokeList(BaseModel):
        """Pydantic model for a list of jokes."""
        jokes: list[Joke]

    response = ai.chat(
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": "Give me 10 funny jokes"}
        ],
        output_model=JokeList
    )
    print(response)
