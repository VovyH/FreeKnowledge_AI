import enum
from matplotlib.pyplot import flag
import requests
import logging
import time
import os
import json
import re
from typing import List, Dict, Optional
from sues_search_duckduckgo import DuckDuckGoSearchOptimized
from sues_search_baidu import BaiduSearchOptimized
from UrlSpecificCrawler import UrlSpecificCrawler
from prompt import summary_prompt
from sues_config import config_args
from sues_search_duckduckgo import logger  # 从搜索模块导入logger

class SuesCenter:
    """
    SuesCenter 类负责与不同搜索引擎交互并处理搜索结果
    支持DuckDuckGo、百度搜索引擎和直接URL爬取
    """
    
    def __init__(self):
        """初始化问答中心，配置API密钥和搜索引擎"""
        self.api_key = config_args.model_key
        self.search_engines = {
            "DUCKDUCKGO": DuckDuckGoSearchOptimized(),
            "BAIDU": BaiduSearchOptimized(),
            "URL_SPECIFIC": UrlSpecificCrawler()  # 添加URL专用爬虫
        }
        self.retry = config_args.chat_model_retry
        logger.info("SUES问答中心初始化完成")

    def get_response(self,
                   prompt: str,
                   flag: bool = True,
                   mode: str = "DUCKDUCKGO", 
                   model: str = config_args.chat_model_type,
                   base_url: str = config_args.model_base_url,
                   key: str = config_args.model_key,
                   max_web_results: int = config_args.max_web_results,
                   specific_url: Optional[str] = None,
                   save_format: Optional[str] = None) -> List[Dict[str, Optional[str]]]:
        """
        获取问题的外部知识响应或特定URL的内容
        
        Args:
            prompt: 用户输入的问题
            flag: 是否使用大模型提取核心内容，默认为True
            mode: 搜索引擎选择，支持"DUCKDUCKGO"、"BAIDU"和"URL_SPECIFIC"，默认为"DUCKDUCKGO"
            model: 大模型类型，默认从配置中获取
            base_url: 大模型API基础URL，默认从配置中获取
            key: API密钥，默认从配置中获取
            max_web_results: 最大Web结果数，默认从配置中获取
            specific_url: 指定要爬取的URL（仅mode="URL_SPECIFIC"时使用）
            save_format: 保存格式，如果为"json"则自动保存，否则不保存
            
        Returns:
            包含外部知识的字典列表
        """
        try:
            logger.info(f"开始处理内容: {prompt}")
            search_engine = self.search_engines.get(mode)
            
            # 特定URL爬取模式
            if mode == "URL_SPECIFIC" and specific_url:
                logger.info(f"使用URL直接爬取模式: {specific_url}")
                web_result = search_engine.fetch_content(specific_url)
                if not web_result:
                    logger.warning(f"无法爬取URL: {specific_url}")
                    return []
                    
                web_results = [web_result]
            else:
                # 常规搜索模式
                web_results = search_engine.search(prompt, max_results=max_web_results)
            
            if not web_results:
                logger.warning(f"未获取到搜索结果: {prompt}")
                return []
            
            results = []
            if flag:
                # 使用大模型提取核心内容
                for i, web_result in enumerate(web_results):
                    logger.debug(f"处理第{i+1}个搜索结果: {web_result['title']}")
                    i += 1
                    formatted_prompt = summary_prompt.format(question = prompt, web_knowledge = web_result['core_content'])
                
                    # 3. 调用API获取回答
                    url = base_url
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": formatted_prompt}]
                    }
                    headers = {
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    }
                
                    for attempt in range(self.retry):
                        try:
                            response = requests.post(url, json=payload, headers=headers)
                            response.raise_for_status()
                            
                            response_data = response.json()
                            cleaned_content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "未找到内容")
                            
                            logger.info(f"成功响应-{i}，问题：{prompt}")
                            results.append({
                                'idx': i,
                                'title': web_result['title'],
                                'question': prompt,
                                'url': web_result['url'],
                                'content': cleaned_content
                            })
                            break
                            
                        except requests.exceptions.RequestException as e:
                            logger.warning(f"API请求失败 (尝试 {attempt + 1}/{self.retry}): {str(e)}")
                            if attempt == self.retry - 1:
                                logger.error("达到最大重试次数，请求失败")
                                continue
                            time.sleep(5)
            else:
                results = web_results
                
            logger.info(f"问题处理完成: {prompt}, 结果数: {len(results)}")
        
            if save_format and save_format.lower() == "json" and results:
                filename = self._generate_filename_from_question(prompt)
                self.save_results(results, filename=filename, output_format="json")
                logger.info(f"自动保存搜索结果到 {filename}")
            
            return results
            
        except Exception as e:
            logger.error(f"处理问题时发生错误: {str(e)}", exc_info=True)  # 添加错误日志
            return []
            
        return "未能生成回答"
        
    def _generate_filename_from_question(self, question: str) -> str:
        """
        根据问题生成有效的文件名
        
        Args:
            question: 用户问题
            
        Returns:
            有效的文件名
        """
        valid_filename = re.sub(r'[\\/*?:"<>|]', "", question)
        if len(valid_filename) > 50:
            valid_filename = valid_filename[:50]
        return f"{valid_filename}.json"
    def save_results(self, results: List[Dict[str, Optional[str]]], 
                    filename: str = 'search_results.json',
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
                        f.write(f"索引: {result.get('idx', 'N/A')}\n")
                        f.write(f"标题: {result.get('title', 'N/A')}\n")
                        f.write(f"问题: {result.get('question', 'N/A')}\n")
                        f.write(f"链接: {result.get('url', 'N/A')}\n")
                        f.write(f"内容: {result.get('content', 'N/A')[:200] + '...' if result.get('content') and len(result.get('content', '')) > 200 else result.get('content', 'N/A')}\n")
                        f.write("-" * 80 + "\n\n")
                else:
                    raise ValueError("不支持的输出格式，请使用 'json' 或 'list'")
                    
            logger.info(f"搜索结果已保存至 {filename} (格式: {output_format})")
        except Exception as e:
            logger.error(f"保存搜索结果时出错: {str(e)}")

def main():
    center = SuesCenter()
    while True:
        question = input("\n请输入您的问题(输入q退出): ").strip()
        if question.lower() == 'q':
            break
            
        start_time = time.time()
        mode = "BAIDU"
        flag = True
        save_json = input("是否保存为JSON格式(y/n, 默认n): ").strip().lower() == 'y'
        save_format = "json" if save_json else None
            
        results = center.get_response(question, flag=flag, mode=mode, save_format=save_format)
        
        # 显示结果
        for result in results:
            print(f"\n回答: {result}")
            
        print(f"\n处理时间: {time.time() - start_time:.2f}秒")

if __name__ == "__main__":
    main()

