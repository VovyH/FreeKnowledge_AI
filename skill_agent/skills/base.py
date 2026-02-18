# skills/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class SkillSchema(BaseModel):
    """技能 JSON Schema 定义（Pydantic 校验）"""
    name: str = Field(..., description="函数名，必须与 register 时一致")
    description: str = Field(..., description="给模型看的技能描述")
    parameters: Dict[str, Any] = Field(..., description="JSON Schema 格式的参数字典")

class BaseSkill(ABC):
    """所有 Skill 的基类，统一接口规范"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """技能唯一标识（必须与 tools_schema 中的 function.name 一致）"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """给 LLM 阅读的技能描述（影响调用准确率）"""
        pass
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema 格式的参数定义"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """执行技能逻辑，返回 string（LLM 可理解）"""
        pass
    
    def to_tool_schema(self) -> Dict[str, Any]:
        """转换为 OpenAI Function Calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters_schema["properties"],
                    "required": self.parameters_schema.get("required", []),
                    "additionalProperties": False
                }
            }
        }