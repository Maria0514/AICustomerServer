"""网络搜索 Node"""

from typing import Any, Dict, List, TypedDict


class TianjiState(TypedDict):
    user_input: str
    chat_history: List[Dict[str, str]]
    scene_label: str
    scene_attributes: Dict[str, str]
    retrieved_docs: List[str]
    search_enabled: bool
    search_results: Dict[str, Any]
    final_answer: str
    need_more_info: bool


def _generate_queries(state: TianjiState) -> List[str]:
    """生成搜索查询"""
    attrs = state.get("scene_attributes", {})
    base = state.get("user_input", "")
    scene_label = state.get("scene_label", "")
    queries = [base]
    extra_bits = [v for v in attrs.values() if v]
    
    if scene_label:
        queries.append(f"场景{scene_label} {base}")
    if extra_bits:
        queries.append(base + " " + " ".join(extra_bits[:3]))
    
    return queries


def search_node(state: TianjiState, tavily_client: Any):
    """
    网络搜索节点：使用 Tavily 搜索实时信息
    
    Args:
        state: 工作流状态
        tavily_client: Tavily 客户端
    
    Returns:
        更新后的状态字典，包含搜索结果
    """
    if not tavily_client:
        return {"search_results": {}}
    
    queries = state.get("search_queries") or _generate_queries(state)
    results: Dict[str, Any] = {}
    
    for idx, q in enumerate(queries):
        try:
            resp = tavily_client.search(q, max_results=5)
            results[str(idx)] = resp.get("results", [])
        except Exception:
            results[str(idx)] = []
    
    return {"search_results": results}