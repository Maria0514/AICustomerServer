"""属性提取 Node"""

import json
import streamlit as st
from typing import Any, Dict, List, TypedDict
from spoil.agents.metagpt_agents.utils.helper_func import (
    extract_single_type_attributes_and_examples,
    extract_attribute_descriptions,
    has_empty_values,
    is_number_in_types,
)
from ..config import SCENE_JSON
from ..prompts import REFINE_PROMPT_TEMPLATE, QUESTION_PROMPT_TEMPLATE


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


def format_history(history: List[Dict[str, str]]) -> str:
    return str(history)


def _sanitize_json(text: str) -> str:
    """清理 JSON 文本"""
    return (
        text.replace("```json", "")
        .replace("```", "")
        .replace(""", '"')
        .replace(""", '"')
        .replace("，", ",")
        .strip()
    )


def llm_invoke(prompt: str, llm: Any) -> str:
    """调用 LLM"""
    if hasattr(llm, "invoke"):
        return llm.invoke(prompt)
    if hasattr(llm, "_call"):
        return llm._call(prompt)
    return llm(prompt)


def ensure_scene_attributes(scene_label: str, current: Dict[str, str]) -> Dict[str, str]:
    """确保场景属性完整"""
    if scene_label and current:
        return current
    scene, attrs, _ = extract_single_type_attributes_and_examples(SCENE_JSON, scene_label)
    if not attrs:
        return current
    return {attr: current.get(attr, "") for attr in attrs}


def refine_node(state: TianjiState, llm: Any):
    """
    属性提取节点：从用户输入中提取文案创作所需的属性
    
    Args:
        state: 工作流状态
        llm: 语言模型实例
    
    Returns:
        更新后的状态字典，包含提取的属性和是否需要更多信息
    """
    scene_label_raw = state.get("scene_label", "").strip()
    scene_label = scene_label_raw.split("：")[0]
    
    if not scene_label or scene_label == "None" or not scene_label.isdigit() or not is_number_in_types(
        SCENE_JSON, int(scene_label)
    ):
        st.warning("此模型只支持回答关于小红书文案创作的事项，已调用 API 为你进行单轮回答。")
        rsp = llm_invoke(prompt=state["user_input"], llm=llm)
        return {"need_more_info": True, "final_answer": rsp if isinstance(rsp, str) else getattr(rsp, "content", str(rsp))}

    base_attrs = ensure_scene_attributes(scene_label, state.get("scene_attributes", {}))
    scene, _, _ = extract_single_type_attributes_and_examples(SCENE_JSON, scene_label)
    desc = extract_attribute_descriptions(SCENE_JSON, base_attrs)

    refine_prompt = REFINE_PROMPT_TEMPLATE.format(
        instruction=format_history(state["chat_history"]),
        scene=scene,
        scene_attributes=base_attrs,
        scene_attributes_description=desc,
    )
    refined_text = llm_invoke(refine_prompt, llm)
    refined = refined_text if isinstance(refined_text, str) else getattr(refined_text, "content", "")
    merged = base_attrs
    
    try:
        parsed = json.loads(_sanitize_json(refined))
        merged = {**base_attrs, **parsed}
    except Exception:
        merged = base_attrs

    if has_empty_values(merged):
        question_prompt = QUESTION_PROMPT_TEMPLATE.format(
            scene=scene,
            scene_attributes=merged,
            scene_attributes_description=desc,
        )
        question = llm_invoke(question_prompt, llm)
        q_content = question if isinstance(question, str) else getattr(question, "content", "")
        return {
            "scene_attributes": merged,
            "need_more_info": q_content.strip() != "Full",
            "final_answer": q_content if q_content.strip() != "Full" else "",
        }

    return {"scene_attributes": merged, "need_more_info": False}