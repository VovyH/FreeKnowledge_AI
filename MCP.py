import os
import sys
import argparse
import logging
from typing import Dict, List, Optional
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sues_center import SuesCenter

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("freeknowledge_mcp.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()
parser.add_argument("--type", type=str, default='stdio')
parser.add_argument("--port", type=int, default=8008)
args = parser.parse_args()

sues_center = SuesCenter()
mcp = FastMCP("FreeKnowledge_AI", port=args.port)

@mcp.tool()
async def baidu_search_with_summary(query: str, max_results: int = 5, flag: bool = True, save_format: str = None) -> str:
    """使用百度搜索获取外部知识并用大模型总结内容
    
    Args:
        query: 搜索查询或问题
        max_results: 返回的最大搜索结果数量 (默认: 5)
        flag: 是否使用大模型提取核心内容 (默认: True)
        save_format: 保存格式，如果为"json"则自动保存 (默认: None)
    """
    logger.info(f"执行百度搜索(带总结): {query}, 最大结果数: {max_results}, 总结: {flag}, 保存格式: {save_format}")
    
    results = sues_center.get_response(
        prompt=query,
        flag=flag,
        mode="BAIDU",
        max_web_results=max_results,
        save_format=save_format
    )
    
    if not results:
        return "未找到相关结果"
    
    if flag:
        formatted_results = "百度搜索结果(已总结):\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result.get('title', '无标题')}\n"
            formatted_results += f"   URL: {result.get('url', '')}\n"
            formatted_results += f"   内容总结:\n{result.get('content', '')}\n\n"
    else:
        formatted_results = "百度搜索结果(原始内容):\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result.get('title', '无标题')}\n"
            formatted_results += f"   URL: {result.get('url', '')}\n"
            formatted_results += f"   内容摘要: {result.get('core_content', '')[:500]}...\n\n"
    
    return formatted_results

@mcp.tool()
async def duckduckgo_search_with_summary(query: str, max_results: int = 5, flag: bool = True, save_format: str = None) -> str:
    """使用DuckDuckGo搜索获取外部知识并用大模型总结内容
    
    Args:
        query: 搜索查询或问题
        max_results: 返回的最大搜索结果数量 (默认: 5)
        flag: 是否使用大模型提取核心内容 (默认: True)
        save_format: 保存格式，如果为"json"则自动保存 (默认: None)
    """
    logger.info(f"执行DuckDuckGo搜索(带总结): {query}, 最大结果数: {max_results}, 总结: {flag}, 保存格式: {save_format}")
    
    results = sues_center.get_response(
        prompt=query,
        flag=flag,
        mode="DUCKDUCKGO",
        max_web_results=max_results,
        save_format=save_format
    )
    
    if not results:
        return "未找到相关结果"
    
    if flag:
        formatted_results = "DuckDuckGo搜索结果(已总结):\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result.get('title', '无标题')}\n"
            formatted_results += f"   URL: {result.get('url', '')}\n"
            formatted_results += f"   内容总结:\n{result.get('content', '')}\n\n"
    else:
        formatted_results = "DuckDuckGo搜索结果(原始内容):\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result.get('title', '无标题')}\n"
            formatted_results += f"   URL: {result.get('url', '')}\n"
            formatted_results += f"   内容摘要: {result.get('core_content', '')[:500]}...\n\n"
    
    return formatted_results

@mcp.tool()
async def url_specific_with_summary(url: str, flag: bool = True, save_format: str = None) -> str:
    """获取并处理特定URL的内容，使用大模型总结
    
    Args:
        url: 要获取内容的URL
        flag: 是否使用大模型提取核心内容 (默认: True)
        save_format: 保存格式，如果为"json"则自动保存 (默认: None)
    """
    logger.info(f"抓取URL内容(带总结): {url}, 总结: {flag}, 保存格式: {save_format}")
    
    results = sues_center.get_response(
        prompt="",
        flag=flag,
        mode="URL_SPECIFIC",
        specific_url=url,
        save_format=save_format
    )
    
    if not results:
        return f"无法抓取URL {url} 的内容"
    
    if flag:
        formatted_result = f"URL内容(已总结): {url}\n\n"
        formatted_result += f"标题: {results[0].get('title', '无标题')}\n\n"
        formatted_result += f"内容总结:\n{results[0].get('content', '')}\n"
    else:
        formatted_result = f"URL内容(原始): {url}\n\n"
        formatted_result += f"标题: {results[0].get('title', '无标题')}\n\n"
        formatted_result += f"内容摘要:\n{results[0].get('core_content', '')[:2000]}...\n"
    
    return formatted_result

if __name__ == "__main__":
    logger.info(f"FreeKnowledge_AI MCP 服务已启动，运行模式: {args.type}, 端口: {args.port}")
    mcp.run(transport=args.type) 