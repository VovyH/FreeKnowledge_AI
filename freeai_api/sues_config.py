"""
配置模块 - 管理FreeKnowledge AI的全局配置项
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    chat_model_retry: int = 3
    embed_model_retry: int = 3
    chat_model_type: str = "internlm/internlm2_5-7b-chat"
    model_key: str = "sk-zyaiumxqgzlocjyvfialewlvqxusjekwlfyexqthbqqhxsxz"
    model_base_url: str = "https://api.siliconflow.cn/v1/chat/completions"
    max_web_results: int = 10
    
config_args = Config()
