# utils/logger.py
import logging
import sys
from pathlib import Path

def setup_logger(level: str = "INFO", log_file: str = "logs/agent.log"):
    """配置统一日志：控制台 + 文件，支持彩色输出"""
    
    # 创建日志目录
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 清除旧 handler（避免重复）
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # 控制台 handler（彩色）
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%H:%M:%S"
    ))
    
    # 文件 handler（详细）
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s\n%(exc_info)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    root_logger.addHandler(console)
    root_logger.addHandler(file_handler)
    
    # 抑制第三方库冗余日志
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)