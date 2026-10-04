# S4 · B7 扩池同分布转换(e5_fuel_sft_convert)

> **组织档案转存件** · 2026-10-05
> 原创正本:chunxiaoxx/nautilus-v5 @ customer-demo-ship-1 @ bbebae42 · `tools/uni_agent_bridge/e5_fuel_sft_convert.py::convert`(v5 回 #3095 转存请·沉淀提案 V1 之 S4·防自喂门 7e505125)

## 接口

- 参数:`--staging`(fuel_trajectories staging jsonl,默认 STAGING 常量;pipeline Step7 显式传参)→ `--out`(SFT 样本 jsonl)。
- 行为:只收 **passed** 轨迹转 SFT 样本;**grpo-r79 前缀 qid 禁入**(学生自产禁回训练池,防自喂回路,代码门 commit 7e505125)。

## 判据(三硬标准)

passed-only 代码门 + r79 前缀禁入门 + 样本数上报(stats json:输入行/通过行/滤除行)。

## 实证

r78 批:pass 8 条→106 样本(8 uniq qids)。防自喂断言有测试(tests/test_pipeline_step6_8.py,测试样例用 r78 前缀分离验证)。配套扩池件:`tools/bench/expand_pool_from_trajectories.py`(池 109→676 unique,sha1 去重+held_out 整条排除)。

## Why(防自喂设计)

学生模型自产轨迹若回流训练池,形成自我强化回路(分布坍缩+判分信号失效)。同分布扩池只收**判分通过的**产线/履约轨迹,学生自产(grpo-r79 前缀)永久排除。
