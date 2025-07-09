import os
import logging
from typing import List, Dict, Optional

from FreeKnowledge_AI.sues_center import SuesCenter
from FreeKnowledge_AI.sues_config import config_args

# 配置日志
log_path = os.path.join(os.path.dirname(__file__), "knowledge_center.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Center:
    """
    Main class for FreeKnowledge AI.
    Provides access to external knowledge through various search engines.
    """
    
    def __init__(self):
        """Initialize the knowledge center."""
        self.sues_center = SuesCenter()
        logger.info("Knowledge Center initialized")
        
    def get_response(
            self, 
            question: str, 
            flag: bool = True, 
            mode: str = "DUCKDUCKGO",
            specific_url: Optional[str] = None
            model: str = config_args.chat_model_type,
            base_url: str = config_args.model_base_url,
            key: str = config_args.model_key,
            max_web_results: int = config_args.max_web_results,
        ) -> List[Dict[str, Optional[str]]]:
        """
        Get external knowledge response for a question or fetch content from specific URL.
        
        Args:
            question: Question entered by the user or a placeholder when using specific_url.
            flag: Whether to use a large model to extract content (Default: True).
            mode: "BAIDU", "DUCKDUCKGO", or "URL_SPECIFIC" (Default: "DUCKDUCKGO").
            model: Large model to use (Default: from config).
            base_url: Model API base URL (Default: from config).
            key: API key (Default: from config).
            max_web_results: Maximum number of web results to return (Default: from config).
            specific_url: Specific URL to crawl (only used when mode="URL_SPECIFIC").
            
        Returns:
            List of dictionaries containing external knowledge.
        """
        logger.info(f"Processing query: {question}")
        results = self.sues_center.get_response(
            question, flag, mode, model, base_url, key, max_web_results, specific_url
        )
        logger.info(f"Retrieved {len(results)} results for question: {question}")
        return results 
        
    def get_url_content(
            self, 
            url: str, 
            flag: bool = True,
            model: str = config_args.chat_model_type,
            base_url: str = config_args.model_base_url,
            key: str = config_args.model_key
        ) -> List[Dict[str, Optional[str]]]:
        """
        Convenient method to directly fetch content from a specific URL.
        
        Args:
            url: URL to crawl.
            flag: Whether to use a large model to extract content (Default: True).
            model: Large model to use (Default: from config).
            base_url: Model API base URL (Default: from config).
            key: API key (Default: from config).
            
        Returns:
            List containing a dictionary with the URL content (usually only one item).
        """
        logger.info(f"Fetching content from URL: {url}")
        return self.get_response(
            question="URL content request", 
            flag=flag,
            mode="URL_SPECIFIC", 
            model=model,
            base_url=base_url,
            key=key,
            specific_url=url
        )