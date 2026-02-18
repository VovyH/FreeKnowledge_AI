"""
搜索结果数据结构 - 定义搜索结果的标准数据类
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchResult:
    idx: int
    title: str 
    url: str 
    content: str 