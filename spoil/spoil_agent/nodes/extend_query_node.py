"""扩展查询 Node

该节点将用户需求 + 场景属性整理成 3-5 个更适合搜索的 query。
优先用 LLM 生成结构化列表；失败则回退到规则拼接。
"""

from __future__ import annotations

import ast
from typing import Any, Dict, List

from ..spoilState import SpoilState


def llm_invoke(prompt: str, llm: Any) -> str:
    if hasattr(llm, "invoke"):
        return llm.invoke(prompt)
    if hasattr(llm, "_call"):
        return llm._call(prompt)
    return llm(prompt)


def _fallback_queries(state: SpoilState) -> List[str]:
    base = (state.get("user_input") or "").strip()
    scene_label = (state.get("scene_label") or "").strip()
    attrs = state.get("scene_attributes") or {}

    extra_bits = [v for v in attrs.values() if isinstance(v, str) and v.strip()]
    queries: List[str] = []
    if base:
        queries.append(base)
    if scene_label and base:
        queries.append(f"{scene_label} {base}")
    if base and extra_bits:
        queries.append(base + " " + " ".join(extra_bits[:3]))
    if extra_bits:
        queries.append("小红书 文案 " + " ".join(extra_bits[:4]))

    # 去重保持顺序
    dedup: List[str] = []
    seen = set()
    for q in queries:
        q = q.strip()
        if not q or q in seen:
            continue
        seen.add(q)
        dedup.append(q)
    return dedup[:5]


def extend_query_node(state: SpoilState, llm: Any):
    """生成搜索查询列表并写入 state.search_queries"""

    base = (state.get("user_input") or "").strip()
    attrs = state.get("scene_attributes") or {}
    scene_label = (state.get("scene_label") or "").strip()

    # 低信息输入直接回退
    if not base:
        return {"search_queries": []}

    prompt = f"""
# Role: 搜索查询生成器

请基于用户要写的小红书文案需求，生成 3-5 条可用于实时搜索的中文查询。

要求：
- 只输出 Python 列表字符串，例如：["查询1","查询2"]
- 查询要具体，优先包含核心对象/地点/品牌/主题/时间等
- 不要输出解释

输入：
- 用户需求：```{base}```
- 已提取属性：```{attrs}```
- 内容类型标记：```{scene_label}```
""".strip()

    try:
        rsp = llm_invoke(prompt, llm)
        text = rsp if isinstance(rsp, str) else getattr(rsp, "content", str(rsp))
        cleaned = (
            text.replace("```", "")
            .replace("```list", "")
            .replace("“", '"')
            .replace("”", '"')
            .replace("，", ",")
            .strip()
        )
        queries = ast.literal_eval(cleaned)
        if not isinstance(queries, list):
            raise ValueError("LLM did not return a list")
        queries = [str(q).strip() for q in queries if str(q).strip()]
        # 去重
        dedup: List[str] = []
        seen = set()
        for q in queries:
            if q in seen:
                continue
            seen.add(q)
            dedup.append(q)
        return {"search_queries": dedup[:5]}
    except Exception:
        return {"search_queries": _fallback_queries(state)}
