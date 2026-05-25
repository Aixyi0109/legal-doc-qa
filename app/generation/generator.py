from dotenv import load_dotenv

from openai import OpenAI
import os
load_dotenv()

class Generator:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1/"
        )
        self.model = model

    def generate(self, query: str, retrieved_chunks: list[dict]) -> str:
        build_message = self._build_message(query, retrieved_chunks)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=build_message
        )
        return response.choices[0].message.content.strip()
    
    def generate_stream(self, query: str, retrieved_chunks: list[dict]):
        build_message = self._build_message(query, retrieved_chunks)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=build_message,
            stream=True
        )
        for chunk in response:
            token = chunk.choices[0].delta.content
            if token:
                yield token

    def _build_message(self, query: str, retrieved_chunks: list[dict]):
        context = "\n\n".join(
            f"第{chunk['page']}页，来源文件{chunk['source_file']}\n{chunk['text']}"
            for chunk in retrieved_chunks
        )
        prompt = f"你是一个法律文档问答助手，基于以下提供的参考文档，回答用户的问题。参考文档\n\n{context}\n\n，请给出详细的答案，并且在答案中引用相关的参考文档，如果文档中没有相关信息，回答'根据提供的文档信息，无法回答该问题'，不要编造信息。"
        return [{"role": "system", "content": prompt},
                {"role": "user", "content": query}]