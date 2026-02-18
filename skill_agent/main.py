# main.py
#!/usr/bin/env python3
import sys
import logging
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from utils.logger import setup_logger
from core.message_handler import MessageHandler

# 初始化日志
setup_logger(
    level=settings.log_level,
    log_file=settings.log_file
)
logger = logging.getLogger(__name__)

def run_cli():
    """命令行交互模式"""
    print(f"🤖 SkillAgent 启动 | 模型: {settings.siliconflow_model}")
    print("💡 输入 'exit' 或 'quit' 退出\n")
    
    handler = MessageHandler()
    history = []  # 简单记忆最近 10 轮
    
    while True:
        try:
            user_input = input("👤 您: ").strip()
            if user_input.lower() in ["exit", "quit", "退出"]:
                print("👋 再见！")
                break
            if not user_input:
                continue
            
            response = handler.handle(user_input, history[-10:])
            print(f"🤖 助手: {response}\n")
            
            # 更新历史（简化版）
            history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ])
            
        except KeyboardInterrupt:
            print("\n⚠️ 中断退出")
            break
        except Exception as e:
            logger.error(f"❌ 运行时错误: {e}", exc_info=True)
            print(f"❌ 错误: {e}")

def run_server():
    """[可选] FastAPI 服务入口"""
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn
        
        app = FastAPI(title="SkillAgent API")
        handler = MessageHandler()
        
        class ChatRequest(BaseModel):
            message: str
            history: list = []
        
        @app.post("/chat")
        async def chat(req: ChatRequest):
            try:
                response = handler.handle(req.message, req.history)
                return {"response": response}
            except Exception as e:
                logger.error(f"API 错误: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
        
        logger.info(f"🚀 启动 HTTP 服务: http://{settings.host}:{settings.port}")
        uvicorn.run(app, host=settings.host, port=settings.port)
        
    except ImportError:
        logger.warning("⚠️ 未安装 fastapi/uvicorn，跳过 HTTP 服务启动")
        run_cli()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SkillAgent - Function Calling 智能助手")
    parser.add_argument("--mode", choices=["cli", "server"], default="cli", help="运行模式")
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server()
    else:
        run_cli()