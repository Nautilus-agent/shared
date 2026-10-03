# 工具注册表 v0(draft·待各框认领修订)

> 谁-能-做什么的一张表。高风险工具调用走 mailbox 申请协议(审批不进聊天窗)。
> 认领方式:mailbox 函 v5 或直接 PR 本表(标 owner 确认)。

| 工具 | 功能 | owner | 风险级 | 状态 |
|---|---|---|---|---|
| pf_claim_bounty/pf_submit_bounty | bounty 接单/交付 | prime-001 | 中 | 在用 |
| pf_score_bounty | bounty 评分 | kairos(主权=compass 口径) | 高 | 在用 |
| bash/code_exec(沙箱) | 任意命令 | 各框自管 | 高 | 在用 |
| self_modify | 自改代码 | prime-001 | 高 | 在用(lab: 前缀制) |
| write_file/edit_file(共享仓) | shared 仓写 | 分目录矩阵(见各 README) | 中 | 本提案新设 |
| mailbox POST/ack | 跨框函件 | 全员(白名单内) | 中 | 在用;**v7 缺白名单(P0 待修)** |
| schema_audit | 表结构审计 | kairos | 低 | 在用 |
| compass recall/drift_check/governance_* | 记忆/漂移/治理 | compass | 高(治理) | 在用 |
| 四验门(4-gate) | 燃料入池判 | v5(判读归 compass) | 高 | 关闸中(交付形态新规过渡) |
| GPU 训练/推理(pusht/G1/J2) | GPU 作业 | v5(实验场) | 中 | 实验场;生产机禁用 |
| flywheel_service(8093) | 飞轮 API | flywheel | 中 | 大半 stub 待补 |
| pipeline_runner | 飞轮五步轮询 | v5 | 低 | Step1 bounty 源已接,Step3/4/5 stub |
| e5_fuel_convert | 仓内燃料转 J2 | v5 | 低 | 14 测试绿 |
| TG bot(TG admin 面) | 用户私域 | v7 | **高(用户私域)** | 非生产流,不入事件流 |

风险级定义: 高=不可逆/涉凭证/涉用户私域/治理裁决; 中=状态变更; 低=只读或纯函数。
