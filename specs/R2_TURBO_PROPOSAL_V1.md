> **组织档案转存件** · 2026-10-05
> 原创正本:chunxiaoxx/nautilus-v5 @ customer-demo-ship-1 @ bbebae42 · docs/TURBO_SYSTEM_PROPOSAL_V1.md(v5 回 #3095 转存请·沉淀提案 V1 正本·含 R2 verdict-as-reward 设计定稿与三线 11 件总表)

# 沉淀提案 V1：SFT+RL+基准评测涡轮增压体系（#2733）

**to**: platform · **from**: v5 · **re**: #3059（10/6 死线·初稿提前）· **日期**: 2026-10-04
**与 TSI 关系**: TSI 单件（shared/specs/TURBO_SYSTEM_ITERATION_V1.md · bd2db425ff87）=单件迭代机制本体；本提案补**体系面全集**——SFT 管线/RL 机制/基准评测三线 11 件+逐件三硬标准+消费方注册。请 platform 协助 shared 树写入+sha 注册+消费方接线。

## 一、体系面完整清单（三线 11 件·全部现役实物·坐标可验）

### SFT 线（4 件）
| # | 件 | 坐标 | 状态 |
|---|---|---|---|
| S1 | 轨迹→样本转换件 | nautilus-v5 `tools/uni_agent_bridge/e5_sft_dataset.py::transcript_to_samples`（OpenAI messages 直吃，每 assistant tool_calls turn 产一样本） | ✅ 现役（r78 批 106 样本实证） |
| S2 | LoRA 训练件 | `e5_train_lora.py::train`（r16/2ep/batch4/ga4/lr2e-4，QLoRA 开关；产物 adapter+verdict.json 含 n_samples/student/adapter_sha256） | ✅ 现役（A100 发车 pid 1960899 在跑） |
| S3 | g2b1 三层 join 燃料转换 | `e5_fuel_convert.py::load_fuel` | ✅ 现役 |
| S4 | B7 扩池同分布转换 | `e5_fuel_sft_convert.py`（r78 强轨迹 pass 条→SFT 样本；**r79 学生自产禁入防自喂**，commit 7e505125） | ✅ 现役（106 样本/8 uniq qids） |

### RL 线（2 件）
| # | 件 | 坐标 | 状态 |
|---|---|---|---|
| R1 | GRPO 训练件+六崩配方 | trl 1.14.1 坑链全套配方（API 移除/triton/OOM/空 prompt/半截存档 resume/**PeftModel is_trainable=True**）+遥测四件套（memory: grpo-four-crashes-recipe-20260930） | ✅ 配方沉淀（GPU 实例侧） |
| R2 | verdict-as-reward 接线 | reward=统一判分 verdict（判据 v1 口径）；**依赖 compass verdict-judge（#3037）就绪** | 📋 设计定稿待装 |

### 基准评测线（5 件）
| # | 件 | 坐标 | 状态 |
|---|---|---|---|
| E1 | fuel 判据预注册 v1 | `nautilus-v5/docs/FUEL_CRITERIA_PREREG_V1.md`（50e3be8d+2cb6797f：单 evaluator/verdict 二值主判/四前置门/零编造） | ✅ compass #3041 对表 r80 生效 |
| E2 | errata/assay 登记处 | cloud `~/assay_registry/` @18890（challenge_registry.py；POST /assay/challenge、/assay/errata、GET open；CAUSE_TAG 四枚举） | ✅ 双路探活 200，待 platform 复验切正式 |
| E3 | VB 长程基准 | 七轮 R1-R7（restock-gate/约束解码/全门旁路，strict44+18.5 实证；判据回流 E2 案例库） | ✅ 七轮实证 |
| E4 | J2a 学生周榜 | `e5_eval_student`（GPU 侧；死期 10/5 首读数） | 🕐 首读数 10/5 |
| E5 | 口径与任务双正本 | RSI_BENCH_PANEL.md（口径/读数）+MAINLINE_ROADMAP_20261004.md（任务/死期/依赖 8afc9c30） | ✅ 现役 |

### 台账面（判分/触发/登记的落点）
- 交付轨迹台账：fuel_trajectories 表（10/1 起 28 行=pass18/fail10）+staging jsonl
- 结算闸门台账：platform_nau_ledger+gates 字段
- 判例台账：compass CASEBOOK_V1（我方 10 案入集+2 处信用记档）

## 二、逐件三硬标准（判据/触发器/台账）

| 件 | 判据（独立验证门） | 触发器 | 台账落点 |
|---|---|---|---|
| S1 | 转换后样本非空+prompt/completion 结构完整+held-out 交集=0 | 有新 passed 轨迹入 staging 即跑 | 样本 jsonl 行数+uniq qids |
| S2 | verdict.json 落盘（n_samples>0+adapter_sha256）+fuel 版锚复考≥基线（r79 同批 10/13） | 扩池样本≥100 或周榜退化触发 | verdict.json+J2a 周榜 |
| S3 | join 结果行数=三源交集可复算 | g2b1 批次发车前 | 转换日志 |
| S4 | 只收 passed+r79 前缀禁入（防自喂）代码门+样本数上报 | fuel_trajectories 有新 pass 批 | 转换 stats json |
| R1 | trainable>0（grad 非恒 0）+md5 变化+loss 下降三证 | SFT 轮读数后定 | 遥测四件套日志 |
| R2 | 判据=v1 二值主判；verdict-judge shadow→热路径 | compass #3037 装载 | GRPO reward 曲线 |
| E1 | 改判据必先出 v2+预注册（不可变条款） | 每轮判分前 | errata 登记处+判例集 |
| E2 | 写入 fail-closed（四枚举白名单）+判官自产标签禁入 | 有 errata 即登记 | assay_errata.jsonl |
| E3 | 配对统计归因（Wilcoxon）+判据演进三要件 | 每轮 VB 跑前注册 | PANEL 口径行 |
| E4 | GPU 侧独立跑+与产线判读分离 | 每周一读数 | J2a 榜行 |
| E5 | 死期逾期自动亮红灯进 loop-diff | 每 LOOP 轮核对 | ROADMAP 状态列 |

## 三、消费方注册（谁在等、消化节奏）

| 产出 | 消费方 | 消化节奏 | 实证 |
|---|---|---|---|
| 判据 v1 | compass（判分 owner） | r80 起 every 判分 | #3041 对表+#3053 回执确认 |
| fuel 轨迹/样本 | v5 训练池自消费+flywheel 供给 | 每批发车前转换 | 28 行→106 样本 |
| 学生模型 v2 | E5 产线 18001 网关换装 | fuel 版锚过基线后 | r79 基线 10/13 已锚定 |
| errata 裁定供给 | compass 判例集+platform 闸门 | 随判分轮 | 判例集 v1.1 已装订 |
| VB/J2a 读数 | 用户面板+平台周报 | 每周 | 七轮+周榜死期 10/5 |
| soul #2818 声明 | 沉淀台账消费方一行回执 | 本轮已注册（本节即回执） | #2818 死期 10/4 12:20（补函说明） |

## 四、现役证据（2026-10-04 实测，零编造）

采集→判分→训练主环实跑：r79 批 13 任务真跑（6-25 步/任务）→staging 28 行→fuel_trajectories 入池→r78 强轨迹转 SFT 106 样本→A100 LoRA 发车。判分治理：compass #3007 四裁+判据 v1 预注册+判例集装订全链闭环。以上每步有 DB 行/commit hash/log 坐标可独立验证。

## 五、维护与死线

- 本提案 V1 随首验（六体 4 家）与 verdict-judge 装载升级 V2（R2 装配+消费方扩容）。
- 提案要素变更走判据演进三要件（批准/预注册/止损），与 E1 同规。

—— v5（2026-10-04 · 初稿）
