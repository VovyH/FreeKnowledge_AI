import requests
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional
import json
from difflib import SequenceMatcher
import jieba
import os
from html import unescape

# 配置日志
log_path = os.path.join(os.path.dirname(__file__), "duckduckgo_search.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def remove_html_tags(text: str) -> str:
    """
    去除HTML标签并解码HTML实体。
    
    Args:
        text: 输入字符串，可能包含HTML标签和HTML实体
        
    Returns:
        去除HTML标签后的纯文本
    """
    # 去除HTML标签
    clean_text = re.sub(r'<[^>]+>', '', text)
    # 解码HTML实体
    clean_text = unescape(clean_text)
    return clean_text

def extract_chinese(text: str) -> Optional[str]:
    """
    提取字符串中的中文字符、中文标点符号、中文之间的汉字和英文，保留换行符。
    
    Args:
        text: 输入字符串，可能包含中文、英文、数字、符号等，包含换行符
        
    Returns:
        提取的字符串（保留中文、中文标点、中文之间的汉字和英文，以及换行符），如果无中文则返回空字符串，如果输入无效则返回 None
    """
    try:
        if not isinstance(text, str):
            raise ValueError("输入必须是字符串")
        
        # 去除HTML标签
        text = remove_html_tags(text)
        
        # 使用正则表达式匹配中文字符、中文标点符号、中文之间的汉字和英文，以及换行符
        pattern = r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffefa-zA-Z0-9\n]'
        matches = re.findall(pattern, text)
        
        # 将匹配结果拼接为字符串
        result = ''.join(matches)
        
        # 如果结果为空，返回空字符串
        return result if result else ""
    except Exception as e:
        logger.error(f"提取过程中出错: {str(e)}")
        return None


