# core/message_handler.py
import logging
from typing import List, Optional

from config.settings import settings
from core.client import LLMClient
from core.skill_manager import SkillManager

logger = logging.getLogger(__name__)

class MessageHandler:
    """处理用户消息 → LLM → Skill → 最终回复 的完整流程"""
    
    def __init__(self):
        self.client = LLMClient.get_instance()
        self.skill_mgr = SkillManager.get_instance()
    
    def handle(self, user_message: str, history: Optional[List[dict]] = None) -> str:
        """
        处理单轮用户消息，支持多轮 tool_calls
        :param user_message: 用户输入
        :param history: 可选的历史消息列表（用于多轮对话）
        :return: 最终回复字符串
        """
        # 初始化消息历史
        messages = history.copy() if history else []
        messages.append({"role": "user", "content": user_message})
        
        tools_schema = self.skill_mgr.get_tools_schema()
        
        # 🔄 多轮工具调用循环
        for turn in range(settings.max_tool_calls_per_turn):
            logger.info(f"🔄 第 {turn+1} 轮 LLM 请求")
            
            response = self.client.chat(
                messages=messages,
                tools=tools_schema if tools_schema else None,
                tool_choice="auto"
            )
            
            assistant_msg = response.choices[0].message
            messages.append(assistant_msg)
            
            # ✅ 无工具调用：直接返回
            if not assistant_msg.tool_calls:
                logger.info("✅ 无工具调用，返回最终回复")
                return assistant_msg.content or ""
            
            # 🛠️ 执行所有 tool_calls
            for tool_call in assistant_msg.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = tool_call.function.arguments or "{}"
                    arguments = json.loads(func_args)  # 注意：需 import json
                except json.JSONDecodeError as e:
                    tool_response = f"❌ 参数解析失败: {e}"
                else:
                    tool_response = self.skill_mgr.execute(func_name, arguments)
                
                # 📥 返回 tool 结果给模型
                messages.append({
                    "role": "tool",
                    "content": tool_response,
                    "tool_call_id": tool_call.id
                })
                logger.debug(f"📥 tool 响应: {tool_response[:100]}...")
        
        # ⚠️ 达到最大轮次，强制生成最终回复
        logger.warning(f"⚠️ 达到最大工具调用轮次 ({settings.max_tool_calls_per_turn})，生成最终回复")
        final_response = self.client.chat(messages=messages, tools=None)
        return final_response.choices[0].message.content or "抱歉，处理超时，请重试。"