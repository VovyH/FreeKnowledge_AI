from dataclasses import dataclass

@dataclass
class SearchResult:
    """搜索结果类"""
    idx: int
    title: str 
    url: str 
    content: str 