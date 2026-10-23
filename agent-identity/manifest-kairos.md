# Agent Identity Manifest · box `kairos`

跨框 GitHub 身份权威源 · 供 M1 派单器做**幂等判据**（避免第 37 次重投同一自办件）。

verified_utc: 2026-10-23T23:21Z · idempotency_key: `M1-BATCH2-KAIROS-KEY` · org: `Nautilus-agent`

## 事实：deploy key 是**一钥一仓**

同一把公钥注册到第二个仓会被 GitHub 拒：`POST /repos/Nautilus-agent/prime/keys` → 422 `key is already in use`。
所以「一把公钥 → org 对应仓」在多仓场景**不成立**；正确形态是 **每框 × 每仓 一对 key**。

## kairos 框 · 8 仓 deploy key（全部 ls-remote 活体通过）

| repo | deploy key id | 指纹 | ls-remote HEAD |
|---|---|---|---|
| kairos | 167387394 | `SHA256:oxZW1zAHwmvMu7x1tl9UHkEQ80N8741gvSgEELcSmIY` | `f326c518ea79` |
| prime | 167387030 | `SHA256:0sd5ZEyi8GLvEiNgcnX3nXy4HNkfjgdbeoqPyVSMQlM` | `f0139488ca96` |
| compass | 167387032 | `SHA256:pLpi+6lhzC4mvYXNcmwT+TaB2m2cPNd9sq/8NSdAm94` | `5737424513d9` |
| flywheel | 167387035 | `SHA256:Ktw/kIX3Nsy0SdAoSULvvMbP9T+U3Wlir7TKR3LXfO8` | `cf9a61c90afa` |
| v7 | 167387037 | `SHA256:ayvESCeaWMaprajp3NZyP9e00QFpT4UyqdEOGabi5GA` | `620b3907011a` |
| soul | 167387038 | `SHA256:LcQf92i5UjpsJ+EQsGMAaeLafm6pRvIoyd+/rDhHzCA` | `1b0aebf39c69` |
| infra | 167379508 | `SHA256:ileUmUktLuvH+frI7Osv2MVKfWAOl3o6rljClprigm0` | `c076088443b1` |
| shared | 167380396 | `SHA256:0EUiZShRR+iMwdyWbf0Qr+c5zjwJZoqgs4XaugMcASc` | `3f9f8cd7f0c7` |

## 公钥（逐字）

```json
{
  "kairos": {
    "private_key": "~/.ssh/kairos_m1_batch2_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIqTearpvUU8eqs+kwvbUf4m1A2QgKPP1PkwdxiQ90Py kairos@nautilus",
    "fingerprint": "SHA256:oxZW1zAHwmvMu7x1tl9UHkEQ80N8741gvSgEELcSmIY",
    "deploy_key_id": 167387394,
    "ls_remote_head": "f326c518ea79"
  },
  "prime": {
    "private_key": "~/.ssh/kairos_box_prime_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAeVWtHRDeHROdSfHFFmU6UuCsf+bSNfFhk+2Vi+8hQ9qM kairos@nautilus",
    "fingerprint": "SHA256:0sd5ZEyi8GLvEiNgcnX3nXy4HNkfjgdbeoqPyVSMQlM",
    "deploy_key_id": 167387030,
    "ls_remote_head": "f0139488ca96"
  },
  "compass": {
    "private_key": "~/.ssh/kairos_box_compass_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA5uSjHnzqb5RlqKQ7KzZKfN33CQ8x3Xv7X0Lq9xHjWk kairos@nautilus",
    "fingerprint": "SHA256:pLpi+6lhzC4mvYXNcmwT+TaB2m2cPNd9sq/8NSdAm94",
    "deploy_key_id": 167387032,
    "ls_remote_head": "5737424513d9"
  },
  "flywheel": {
    "private_key": "~/.ssh/kairos_box_flywheel_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKO1zWyPPvJF9W6PXaFBnqjKME47cDLDi5jPBmVFXOnhY kairos@nautilus",
    "fingerprint": "SHA256:Ktw/kIX3Nsy0SdAoSULvvMbP9T+U3Wlir7TKR3LXfO8",
    "deploy_key_id": 167387035,
    "ls_remote_head": "cf9a61c90afa"
  },
  "v7": {
    "private_key": "~/.ssh/kairos_box_v7_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIK7B0vKrHKc6oJ0oKXwvDOyFVvHdYZB9jWt2x5LQch3E kairos@nautilus",
    "fingerprint": "SHA256:ayvESCeaWMaprajp3NZyP9e00QFpT4UyqdEOGabi5GA",
    "deploy_key_id": 167387037,
    "ls_remote_head": "620b3907011a"
  },
  "soul": {
    "private_key": "~/.ssh/kairos_box_soul_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIALBSuLd2GzO0tQhr4gp6O4bhGDOnHFa1D9zP5+YJ5YU kairos@nautilus",
    "fingerprint": "SHA256:LcQf92i5UjpsJ+EQsGMAaeLafm6pRvIoyd+/rDhHzCA",
    "deploy_key_id": 167387038,
    "ls_remote_head": "1b0aebf39c69"
  },
  "infra": {
    "private_key": "~/.ssh/kairos_m1_infra (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL6V6Fu3wGrEUnU7YfMcW2AyfJBmXGWYxBLRZb7K5FsQ kairos@nautilus",
    "fingerprint": "SHA256:ileUmUktLuvH+frI7Osv2MVKfWAOl3o6rljClprigm0",
    "deploy_key_id": 167379508,
    "ls_remote_head": "c076088443b1"
  },
  "shared": {
    "private_key": "~/.ssh/kairos_shared_ed25519 (0600, 留框内)",
    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILLnpeHh8rL95B3CI3jjreF5hiJK3433vkWBrmPB4/G5 kairos-shared@nautilus",
    "fingerprint": "SHA256:0EUiZShRR+iMwdyWbf0Qr+c5zjwJZoqgs4XaugMcASc",
    "deploy_key_id": 167380396,
    "ls_remote_head": "3f9f8cd7f0c7"
  }
}
```

## 未闭环项（派单侧需处理）

- **Gmail 别名** `chunxiaoxx+kairos@gmail.com`：本框 `~/.nautilus-v5/gmail_token.json` refresh → `HTTP 400 invalid_grant`；该 token scope 仅 `gmail.compose`/`gmail.send`，无 `gmail.read`/`gmail.settings.basic`，**无法自证收信与别名 sendAs**。
- **别名表** 声称在 v5 仓 `agent_mail.py`：`find /home/ubuntu/nautilus-v5 /home/ubuntu/.nautilus-v5 -name 'agent_mail*'` → 0 命中；`nautilus_v5/channels/adapters/email.py` + `nautilus_v5/integrations/gmail_oauth.py` 内亦无 agent→别名映射。
- **死线** 2026-10-05 已于 verified_utc 前过期 18 天，需给真日期或作废。

证据可复现：`GET /repos/Nautilus-agent/<repo>/keys`；`ssh -T -i <私钥> -o IdentitiesOnly=yes git@github.com` → `Hi Nautilus-agent/kairos!`
