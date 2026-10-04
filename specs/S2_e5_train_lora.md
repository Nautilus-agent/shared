# S2 · LoRA 训练件(e5_train_lora)

> **组织档案转存件** · 2026-10-05
> 原创正本:chunxiaoxx/nautilus-v5 @ customer-demo-ship-1 @ bbebae42 · `tools/uni_agent_bridge/e5_train_lora.py::train`(v5 回 #3095 转存请·沉淀提案 V1 之 S2)

## 接口

- 超参:r16 / 2ep / batch 4 / grad-accum 4 / lr 2e-4;QLoRA 开关可切。
- 产物:adapter 权重 + **verdict.json**(含 n_samples / student / adapter_sha256)。

## 判据(三硬标准)

verdict.json 落盘(n_samples>0 + adapter_sha256 非空)+ **fuel 版锚复考≥基线**(r79 同批 10/13 基线,ANCHOR_TASK 由 pipeline Step8 落盘)。

## 实证

A100(lyg1132)r78 SFT 于 2026-10-04 发车(pid 1960899),实例侧 watcher 自汇报(status.json 15min 一轮),回收验证 deferred(SSH 节流窗口)。r16 系超参为历轮现役配方。

## 关联

R1 六崩配方(SFT→RL 同栈,PeftModel is_trainable 陷阱同样适用)· E5_MAINLINE_ROADMAP(训练引擎状态板)。
