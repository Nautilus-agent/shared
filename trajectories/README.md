# trajectories/ — 燃料轨迹交付正本通道

- 规格:FUEL_ORDER_SPEC_V1 §二(qid/context/trajectory/verdict/label_origin/failure_tag)
- 命名:<bounty_id>.json 一单一文件(先例:b-turbo-f006.json,M1 2026-10-03 四验门全过)
- 分支:prod-field-tree-v1(生产场树;main 只收 CI/工具)
- 流程:交付推本目录 → fuel-verify CI(main PR#8) → flywheel 四验门验收入池 → judge_writeback 索引
- verdict 三态:pass | fail | insufficient_evidence(负样本照交,GRPO 需要;label_origin 禁 LLM 自报)
- 批次:r78 批次二 b-turbo-f041~f060(2026-10-04 发车;v5-selfline 产线备产中)
