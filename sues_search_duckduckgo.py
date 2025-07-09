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
import re
import os
from html import unescape
from typing import Optional

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
    提取网页内容中的有效文本，保留中文字符、中文标点符号、英文字母、数字和换行符
    过滤掉HTML标签和其他不相关字符
    
    Args:
        text: 输入字符串，可能包含中文、英文、数字、符号等，包含换行符
        
    Returns:
        提取的字符串（保留中文、中文标点、中文之间的汉字和英文，以及换行符），如果无中文则返回空字符串，如果输入无效则返回 None
    """
    try:
        if not isinstance(text, str):
            logger.warning("extract_chinese函数收到非字符串输入")
            raise ValueError("输入必须是字符串")
        
        # 首先去除HTML标签
        text = remove_html_tags(text)
        
        # 使用正则表达式匹配中文字符、中文标点符号、英文字母、数字和换行符
        # \u4e00-\u9fff: 中文汉字
        # \u3000-\u303f: 中文标点
        # \uff00-\uffef: 全角字符
        pattern = r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffefa-zA-Z0-9\n]'
        matches = re.findall(pattern, text)
        
        # 将匹配结果拼接为字符串
        result = ''.join(matches)
        
        # 如果结果为空，返回空字符串
        return result if result else ""
    
    except Exception as e:
        print(f"提取过程中出错: {str(e)}")
        return None

log_path = os.path.join(os.path.dirname(__file__), "duckduckgo_search_optimized.log")

# 配置日志（确保这是唯一的日志配置）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DuckDuckGoSearchOptimized:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        初始化优化的 DuckDuckGo 搜索类
        
        Args:
            timeout: 网络请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = "https://duckduckgo.com/html/"
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
        """使用 jieba 分词提取名词和其他重要词语"""
        words = jieba.lcut(query)
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
            query_nouns = self._get_nouns(query)
            if not query_nouns:
                return 0.0

            content = (title.lower() + " " + snippet.lower())
            matched_nouns = [noun for noun in query_nouns if noun.lower() in content]
            noun_match_ratio = len(matched_nouns) / len(query_nouns) if query_nouns else 0.0
            if noun_match_ratio == 0:
                return 0.0

            domain = urlparse(url).netloc.lower()
            domain_score = 1.0
            for auth_domain, weight in self.authoritative_domains.items():
                if domain.endswith(auth_domain):
                    domain_score = weight
                    break

            page_content = self._fetch_page_content(url)
            if page_content:
                page_text = extract_chinese(page_content).lower()
                query_words = set(query.lower().split())
                content_words = set(page_text.split())
                content_match_ratio = len(query_words.intersection(content_words)) / len(query_words)
                
                word_frequency_score = 0
                for word in query_words:
                    word_frequency_score += page_text.count(word)
                word_frequency_score = min(word_frequency_score / len(query_words), 5)
            else:
                content_match_ratio = 0.0
                word_frequency_score = 0.0

            query_words = set(query.lower().split())
            title_words = set(title.lower().split())
            snippet_words = set(snippet.lower().split())
            
            title_match = len(query_words.intersection(title_words)) / len(query_words)
            snippet_match = len(query_words.intersection(snippet_words)) / len(query_words)
            title_similarity = SequenceMatcher(None, query.lower(), title.lower()).ratio()
            snippet_similarity = SequenceMatcher(None, query.lower(), snippet.lower()).ratio()

            score = (0.1 * noun_match_ratio + 
                     0.3 * content_match_ratio +
                     0.3 * (word_frequency_score / 5) +
                     0.05 * title_match + 
                     0.25 * snippet_match) * domain_score
            return min(score, 1.0)
        except Exception as e:
            logger.warning(f"计算相关性得分时出错: {str(e)}")
            return 0.0

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Optional[str]]]:
        """
        执行优化的 DuckDuckGo 搜索，返回 top-N 最相关结果
        
        Args:
            query: 搜索关键词
            max_results: 返回的最大结果数（默认10）
        
        Returns:
            List of dictionaries containing title, url, content, and relevance score
        """
        results = []
        try:
            params = {'q': query}
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

            # 解析搜索结果页面
            soup = BeautifulSoup(response.text, 'html.parser')
            candidates = []
            for item in soup.select('div.result.results_links_deep')[:30]:
                try:
                    title_tag = item.select_one('a.result__a')
                    title = title_tag.get_text().strip() if title_tag else "无标题"
                    url = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
                    snippet_tag = item.select_one('div.result__snippet')
                    snippet = snippet_tag.get_text().strip() if snippet_tag else ""

                    if url:
                        score = self._calculate_relevance_score(query, title, snippet, url)
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

            candidates.sort(key=lambda x: x['score'], reverse=True)
            top_candidates = candidates[:max_results]

            for candidate in top_candidates:  # 修复语法错误
                try:
                    content = self._fetch_page_content(candidate['url']) if candidate['url'] else "无法获取内容"
                    extract_chinese_content = extract_chinese(content)
                    results.append({
                        'title': candidate['title'],
                        'url': candidate['url'],
                        'core_content': extract_chinese_content,
                        'relevance_score': candidate['score']
                    })
                    logger.info(f"成功处理结果: {candidate['title']} ({candidate['url']})")
                except Exception as e:
                    logger.error(f"处理候选结果时出错: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"搜索过程中发生错误: {str(e)}")

        return results

    def _fetch_page_content(self, url: str) -> Optional[str]:
        """
        获取网页的完整 HTML 内容，处理可能的重定向
        
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
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    response.encoding = 'utf-8'
                    # 检查是否为重定向页面（例如 DuckDuckGo 的安全跳转）
                    soup = BeautifulSoup(response.text, 'html.parser')
                    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
                    if meta_refresh and 'content' in meta_refresh.attrs:
                        # 提取 meta 标签中的目标 URL
                        content = meta_refresh['content']
                        match = re.search(r'url=(.*)', content, re.IGNORECASE)
                        if match:
                            target_url = match.group(1)
                            logger.info(f"检测到重定向，目标 URL: {target_url}")
                            # 再次请求目标 URL
                            response = self.session.get(
                                target_url,
                                headers=self.headers,
                                timeout=self.timeout,
                                allow_redirects=True
                            )
                            response.raise_for_status()
                            response.encoding = 'utf-8'
                    return response.text if response.text else "无有效内容"
                except requests.RequestException as e:
                    logger.warning(f"获取网页内容失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    if attempt == self.max_retries - 1:
                        return None
        except Exception as e:
            logger.error(f"获取网页内容时出错: {str(e)}")
        return None

    def save_results(self, results: List[Dict[str, Optional[str]]], 
                    filename: str = 'duckduckgo_search_results.json',
                    output_format: str = 'json'):
        """
        将搜索结果保存为文件
        
        Args:
            results: 搜索结果列表
            filename: 保存文件名
            output_format: 输出格式，支持 'json' 或 'list'
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if output_format.lower() == 'json':
                    json.dump(results, f, ensure_ascii=False, indent=2)
                elif output_format.lower() == 'list':
                    for result in results:
                        f.write(f"标题: {result['title']}\n")
                        f.write(f"链接: {result['url']}\n")
                        f.write(f"内容预览: {result['core_content'][:200] + '...' if result['core_content'] and len(result['core_content']) > 200 else result['core_content']}\n")
                        f.write(f"相关性得分: {result['relevance_score']:.2f}\n")
                        f.write("-" * 80 + "\n\n")
                else:
                    raise ValueError("不支持的输出格式，请使用 'json' 或 'list'")
                    
            logger.info(f"搜索结果已保存至 {filename} (格式: {output_format})")
        except Exception as e:
            logger.error(f"保存搜索结果时出错: {str(e)}")

def main():
    """示例使用DuckDuckGo搜索引擎"""
    search_engine = DuckDuckGoSearchOptimized()
    query = input("请输入搜索关键词: ")
    output_format = input("请输入输出格式(json/list): ").strip().lower() or 'json'
    start_time = time.time()
    results = search_engine.search(query, max_results=10)
    
    # 控制台输出
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"标题: {result['title']}")
        print(f"链接: {result['url']}")
        print(f"内容预览: {result['core_content'][:200] + '...' if result['core_content'] and len(result['core_content']) > 200 else result['core_content']}")
        print(f"相关性得分: {result['relevance_score']:.2f}")
        print("-" * 80)
    
    # 文件保存
    search_engine.save_results(results, output_format=output_format)
    print(f"\n搜索用时: {time.time() - start_time:.2f} 秒")

if __name__ == "__main__":
    main()