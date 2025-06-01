import openai
from openai import AzureOpenAI
import os
import time

OPENAI_AZURE_ENDPOINT = "https://azure-openai-miblab-japan.openai.azure.com/"
OPENAI_API_KEY = "c090e69fdae34b63a77ecbe436b1e356"
OPENAI_API_VERSION = "2024-02-15-preview"

class ChatCompletionSampler:
    """
    Sample from OpenAI's chat completion API
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        system_message: str = None,
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ):
        self.azure_endpoint = OPENAI_AZURE_ENDPOINT
        self.api_key = OPENAI_API_KEY
        self.api_version = OPENAI_API_VERSION
        self.engine = model

        self.client = AzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "url"

    def _handle_image(
        self, image: str, encoding: str = "base64", format: str = "png", fovea: int = 768
    ):
        new_image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{format};{encoding},{image}",
            },
        }
        return new_image

    def _handle_text(self, text: str):
        return {"type": "text", "text": text}

    def _pack_message(self, role: str, content):
        return {"role": str(role), "content": content}

    def __call__(self, message_list) -> str:
        if self.system_message:
            message_list = [self._pack_message("system", self.system_message)] + message_list
        num_trials = 0
        max_trials = 3
        while num_trials < max_trials:
            try:
                # breakpoint()
                response = self.client.chat.completions.create(
                    model=self.engine,
                    messages=message_list,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                # breakpoint()
                return response.choices[0].message.content
            # NOTE: BadRequestError is triggered once for MMMU, please uncomment if you are reruning MMMU
            except openai.BadRequestError as e:
                print("Bad Request Error", e)
                return ""
            except Exception as e:
                exception_backoff = 2**num_trials  # expontial back off
                print(
                    f"Rate limit exception so wait and retry {num_trials} after {exception_backoff} sec",
                    e,
                )
                time.sleep(exception_backoff)
                num_trials += 1
            # unknown error shall throw exception

if __name__ == '__main__':
    sampler = ChatCompletionSampler()
    print(sampler([{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of France?"}]))