rag改进建议（都可以只改现有文件，不新增文件）

- [x] 让检索更“懂需求”：在 rag_node.py 把 query 从 user_input 升级为 user_input + scene_attributes 关键字段（例如把“内容主题/产品类型/目标受众”等非空值拼接进去），并在多轮对话时优先使用最新的“已确认属性”而不是纯自然语言。
- [x] 控制 TopK 与多样性：在 demo_agent_metagpt_refactored.py 构造 retriever 时用 vectordb.as_retriever(search_kwargs={"k": 6})（或 MMR：search_type="mmr", search_kwargs={"k": 6, "fetch_k": 20}）提升覆盖面，减少“检索到一堆相似段落”的情况。
- [x] 提升 chunk 策略：中文+小红书文案通常短段密集，chunk_size=896 可能偏大；可以尝试 chunk_size=400~700、chunk_overlap=80~150，让检索更精细，减少“一个 chunk 混进太多无关技巧”的噪声（修改点仍在 demo_agent_metagpt_refactored.py）
- [ ] 加入轻量去重/清洗：在 rag_node.py 对 page_content 做简单去重（完全相同或高度重复的段落跳过），并限制每段最大长度，避免把长文本撑爆上下文窗口。
- [ ] 文本内容改成高质量示例，同时格式上改成jsonl