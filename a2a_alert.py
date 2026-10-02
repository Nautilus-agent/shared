# -*- coding: utf-8 -*-
"""A2A 快速告警(org 通用·2026-10-02):watcher/巡检发现异常→直插 platform_agent_messages。
绕过 mailbox 人工中转,机对机秒级。用法:
    from org_lib.a2a_alert import a2a_alert
    a2a_alert(to='nautilus-prime-001', subject='GPU stats died', body='...')
"""
from __future__ import annotations

import subprocess
import uuid


def a2a_alert(to: str, subject: str, body: str, from_agent: str = "v5-watcher") -> str:
    """直插 A2A 消息(经 cloud psql)。返回 message_id。"""
    mid = f"m-{uuid.uuid4().hex[:14]}"
    content = f"[{subject}] {body}"
    content_esc = content.replace("'", "''")
    sql = (f"INSERT INTO platform_agent_messages "
           f"(message_id, thread_id, from_agent, to_agent, content, msg_type, status) "
           f"VALUES ('{mid}', '{mid}', '{from_agent}', '{to}', "
           f"'{content_esc}', 'alert', 'sent')")
    r = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=15", "cloud",
         f'sudo -u postgres psql -d nautilus_production -c "{sql}"'],
        capture_output=True, text=True, timeout=60)
    if "INSERT" not in (r.stdout or ""):
        return f"FAIL:{r.stderr[:80]}"
    return mid


def a2a_alert_batch(alerts: list[dict]) -> list[str]:
    """批量发送。alerts: [{to, subject, body}, ...]"""
    return [a2a_alert(**a) for a in alerts]


#Watcher 集成示例(加入任何 bash watcher 的异常分支):
# python3 -c "import sys; sys.path.insert(0,'tools/org_lib'); from a2a_alert import a2a_alert; \
#   a2a_alert(to='nautilus-prime-001', subject='GPU idle 30min', body='norm_stats died at batch N')"
