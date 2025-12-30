"""
这是一个单例模式的共享数据类，用于在多个智能体之间共享数据。
主要功能:
1. 维护每个用户会话的独立数据实例
2. 存储场景标签、属性、搜索结果等会话状态
3. 保存用户的聊天历史和消息列表
4. 通过uuid区分不同用户的数据
"""

import streamlit as st


class SharedDataSingleton:
    _instance = None
    json_from_data = None  # 这是要共享的变量
    message_list_for_agent = []
    filter_weblist = []
    scene_label = ""
    scene_attribute = {}
    extra_query = []
    search_results = {}
    chat_history = []
    uuid_obj = {}
    ask_num = 0

    @classmethod
    def get_instance(cls):
        user_id = ""
        if "user_id" in st.session_state:
            user_id = st.session_state["user_id"]
        if user_id == "":
            inst = cls()
            return SharedDataSingleton._new_init(inst)

        if user_id not in SharedDataSingleton.uuid_obj:
            inst = cls()
            SharedDataSingleton.uuid_obj[user_id] = SharedDataSingleton._new_init(inst)
        return SharedDataSingleton.uuid_obj[user_id]

    def _new_init(inst):
        # 注意：这里初始化的是“当前会话实例”的字段，不应该重置全局 uuid_obj
        inst._instance = None
        inst.json_from_data = None
        inst.message_list_for_agent = []
        inst.filter_weblist = []
        inst.scene_attribute = {}
        inst.scene_label = ""
        inst.extra_query = []
        inst.search_results = {}
        inst.chat_history = []
        inst.ask_num = 0
        return inst

    def __init__(self):
        if SharedDataSingleton._instance is not None:
            raise Exception("This class is a singleton!")
        # 可以在这里初始化共享变量
        self.json_from_data = {
            "requirement": "",
            "scene": "",
            "festival": "",
            "role": "",
            "age": "",
            "career": "",
            "state": "",
            "character": "",
            "time": "",
            "hobby": "",
            "wish": "",
        }

    # 可以添加更多方法来操作 shared_variable
