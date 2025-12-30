"""LangGraph 工作流构建"""

from typing import Any, Dict
from langgraph.graph import END, StateGraph
from .nodes import *
from .spoilState import SpoilState


def build_xhs_workflow(llm: Any, retrievers: Dict[str, Any], tavily_client: Any = None):
    """
    构建小红书文案生成工作流
    
    Args:
        llm: 语言模型实例
        retrievers: 各场景的检索器字典
        tavily_client: Tavily 搜索客户端（可选）
    
    Returns:
        编译后的 LangGraph 工作流
    """
    workflow = StateGraph(SpoilState)
    
    # 添加节点
    workflow.add_node("intent", lambda state: intent_node(state, llm))
    workflow.add_node("refine", lambda state: refine_node(state, llm))
    workflow.add_node("rag", lambda state: rag_node(state, retrievers))
    workflow.add_node("search", lambda state: search_node(state, tavily_client))
    workflow.add_node("answer", lambda state: answer_node(state, llm))
    workflow.add_node("question", lambda state: question_node(state, llm))
    workflow.add_node("extend_query", lambda state: extend_query_node(state, llm))
    workflow.add_node("fillter_web", lambda state: fillter_web_node(state, llm))

    
    # 设置入口点
    workflow.set_entry_point("intent")
    workflow.add_edge("intent", "refine")
    
    # 条件分支：refine 之后，若只需要单轮对话则直接结束，否则进行rag
    def after_refine(state: SpoilState):
        return END if state.get("need_more_info") else "rag"
    
    workflow.add_conditional_edges("refine", after_refine, {"rag": "rag", END: END})
    
    # 条件分支：rag 之后，若开启了搜索功能则进行搜索第一步：写query，若未开启则进行答案生成
    def after_rag(state: SpoilState):
        return "search" if state.get("search_enabled") else "answer"
    
    workflow.add_conditional_edges("rag", after_rag, {"search": "extend_query", "answer": "answer"})
    
    # 其他边
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)
    
    return workflow.compile()