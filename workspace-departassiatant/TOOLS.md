# TOOLS.md - Local Notes

## lark-cli（飞书多维表格）

**路径**: `~/.npm-global/bin/lark-cli`

**核心原则：群里涉及读取多维表格的操作，优先用 `lark-cli base ... --as bot`，不走用户 OAuth。**

depart_bot 在有权限的多维表格上可以直接用应用身份读取，无需群里成员逐个授权。

### 常用命令模板

```bash
# 列出数据表
~/.npm-global/bin/lark-cli base +table-list --as bot --base-token <token>

# 列出字段结构
~/.npm-global/bin/lark-cli base +field-list --as bot --base-token <token> --table-id <table-id>

# 搜索记录
~/.npm-global/bin/lark-cli base +record-search --as bot --base-token <token> --table-id <table-id> --query <关键词>

# 列出记录明细
~/.npm-global/bin/lark-cli base +record-list --as bot --base-token <token> --table-id <table-id> --limit 50

# 按 ID 获取记录
~/.npm-global/bin/lark-cli base +record-get --as bot --base-token <token> --table-id <table-id> --record-id <record-id>
```

### 身份策略
- **`--as bot`（默认）**：depart_bot 有权限的多维表格，一律用 bot 身份，不依赖用户授权
- **`--as user`**：只有 bot 没权限、但当前用户有权限的表格，才降级用 user 身份
- **token 提取**：URL 里 `/base/{token}` 就是 base-token；`/wiki/{token}` 需先 `lark-cli wiki +node-get` 解析出 `data.obj_token`

---

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)
