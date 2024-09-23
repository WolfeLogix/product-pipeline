from openai import OpenAI
from os import getenv

class ai_util:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if not self.api_key:
            self.api_key = getenv("OPENAI_API_KEY")
        self.client = OpenAI()

    def chat(self, messages: list):
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "write a haiku about ai"}
            ]
        )
        return completion.choices[0].message.content


# Example usage:
ai = ai_util()
response = ai.chat(["What is the meaning of life?"])
print(response)