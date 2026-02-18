# core/client.py
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """SiliconFlow 客户端（单例 + 自动重试）"""
    
    _instance: Optional["LLMClient"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.client = OpenAI(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url.rstrip("/"),  # ✅ 去除末尾空格
            timeout=30.0
        )
        self.model = settings.siliconflow_model
        self._initialized = True
        logger.info(f"✅ LLMClient 初始化: model={self.model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def chat(
        self,
        messages: list,
        tools: list = None,
        tool_choice: str = "auto",
        stream: bool = False,
        **kwargs
    ):
        """封装 chat.completions.create，添加默认参数"""
        default_params = {
            "model": self.model,
            "temperature": settings.temperature,
            "stream": stream,
        }
        if tools:
            default_params["tools"] = tools
            default_params["tool_choice"] = tool_choice
        
        # 合并用户参数（用户参数优先）
        final_params = {**default_params, **kwargs}
        
        logger.debug(f"📤 请求 LLM: messages={len(messages)}, tools={len(tools) if tools else 0}")
        response = self.client.chat.completions.create(
            messages=messages,
            **final_params
        )
        logger.debug(f"📥 响应 LLM: choices={len(response.choices)}")
        return response
    
    @classmethod
    def get_instance(cls) -> "LLMClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance