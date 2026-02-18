# skills/knowledge.py
import logging
from typing import Literal, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from skills.base import BaseSkill
from config.settings import settings
from utils.token_utils import estimate_tokens, safe_truncate

# 延迟导入，避免循环依赖
_knowledge_center = None

def _get_center():
    global _knowledge_center
    if _knowledge_center is None:
        from FreeKnowledge_AI import knowledge_center
        _knowledge_center = knowledge_center.Center()
    return _knowledge_center

logger = logging.getLogger(__name__)

class KnowledgeRetrievalSkill(BaseSkill):
    """FreeKnowledge_AI 封装：外部知识检索技能"""
    
    @property
    def name(self) -> str:
        return "search_external_knowledge"
    
    @property
    def description(self) -> str:
        return "检索实时外部知识（百度/DuckDuckGo/指定URL），适用于查询政策、分数线、会议信息等动态内容。优先使用 BAIDU 模式获取中文高校信息。"
    
    @property
    def parameters_schema(self) -> dict:
        return {
            "properties": {
                "question": {
                    "type": "string",
                    "description": "用户要查询的具体问题，如'2024年上海工程技术大学研究生复试分数线'"
                },
                "mode": {
                    "type": "string",
                    "enum": ["BAIDU", "DUCKDUCKGO", "URL_SPECIFIC"],
                    "description": "搜索源：BAIDU(中文快/无需VPN), DUCKDUCKGO(英文准/需VPN), URL_SPECIFIC(爬取指定网页)",
                    "default": settings.fkai_default_mode
                },
                "use_llm_refine": {
                    "type": "boolean",
                    "description": "是否用大模型清洗结果（True=输出规范但稍慢）",
                    "default": settings.fkai_use_llm_refine
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "最大返回结果数，建议3-5",
                    "default": settings.fkai_max_results
                },
                "specific_url": {
                    "type": "string",
                    "description": "当mode='URL_SPECIFIC'时，填写要爬取的具体URL"
                }
            },
            "required": ["question"]
        }
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    def execute(self, **kwargs) -> str:
        """执行知识检索，返回格式化字符串"""
        question = kwargs.get("question", "")
        mode = kwargs.get("mode", settings.fkai_default_mode)
        use_llm_refine = kwargs.get("use_llm_refine", settings.fkai_use_llm_refine)
        max_results = kwargs.get("max_results", settings.fkai_max_results)
        specific_url = kwargs.get("specific_url")
        
        # 🎯 领域优化：高校查询自动增强
        if self._is_university_query(question):
            mode = "BAIDU"
            if mode == "URL_SPECIFIC" and not specific_url:
                specific_url = "https://gs.sues.edu.cn"  # 上海工程技术大学研究生院
        
        logger.info(f"🔍 知识检索: question='{question}', mode={mode}")
        
        try:
            center = _get_center()
            results = center.get_response(
                question=question,
                flag=use_llm_refine,
                mode=mode,
                specific_url=specific_url if mode == "URL_SPECIFIC" else None,
                max_web_results=max_results
            )
            
            # 📦 格式化输出
            formatted = self._format_results(results, max_results)
            
            # 🔒 Token 安全截断
            if estimate_tokens(formatted) > 500:
                formatted = safe_truncate(formatted, max_tokens=500)
            
            logger.info(f"✅ 检索成功，返回 {len(formatted)} 字符")
            return formatted
            
        except Exception as e:
            logger.error(f"❌ 知识检索失败: {e}", exc_info=True)
            return f"⚠️ 知识检索暂时不可用: {str(e)[:100]}"
    
    def _is_university_query(self, question: str) -> bool:
        """智能识别高校相关查询"""
        keywords = [
            "上海工程技术大学", "sues", "研究生复试", "分数线", 
            "录取名单", "调剂", "导师", "招生简章"
        ]
        return any(kw.lower() in question.lower() for kw in keywords)
    
    def _format_results(self, results, max_results: int) -> str:
        """统一结果格式"""
        if isinstance(results, list):
            items = []
            for i, r in enumerate(results[:max_results]):
                # 清理 HTML/多余空白
                clean_r = str(r).strip().replace("\n\n", "\n")
                items.append(f"【来源{i+1}】{clean_r}")
            return "\n\n".join(items)
        return str(results).strip()

# ✅ 单例实例（便于注册）
knowledge_skill = KnowledgeRetrievalSkill()