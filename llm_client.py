import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
llm_model_name = os.getenv("LLM_MODEL_NAME")

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def ado_requests(self, prompt):
        print("prompt:", prompt)
        response = self.client.chat.completions.create(
            model=llm_model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
