# S3 · g2b1 三层 join 燃料转换(e5_fuel_convert)

> **组织档案转存件** · 2026-10-05
> 原创正本:chunxiaoxx/nautilus-v5 @ customer-demo-ship-1 @ bbebae42 · `tools/uni_agent_bridge/e5_fuel_convert.py::load_fuel`(v5 回 #3095 转存请·沉淀提案 V1 之 S3)

## 接口

- 行为:g2b1 **三层 join**(starter_path × prompt × gold)——零编造通路:只有三源可 join 的任务才进训练/评测集。
- 输出:join 后任务集(供 r77 系发射)。

## 判据(三硬标准)

join 结果行数=三源交集**可复算**(重跑同数)。

## 实证

r77 发射坐标=e6_rl_v3+j2full77 现役由此通路供数。此件是"仓内闲置燃料证伪"后确立的唯一零编造转换路径(b1-fuel-reality 判例:4 类闲置燃料 0 行 tool_call 实证,唯 join 通路成立)。
