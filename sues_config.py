from dataclasses import dataclass
import os

@dataclass
class Config:
    chat_model_retry: int = 3
    embed_model_retry: int = 3
    chat_model_type: str = "internlm/internlm2_5-7b-chat"
    model_key: str = "sk-ybtkfjuxnmxuznblvyzfpfgjevqdlgslwvwjfndmeuimfhku"
    model_base_url: str = "https://api.siliconflow.cn/v1/chat/completions"
    max_web_results: int = 10
    
config_args = Config()