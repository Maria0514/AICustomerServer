"""常量配置"""

from spoil.agents.metagpt_agents.utils.helper_func import (
    extract_all_types,
    extract_all_types_and_examples,
    load_json,
)

# 加载 scene_attribute.json
SCENE_JSON = load_json("scene_attribute.json")
SCENE_OPTIONS = extract_all_types(SCENE_JSON)
SCENE_EXAMPLES = extract_all_types_and_examples(SCENE_JSON)

# RAG 场景映射
RAG_SCENE_MAP = {
    "1": ("生活分享", "1-lifestyle"),
    "2": ("美妆护肤", "2-beauty"),
    "3": ("时尚穿搭", "3-fashion"),
    "4": ("运动健康", "4-fitness"),
    "5": ("科技数码", "5-tech"),
    "6": ("音乐影视", "6-entertainment"),
    "7": ("书籍阅读", "7-reading"),
    "8": ("宠物生活", "8-pets"),
}