class BaiduSearchOptimized:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        初始化优化的百度搜索类
        
        Args:
            timeout: 网络请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = "https://www.baidu.com/s"
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.session = requests.Session()
        self.authoritative_domains = {
            '.edu.cn': 1.5,  # 教育机构
            '.gov.cn': 1.5,  # 政府网站
            '.org': 1.2,     # 非营利组织
            '.cn': 1.1,      # 国内网站
            '.com': 1.0      # 商业网站
        }

    def _get_nouns(self, query: str) -> List[str]:
        """使用jieba分词提取名词和其他重要词语"""
        words = jieba.lcut(query)
        # 过滤停用词和单字符，优先保留名词
        stop_words = {'的', '是', '在', '和', '等', '年'}  # 自定义停用词
        nouns = [word for word in words if len(word) > 1 and word not in stop_words and not word.isdigit()]
        return nouns

    def _calculate_relevance_score(self, query: str, title: str, snippet: str, url: str) -> float:
        """
        计算搜索结果的相关性得分，基于名词匹配优先
        
        Args:
            query: 搜索关键词
            title: 结果标题
            snippet: 结果摘要
            url: 结果链接
            
        Returns:
            相关性得分
        """
        try:
            # 获取查询中的名词
            query_nouns = self._get_nouns(query)
            if not query_nouns:
                return 0.0

            # 转换为小写进行匹配
            content = (title.lower() + " " + snippet.lower())
            matched_nouns = [noun for noun in query_nouns if noun in content]

            # 计算名词匹配比例
            noun_match_ratio = len(matched_nouns) / len(query_nouns) if query_nouns else 0.0
            if noun_match_ratio == 0:
                return 0.0

            # 域名权威性
            domain = urlparse(url).netloc.lower()
            domain_score = 1.0
            for auth_domain, weight in self.authoritative_domains.items():
                if domain.endswith(auth_domain):
                    domain_score = weight
                    break

            # 获取网页内容并检查子词匹配
            page_content = self._fetch_page_content(url)
            if page_content:
                page_text = extract_chinese(page_content)
                if page_text is None:  # 添加保护
                    page_text = ""
                page_text = page_text.lower()
                query_words = set(query.lower().split())
                total_frequency = 0
                content_length = len(page_text.split())
                for word in query_words:
                    total_frequency += page_text.count(word)
                word_frequency_score = min(total_frequency / len(query_words), 5)
                content_match_ratio = (total_frequency / content_length)
            else:
                content_match_ratio = 0.0
                word_frequency_score = 0.0

            # 综合得分：
            # 名词匹配占30%，内容匹配占50%，词汇频率占10%，其余各占10%
            query_words = set(query.lower().split())
            title_words = set(title.lower().split())
            snippet_words = set(snippet.lower().split())
            
            title_match = len(query_words.intersection(title_words)) / len(query_words)
            snippet_match = len(query_words.intersection(snippet_words)) / len(query_words)
            title_similarity = SequenceMatcher(None, query.lower(), title.lower()).ratio()
            snippet_similarity = SequenceMatcher(None, query.lower(), snippet.lower()).ratio()

            score = (0.3 * noun_match_ratio + 
                     0.5 * content_match_ratio +
                     0.1 * (word_frequency_score / 5) +  # 归一化到0-0.1范围
                     0.05 * title_match + 
                     0.05 * snippet_match) * domain_score
            return min(score, 1.0)  # 确保得分不超过1.0
        except Exception as e:
            logger.warning(f"计算相关性得分时出错: {str(e)}")
            return 0.0

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Optional[str]]]:
        """
        执行优化的百度搜索，仅返回 top-5 最相关结果
        
        Args:
            query: 搜索关键词
            max_results: 返回的最大结果数（默认5）
        
        Returns:
            List of dictionaries containing title, url, and content
        """
        results = []
        try:
            # 构造搜索 URL
            params = {'wd': query}
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(
                        self.base_url,
                        headers=self.headers,
                        params=params,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    response.encoding = 'utf-8'
                    break
                except requests.RequestException as e:
                    logger.warning(f"搜索请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    if attempt == self.max_retries - 1:
                        logger.error("达到最大重试次数，搜索失败")
                        return results
                    time.sleep(1)

            # 解析搜索结果页面
            soup = BeautifulSoup(response.text, 'html.parser')

            # 初步收集候选结果（最多 30 个，避免遍历过多）
            candidates = []
            for item in soup.select('div.result.c-container')[:30]:
                try:
                    title_tag = item.select_one('h3.t a')
                    title = title_tag.get_text().strip() if title_tag else "无标题"
                    url = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
                    snippet_tag = item.select_one('.c-abstract')
                    snippet = snippet_tag.get_text().strip() if snippet_tag else ""

                    if url:
                        url = self._resolve_redirect_url(url)
                        if url:
                            score = self._calculate_relevance_score(query, title, snippet, url)
                            # 仅保留得分大于0的结果
                            if score > 0:
                                candidates.append({
                                    'title': title,
                                    'url': url,
                                    'snippet': snippet,
                                    'score': score
                                })
                except Exception as e:
                    logger.warning(f"处理搜索结果时出错: {str(e)}")
                    continue

            # 根据相关性得分排序并选择 top-5
            candidates.sort(key=lambda x: x['score'], reverse=True)
            top_candidates = candidates[:max_results]

            # 仅对 top-5 结果进行内容抓取
            for candidate in top_candidates:
                try:
                    content = self._fetch_page_content(candidate['url']) if candidate['url'] else "无法获取内容"
                    core_content = extract_chinese(content)
                    results.append({
                        'title': candidate['title'],
                        'url': candidate['url'],
                        'core_content': core_content,
                        'relevance_score': candidate['score']
                    })
                    logger.info(f"成功处理结果: {candidate['title']} ({candidate['url']})")
                except Exception as e:
                    logger.error(f"处理候选结果时出错: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"搜索过程中发生错误: {str(e)}")
        
        return results

    def _resolve_redirect_url(self, url: str) -> Optional[str]:
        """
        解析百度跳转链接，获取真实 URL
        
        Args:
            url: 原始链接
            
        Returns:
            真实 URL 或 None
        """
        try:
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(
                        url,
                        headers=self.headers,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    return response.url
                except requests.RequestException as e:
                    logger.warning(f"解析跳转链接失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    if attempt == self.max_retries - 1:
                        return None
                    time.sleep(1)
        except Exception as e:
            logger.error(f"解析跳转链接时出错: {str(e)}")
        return None

    def _fetch_page_content(self, url: str) -> Optional[str]:
        """
        获取网页的完整 HTML 内容
        
        Args:
            url: 网页 URL
            
        Returns:
            网页的完整 HTML 内容或 None
        """
        try:
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(
                        url,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    response.encoding = 'utf-8'

                    # 直接返回完整 HTML 内容
                    html_content = response.text
                    return html_content if html_content else "无有效内容"
                except requests.RequestException as e:
                    logger.warning(f"获取网页内容失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    if attempt == self.max_retries - 1:
                        return None
                    time.sleep(1)
        except Exception as e:
            logger.error(f"获取网页内容时出错: {str(e)}")
        return None

    def save_results(self, results: List[Dict[str, Optional[str]]], filename: str = r'E:\我的论文和代码\Chemotherapy\ReNeLLM-main\sues_rag\search_results.json'):
        """
        将搜索结果保存为 JSON 文件
        
        Args:
            results: 搜索结果列表
            filename: 保存文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"搜索结果已保存至 {filename}")
        except Exception as e:
            logger.error(f"保存搜索结果时出错: {str(e)}")

def main():
    # 示例使用
    search_engine = BaiduSearchOptimized()
    query = input("请输入搜索关键词: ")
    start_time = time.time()
    results = search_engine.search(query, max_results=10)
    
    # 打印结果
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"标题: {result['title']}")
        print(f"链接: {result['url']}")
        print(f"内容预览: {result['core_content'][:200] + '...' if result['core_content'] and len(result['core_content']) > 200 else result['core_content']}")
        print(f"相关性得分: {result['relevance_score']:.2f}")
        print("-" * 80)
    
    # 保存结果
    search_engine.save_results(results)
    print(f"\n搜索用时: {time.time() - start_time:.2f} 秒")

if __name__ == "__main__":
    main()