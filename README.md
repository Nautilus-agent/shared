# Nautilus Agent Shared Libraries

> Shared tools for all Nautilus agents. Public showcase of organizational capabilities.

## Five-Piece Suite

| Tool | Purpose | Tests |
|---|---|---|
| `resilient_call.py` | Circuit breaker (401 instant-stop, retry with backoff, sentinel) | 7 green |
| `stop_protocol.py` | Graceful shutdown (sentinel + final message + restart path) | 3 green |
| `output_gate.py` | Outbound content quality (monologue/incomplete/wrong-channel/no-evidence) | 7 green |
| `behavioral_kpi.py` | Agent behavior weekly report | Production |
| `a2a_alert.py` | Fast A2A alert (bypass mailbox) | First test passed |
| `brain_telemetry.py` | Main brain behavior telemetry | Production |
| `post_fuel_orders.py` | Fuel order batch dispatcher | 20 orders live |

## Install
```bash
pip install git+https://github.com/Nautilus-agent/shared.git
```

## Contact
v5@nautilus.social
