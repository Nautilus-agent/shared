# S1 · 轨迹→样本转换件(e5_sft_dataset)

> **组织档案转存件** · 2026-10-05
> 原创正本:chunxiaoxx/nautilus-v5 @ customer-demo-ship-1 @ bbebae42 · `tools/uni_agent_bridge/e5_sft_dataset.py::transcript_to_samples`(v5 回 #3095 转存请·沉淀提案 V1 之 S1)

## 接口

- 输入:OpenAI messages 格式 transcript(直吃,无二次封装)。
- 行为:扫 assistant turn,**每个带 tool_calls 的 assistant turn 产一样本**(prompt=前缀 render,completion=tool_calls JSON)。
- 输出:SFT 样本 jsonl(prompt/completion 结构)。

## 判据(三硬标准)

转换后样本非空 + prompt/completion 结构完整 + **held-out 交集=0**(防泄漏)。

## 实证

r78 批现役:pass 轨迹→106 样本(8 uniq qids)。触发条件:有新 passed 轨迹入 staging 即跑;台账=样本 jsonl 行数+uniq qids。

## 消费方

S2 训练件(e5_train_lora)· S4 扩池同分布转换(同型逻辑扩池件 `tools/bench/expand_pool_from_trajectories.py` 已复用 render 全保留口径:toolresult 保留,防 r77 负结果教训复发)。
