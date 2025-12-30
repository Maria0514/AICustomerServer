from typing import Any, Dict, List, TypedDict

class SpoilState(TypedDict):
    user_input: str
    chat_history: List[Dict[str, str]]
    scene_label: str
    scene_attributes: Dict[str, str]
    retrieved_docs: List[str]
    search_enabled: bool
    search_results: Dict[str, Any]
    final_answer: str
    need_more_info: bool