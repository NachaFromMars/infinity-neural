# Infinity Memory V1.0 — Hướng dẫn cài đặt

## Bước 1: Install Infinity Neural engine

```bash
pip install dist/infinity_neural-1.0.0-py3-none-any.whl
```

Verify:
```bash
infinity-neural --version
# Output: infinity-neural 1.0.0
```

## Bước 2: Khởi tạo brain

```bash
# Tạo brain mới cho OpenClaw
infinity-neural init --name openclaw-brain

# Database sẽ ở: ~/.neuralmemory/brains/openclaw-brain.db
```

## Bước 3: Thêm MCP config vào OpenClaw

### Cách A: Tự động (khuyên dùng)
```bash
python scripts/verify_install.py --setup
```

### Cách B: Thủ công
Mở OpenClaw config (openclaw config edit) và thêm vào phần `mcp`:

```yaml
mcp:
  servers:
    infinity-neural:
      command: nmem-mcp
      env:
        NEURALMEMORY_BRAIN: openclaw-brain
```

Hoặc dùng JSON config:
```json
{
  "mcp": {
    "servers": {
      "infinity-neural": {
        "command": "nmem-mcp",
        "env": {
          "NEURALMEMORY_BRAIN": "openclaw-brain"
        }
      }
    }
  }
}
```

### Restart OpenClaw
```bash
openclaw gateway restart
```

## Bước 4: Memory Bridge (optional)

Bridge tự đồng bộ MEMORY.md ↔ Neural Graph:

```bash
# Chạy 1 lần (import MEMORY.md hiện tại vào graph)
python scripts/memory_bridge.py --import-once

# Chạy liên tục (watch mode)
python scripts/memory_bridge.py --watch

# Hoặc đặt cron job
python scripts/memory_bridge.py --sync
```

## Bước 5: Verify

```bash
python scripts/verify_install.py

# Expected output:
# ✅ infinity-neural installed (v1.0.0)
# ✅ nmem-mcp CLI available
# ✅ Brain 'openclaw-brain' exists
# ✅ MCP server starts successfully
# ✅ nmem_remember works
# ✅ nmem_recall works
# ✅ ETERNAL neurons supported
# ✅ Vietnamese NLP loaded (200+ compounds)
# ✅ All checks passed!
```

## Gỡ cài đặt

```bash
pip uninstall infinity-neural
# Xóa brain data (optional):
# rm -rf ~/.neuralmemory/brains/openclaw-brain.db
# Xóa MCP config từ OpenClaw config
```
