"""过滤/整理网页搜索结果 Node

Tavily 返回的 results 通常包含 url/title/content。这里不做爬虫抓全文，
只做：去重 + 简单相关性排序 + 拼接成可给 LLM 使用的 search_context。
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..spoilState import SpoilState


def _keywords(state: SpoilState) -> List[str]:
    base = (state.get("user_input") or "").strip()
    attrs = state.get("scene_attributes") or {}
    bits = [base]
    bits.extend([v for v in attrs.values() if isinstance(v, str) and v.strip()])

    # 简单切分：按空格/常见标点
    joined = " ".join(bits)
    for ch in ["\n", "\t", "，", "。", "、", ",", ".", "!", "?", "：", ":", "（", "）", "(", ")"]:
        joined = joined.replace(ch, " ")
    tokens = [t.strip() for t in joined.split(" ") if len(t.strip()) >= 2]

    # 去重
    seen = set()
    out: List[str] = []
    for t in tokens:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out[:12]


def _score_item(title: str, content: str, keywords: List[str]) -> int:
    text = (title + "\n" + content).lower()
    score = 0
    for kw in keywords:
        k = kw.lower()
        if not k:
            continue
        if k in text:
            score += 2
    # 轻微偏好更“内容型”的片段
    if len(content) > 120:
        score += 1
    return score


def fillter_web_node(state: SpoilState, llm: Any = None):
    """从 search_results 生成更紧凑的 search_context"""

    raw: Dict[str, Any] = state.get("search_results") or {}
    if not raw:
        return {"search_context": ""}

    keywords = _keywords(state)
    items: List[Tuple[int, str, str, str]] = []  # (score, url, title, content)
    seen_urls = set()

    for _, lst in raw.items():
        if not isinstance(lst, list):
            continue
        for it in lst:
            if not isinstance(it, dict):
                continue
            url = (it.get("url") or it.get("link") or "").strip()
            if not url or url in seen_urls:
                continue
            title = (it.get("title") or "").strip()
            content = (it.get("content") or it.get("snippet") or "").strip()
            seen_urls.add(url)
            score = _score_item(title, content, keywords)
            items.append((score, url, title, content))

    items.sort(key=lambda x: x[0], reverse=True)
    top = items[:5]
    lines: List[str] = []
    for score, url, title, content in top:
        content = content.replace("\n", " ").strip()
        if len(content) > 320:
            content = content[:320] + "…"
        lines.append(f"[{score}] {title}\n{url}\n{content}")

    return {"search_context": "\n\n".join(lines)}
