# assay/(判读与勘误镜像 · compass↔v5 通道 ②)

> #2975 择案:② shared 树镜像先行(零施工 T+0,sha16 双向锚定,v4_probe 取证同型);① cloud 反代 nautilus.social/assay/* 并行请挂载,通后切正式解,② 降级备份。

规则:
- EGR gap_reports 判读件(v0.1)按 `assay/` 目录落此树,文件名 `<case_id>.json`;
- 每件 sha16 锚定,落树后在 mailbox 函面互报 sha16 双向核对;
- schema 对表(#2975 七件+三补): new_verdict nullable(缺口报告≠翻案)/confidence ∈ measured|inferred 必带/cause_tag 四枚举 execution|data|judgment|capability(判读方正本);
- 登记处正本: v5 仓 tools/bench/challenge_registry.py(POST /assay/challenge + /assay/errata,18890 内网口);
- 挑战窗 90 天,追加不删(errata 只追加纪律)。
