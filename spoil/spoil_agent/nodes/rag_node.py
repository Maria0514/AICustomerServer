"""RAG 检索 Node"""

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


def rag_node(state: TianjiState, retrievers: Dict[str, Any]):
    """
    RAG 检索节点：从知识库中检索相关文案
    
    Args:
        state: 工作流状态
        retrievers: 各场景的检索器字典
    
    Returns:
        更新后的状态字典，包含检索到的文档
    """
    scene_label = state.get("scene_label", "").split("：")[0].strip()
    retriever = retrievers.get(scene_label)
    docs = []
    
    if retriever:
        try:
            docs = retriever.invoke(state["user_input"]) or []
        except Exception:
            docs = []
    
    doc_texts = [d.page_content for d in docs][:5]
    return {"retrieved_docs": doc_texts}