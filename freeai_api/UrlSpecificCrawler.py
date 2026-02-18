"""
URL专用爬虫模块 - 用于爬取特定网页的内容
"""

import requests
from bs4 import BeautifulSoup
import logging
import os
from typing import Dict, Optional
import time

# 配置日志
log_path = os.path.join(os.path.dirname(__file__), "url_crawler.log")
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path, encoding='utf-8', mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.propagate = False

def extract_chinese(text: str) -> Optional[str]:
    """
    从网页内容中提取有效文本（复用此函数以保持一致性）
    """
    try:
        from FreeKnowledge_AI.sues_search_duckduckgo import extract_chinese as duckgo_extract
        return duckgo_extract(text)
    except Exception as e:
        logger.error(f"提取文本过程中出错: {str(e)}")
        if not isinstance(text, str):
            return None
        return text

class UrlSpecificCrawler:
    """专门用于爬取特定URL的爬虫类"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        初始化URL爬虫
        
        Args:
            timeout: 请求超时时间(秒)
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.session = requests.Session()
        logger.info("URL爬虫初始化完成")
    
    def fetch_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        爬取特定URL的内容
        
        Args:
            url: 网页URL
            
        Returns:
            包含标题和内容的字典，或None（爬取失败）
        """
        try:
            logger.info(f"开始爬取URL: {url}")
            
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(
                        url,
                        headers=self.headers,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    response.encoding = 'utf-8'
                    
                    # 解析网页内容
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取标题
                    title = soup.title.string if soup.title else "无标题"
                    
                    # 提取正文内容
                    content = extract_chinese(response.text)
                    
                    logger.info(f"成功爬取URL: {url}")
                    return {
                        'title': title,
                        'url': url,
                        'core_content': content,
                        'relevance_score': 1.0  # 直接URL爬取默认相关性为1.0
                    }
                    
                except requests.RequestException as e:
                    logger.warning(f"爬取失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    if attempt == self.max_retries - 1:
                        logger.error(f"达到最大重试次数，爬取URL失败: {url}")
                        return None
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"爬取过程中发生错误: {str(e)}")
            return None
            
    def search(self, query: str, max_results: int = 1) -> list:
        """
        为了与其他搜索引擎接口保持一致，提供search方法
        当使用URL_SPECIFIC模式时，query参数被忽略，实际URL通过specific_url参数传递
        
        Args:
            query: 搜索关键词（在此类中被忽略）
            max_results: 最大结果数（在此类中被忽略）
            
        Returns:
            空列表，因为此方法不应直接被调用
        """
        logger.warning("URL爬虫的search方法被直接调用，这通常是不正确的。请使用fetch_content方法。")
        return [] 