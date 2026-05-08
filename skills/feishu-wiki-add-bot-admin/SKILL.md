---
name: feishu-wiki-add-bot-admin
description: |
  将机器人添加为飞书团队知识库的管理员。
  使用 lark-cli 工具,通过用户身份调用 Wiki API 添加机器人成员。
  这是使用 feishu-wiki-create-node-as-bot 的前置步骤。
---

# 将机器人添加为飞书知识库管理员

本技能用于将机器人(应用)添加为飞书团队知识库的管理员,使机器人能够以应用身份创建、编辑知识库文档。

## ⚠️ 关键：自动检测当前 bot profile

**不要假设自己是 ai_bot 或其他固定 key。**

```bash
# 自动推导 BOT_PROFILE（从 workspace 路径匹配 openclaw.json 中的 bot key）
WORKSPACE_NAME=$(basename "${WORKSPACE_PATH:-$(pwd)}")
AGENT_PREFIX=$(echo "$WORKSPACE_NAME" | sed -E 's/^workspace-//; s/^([A-Za-z]+).*/\1/' | tr '[:upper:]' '[:lower:]')
BOT_PROFILE=$(jq -r ".channels.feishu.accounts | to_entries[] | select(.value.appId != null) | .key" ~/.openclaw/openclaw.json 2>/dev/null | grep "^${AGENT_PREFIX}_" | head -1)
# fallback: lark-cli 默认 profile
[ -z "$BOT_PROFILE" ] && BOT_PROFILE=$(jq -r '.profile // empty' ~/.lark-cli/config.json 2>/dev/null)
```

**获取自己的 bot OpenID（必须用检测到的 profile）：**
```bash
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --profile "$BOT_PROFILE" --as bot | jq -r '.bot.open_id')
```

## 前置条件

1. **安装 lark-cli**
2. **完成 lark-cli 用户授权**: `lark-cli auth login --recommend`

## 使用方法

### 方式 1: 完整脚本(推荐,所有参数自动获取)

```bash
#!/bin/bash
set -e
export PATH="$HOME/.npm-global/bin:$PATH"

# 1. 自动检测 BOT_PROFILE（见上方"关键"章节）

# 2. 获取自己的 bot OpenID
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --profile "$BOT_PROFILE" --as bot | jq -r '.bot.open_id')
echo "✅ 机器人 OpenID: ${BOT_OPENID}"

# 3. 自动获取知识库 Space ID
SPACE_NAME="半导体行研"  # ← 改为你的知识库名称
SPACE_ID=$(lark-cli wiki spaces list --profile "$BOT_PROFILE" | jq -r '.spaces[] | select(.name=="'${SPACE_NAME}'") | .space_id')
echo "✅ 知识库 Space ID: ${SPACE_ID}"

# 4. 添加机器人为管理员（使用用户身份）
RESULT=$(lark-cli wiki members create --as user \
  --params '{"space_id":"'${SPACE_ID}'"}' \
  --data '{"member_id":"'${BOT_OPENID}'","member_type":"openid","member_role":"admin"}' 2>&1)

if echo "${RESULT}" | grep -q '"code": 0'; then
  echo "✅ 添加成功！"
else
  echo "❌ 添加失败: ${RESULT}"
  exit 1
fi
```

### 方式 2: 单行命令

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
# 先自动检测 BOT_PROFILE

lark-cli wiki members create --as user \
  --params '{"space_id":"'$(lark-cli wiki spaces list --profile "$BOT_PROFILE" | jq -r '.spaces[] | select(.name=="知识库名称") | .space_id')'"}' \
  --data '{"member_id":"'$(lark-cli api GET /open-apis/bot/v3/info --profile "$BOT_PROFILE" --as bot | jq -r '.bot.open_id')'","member_type":"openid","member_role":"admin"}'
```

### 方式 3: 在 OpenClaw 中调用

描述需求即可，AI 会自动检测 bot 身份并执行。

## 参数说明

| 参数 | 说明 | 必填 | 默认值 | 获取方式 |
|------|------|------|--------|----------|
| `space_id` | 知识库空间 ID | 是 | - | `lark-cli wiki spaces list` |
| `member_id` | 机器人的 OpenID | 是 | - | `lark-cli api GET /open-apis/bot/v3/info --profile "$BOT_PROFILE" --as bot` |
| `member_type` | 成员类型 | 是 | `openid` | 固定值 |
| `member_role` | 角色 | 是 | `admin` | `admin` 或 `member` |

## 验证添加结果

```bash
SPACE_ID=$(lark-cli wiki spaces list --profile "$BOT_PROFILE" | jq -r '.spaces[] | select(.name=="知识库名称") | .space_id')
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --profile "$BOT_PROFILE" --as bot | jq -r '.bot.open_id')
lark-cli wiki members list --profile "$BOT_PROFILE" --params '{"space_id":"'${SPACE_ID}'"}' | \
  jq '.data.members[] | select(.member_id=="'${BOT_OPENID}'")'
```

## 常见问题

### Q: 提示 "permission denied"
**A:** 确保使用 `--as user` 参数，且当前用户是知识库管理员。

### Q: 提示 "invalid member_type"
**A:** `member_type` 必须为 `openid`。

### Q: 提示 "need_user_authorization"
**A:** 运行 `lark-cli auth login --recommend` 完成授权。

### Q: 无法获取机器人 OpenID
**A:** 确保使用了 `--profile "$BOT_PROFILE" --as bot`，不要裸用 `--as bot`（那是 lark-cli 默认配置的 ai_bot）。

## 注意事项

1. **权限要求**：执行此操作的用户必须是知识库管理员
2. **身份类型**：必须使用 `--as user` 参数（应用身份无权限添加成员）
3. **成员类型**：`member_type` 固定为 `openid`
4. **角色类型**：`member_role` 可选 `admin` 或 `member`
5. **参数获取**：所有参数应动态获取，不要硬编码
