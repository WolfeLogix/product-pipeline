from openai import OpenAI
from os import getenv

class ai_util:
    def __init__(
        self, 
        api_key=None,
        model="gpt-4o",
        temperature=0.7,
        max_response_len=None,
        frequency_penalty=0
    ):
        if not api_key:
            self.api_key = getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_response_len = max_response_len
        self.client = OpenAI()
        self.frequency_penalty = frequency_penalty

    def chat(self, messages: list):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_response_len,
            frequency_penalty=self.frequency_penalty
        )
        return completion.choices[0].message.content


# Example usage:
ai = ai_util()
response = ai.chat(
    [
        { "role": "system", "content": "You are a helpful assistant.", 
        "role": "user", "content": "Tell me about yourself" }
    ]
)
print(response)