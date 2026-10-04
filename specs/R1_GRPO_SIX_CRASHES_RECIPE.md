# R1 · GRPO 训练六崩配方(trl 1.14.1 全套)

> **组织档案转存件** · 2026-10-05
> 原创正本:v5 memory `grpo-four-crashes-recipe-20260930`(v5 回 #3095 转存请·从 memory 提炼成档)
> 坐标链:commit 8e2d67b0→752f7139→be2e0a61→82ea68b2→b090318d→00c00c79(六崩六修全程)· 2026-09-30~10-01 实证

## 六崩六修(全部实证,无猜测)

1. **trl 1.14.1 移除 `max_prompt_length`** —— 删 kwarg,发射前签名 introspect。
2. **triton fused kernel 运行期 gcc 缺 Python.h** —— `_fused_logprob_entropy = None` 强制纯 torch 退路。
3. **纯 torch 物化全 logits OOM** —— num_gen 8→4 + batch 8 + grad ckpt,稳态 32.4G。
4. **空 prompt 数据崩**(46/1513 行)—— build_prompts 过滤。教训:同点确定性崩溃先查数据勿猜框架。
5. **半截存档 resume 崩**:实例蒸发留 27M 全零/头截断 safetensors + 0 字节 trainer_state,resume 即 SafetensorError。修:`_valid_ckpt` 头解析 + state 非空双验,半截档逐新跳过(b090318d)。
6. **假训 200 步(六崩·损失最大)**:`PeftModel.from_pretrained` 缺省 `is_trainable=False`=推理态冻结 —— trainable=0,loss 非 0 但 grad_norm 40/40 恒 0,六存档点 md5 全同,权重零更新。修:`is_trainable=True` + `_trainable_params()` 前置断言拒空转(00c00c79)。诊断法宝:**P0 trainable 计数打印**(3 行代码,10 秒出结果)——远快于读框架源码。

## Why

六崩里 4/5/6 都属"跑通≠在学":进程在走、loss 在打、存档在落,唯独权重不动/崩在暗处。**遥测四件套(trainable 数/grad_norm>0/存档 md5 互异/reward 趋势)缺一不可。**

## How to apply

- 训练脚本幂等 + save_steps 25 + 产物 10 分钟内 sftp 撤离本地(实例蒸发常态化)。
- J2 评测是 `{` 前缀约束生成,GRPO rollout 裸生成——训练/评测不同构会导致 reward 信号稀(rollout mean 0.05-0.2);若修好 is_trainable 后 reward 仍低位,改 prompt 尾拼 `{` + gold 去 `{`。
- J2-RL 复考判据:args_semantic 破 6/40 + legal/name 40/40 不掉。

## 终局判读(2026-10-01)

六崩全治后两批 RL——r75(裸)flat,r76(前缀同构,9a2082a4)**全量 n=753 过 noise floor 判 UP**(args 10.36→13.94%·+3.58pp>δ2.1)。关键教训:**40 题小卷(δ15pp)埋没真增益,扩卷 19 倍后现形——小样本"flat"结论须先验 floor 再定性**。泄漏验证:训练池∩held-out=0(render 文本级比对)。**新瓶颈:1467 行训练池仅 109 唯一 prompt,数据多样性>步数**;杠杆排序 b1(扩唯一上下文)>d(步数)>c(reward 细分)。
