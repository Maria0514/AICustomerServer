"""追问 Node

当 refine_node 判定还缺关键属性时，用该节点生成一个自然的追问。
"""

from __future__ import annotations

from typing import Any

from spoil.agents.metagpt_agents.utils.helper_func import (
    extract_single_type_attributes_and_examples,
    extract_attribute_descriptions,
)

from ..config import SCENE_JSON
from ..prompts import QUESTION_PROMPT_TEMPLATE
from ..spoilState import SpoilState


def llm_invoke(prompt: str, llm: Any) -> str:
    if hasattr(llm, "invoke"):
        return llm.invoke(prompt)
    if hasattr(llm, "_call"):
        return llm._call(prompt)
    return llm(prompt)


def question_node(state: SpoilState, llm: Any):
    # refine_node 可能已经生成了 final_answer（追问）。这里做兜底。
    if state.get("final_answer"):
        # LangGraph 要求节点至少写入一个字段，否则会触发 InvalidUpdateError。
        return {"final_answer": state.get("final_answer", ""), "need_more_info": True}

    scene_label = (state.get("scene_label") or "").split("：")[0].strip()
    scene, _, _ = extract_single_type_attributes_and_examples(SCENE_JSON, scene_label)
    attrs = state.get("scene_attributes") or {}
    desc = extract_attribute_descriptions(SCENE_JSON, attrs)

    prompt = QUESTION_PROMPT_TEMPLATE.format(
        scene=scene,
        scene_attributes=attrs,
        scene_attributes_description=desc,
    )
    rsp = llm_invoke(prompt, llm)
    text = rsp if isinstance(rsp, str) else getattr(rsp, "content", str(rsp))
    if text.strip() == "Full":
        return {"need_more_info": False}
    return {"final_answer": text, "need_more_info": True}
