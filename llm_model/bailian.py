from openai import OpenAI
from .base_llm import base_llm

class BAILIAN (base_llm):
    def __init__(self, api_key, system_role, system_role_english, base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.system_role = system_role
        self.system_role_english = system_role_english

    def detect_classification(self, text, sub_domain) -> bool:
        client = OpenAI(
            api_key = self.api_key,
            base_url = self.base_url,
        )

        completion = client.chat.completions.create(
            model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {'role': 'system', 'content': f'You are a helpful {self.system_role_english},you can just answer yes or no.'},
                {'role': 'user', 'content': f"Is the following content in the field of {sub_domain}?{text}"}],
        )
        if 'yes' in completion.choices[0].message.content.lower():
            return True
        else:
            return False

    def AI_chat(self, text, answer_length=50, is_conclusion=False) -> str:
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            # api_key=os.getenv("DASHSCOPE_API_KEY"),
            api_key=self.api_key,
            base_url=self.base_url,
        )
        if is_conclusion:
            completion = client.chat.completions.create(
                model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=[
                    {'role': 'system', 'content': f'你是一名{self.system_role}，并且你拥有ChatGPT4的能力'},
                    {'role': 'user', 'content': f"将如下内容通俗易懂地总结，不超过{answer_length}字\n{text}"}],
            )
        else:
            completion = client.chat.completions.create(
                model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=[
                    {'role': 'system', 'content': f'你是一名{self.system_role}，并且你拥有ChatGPT4的能力'},
                    {'role': 'user', 'content':f"详细理解每个研究方法，并分别通俗易懂地总结他们，每点严格不超过{answer_length}字，中文回答\n{text}"}],
            )
        return completion.choices[0].message.content