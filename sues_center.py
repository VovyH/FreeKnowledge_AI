import enum
from matplotlib.pyplot import flag
import requests
import logging
import time
from typing import List, Dict, Optional
from sues_search_duckduckgo import DuckDuckGoSearchOptimized
from sues_search_baidu import BaiduSearchOptimized
from prompt import summary_prompt
from sues_config import config_args
from sues_search_duckduckgo import logger  # 从搜索模块导入logger

class SuesCenter:
    """
    SuesCenter 类负责与不同搜索引擎交互并处理搜索结果
    支持DuckDuckGo和百度搜索引擎
    """
    
    def __init__(self):
        """初始化问答中心，配置API密钥和搜索引擎"""
        self.api_key = config_args.model_key
        self.search_engines = {
            "DUCKDUCKGO": DuckDuckGoSearchOptimized(),
            "BAIDU": BaiduSearchOptimized()
        }
        self.retry = config_args.chat_model_retry

    def get_response(self,
                   prompt: str,
                   flag: bool = True,
                   mode: str = "DUCKDUCKGO", 
                   model: str = config_args.chat_model_type,
                   base_url: str = config_args.model_base_url,
                   key: str = config_args.model_key,
                   max_web_results: int = config_args.max_web_results) -> List[Dict[str, Optional[str]]]:
        """
        获取问题的外部知识响应
        
        Args:
            prompt: 用户输入的问题
            flag: 是否使用大模型提取核心内容，默认为True
            mode: 搜索引擎选择，支持"DUCKDUCKGO"和"BAIDU"，默认为"DUCKDUCKGO"
            model: 大模型类型，默认从配置中获取
            base_url: 大模型API基础URL，默认从配置中获取
            key: API密钥，默认从配置中获取
            max_web_results: 最大Web结果数，默认从配置中获取
            
        Returns:
            包含外部知识的字典列表
        """
        try:
            logger.info(f"开始处理问题: {prompt}")
            search_engine = self.search_engines.get(mode)
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
            logger.info(f"问题处理完成: {prompt}, 结果数: {len(results)}")  # 添加完成日志
            return results
            
        except Exception as e:
            logger.error(f"处理问题时发生错误: {str(e)}", exc_info=True)  # 添加错误日志
            return []
            
        return "未能生成回答"

def main():
    center = SuesCenter()
    while True:
        question = input("\n请输入您的问题(输入q退出): ").strip()
        if question.lower() == 'q':
            break
            
        start_time = time.time()
        mode = "BAIDU"
        flag =True
        results = center.get_response(question, flag, mode)
        for result in results:
            print(f"\n回答: {result}")
        print(f"\n处理时间: {time.time() - start_time:.2f}秒")

if __name__ == "__main__":
    main()

