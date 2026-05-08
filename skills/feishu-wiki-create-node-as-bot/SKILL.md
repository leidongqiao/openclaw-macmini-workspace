---
name: feishu-wiki-create-node-as-bot
description: |
  以机器人身份创建飞书知识库节点（文档）。
  使用应用身份（tenant_access_token）调用 Wiki API，创建者显示为机器人。
---

# 以机器人身份创建飞书知识库节点

本技能用于以机器人（应用）身份在飞书知识库中创建文档节点，创建者显示为机器人而非用户。

## ⚠️ 关键：自动检测当前 bot profile

**不要假设自己是 ai_bot 或其他固定 key。** 在 openclaw.json → channels.feishu.accounts 里可能有多个 bot 账号。

**在 shell 中自动检测当前 agent 对应的 bot profile：**

```bash
# 自动推导 BOT_PROFILE（从 workspace 路径匹配 openclaw.json 中的 bot key）
WORKSPACE_NAME=$(basename "${WORKSPACE_PATH:-$(pwd)}")
AGENT_PREFIX=$(echo "$WORKSPACE_NAME" | sed -E 's/^workspace-//; s/^([A-Za-z]+).*/\1/' | tr '[:upper:]' '[:lower:]')
BOT_PROFILE=$(jq -r ".channels.feishu.accounts | to_entries[] | select(.value.appId != null) | .key" ~/.openclaw/openclaw.json 2>/dev/null | grep "^${AGENT_PREFIX}_" | head -1)
# fallback: lark-cli 默认 profile
[ -z "$BOT_PROFILE" ] && BOT_PROFILE=$(jq -r '.profile // empty' ~/.lark-cli/config.json 2>/dev/null)
echo "BOT_PROFILE=$BOT_PROFILE"
```

**所有 lark-cli 命令统一使用 `--profile "$BOT_PROFILE" --as bot`**，不要裸用 `--as bot`。

## 前置条件

1. **机器人已添加为知识库管理员**（使用 `feishu-wiki-add-bot-admin` skill）
2. **获取 tenant_access_token**（用上面检测到的 BOT_PROFILE 对应的 appId/appSecret）

## 使用方法

### 方式 1：使用 lark-cli（推荐）

```bash
export PATH="$HOME/.npm-global/bin:$PATH"

# 先自动检测 BOT_PROFILE（见上方"关键"章节）

# 自动获取 space_id
SPACE_ID=$(lark-cli wiki spaces list --profile "$BOT_PROFILE" | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')

# 创建知识库节点（机器人身份）
lark-cli wiki +node-create --profile "$BOT_PROFILE" --as bot \
  --space-id "${SPACE_ID}" \
  --title "文档标题" \
  --obj-type "docx"
```

### 方式 2：直接使用 API（适合脚本）

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
# 先自动检测 BOT_PROFILE

APP_ID=$(cat ~/.openclaw/openclaw.json | jq -r ".channels.feishu.accounts.${BOT_PROFILE}.appId")
APP_SECRET=$(cat ~/.openclaw/openclaw.json | jq -r ".channels.feishu.accounts.${BOT_PROFILE}.appSecret")

# 获取 tenant_access_token
TENANT_TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"${APP_ID}\",\"app_secret\":\"${APP_SECRET}\"}" | jq -r '.tenant_access_token')

# 获取 space_id
SPACE_ID=$(curl -s -X GET "https://open.feishu.cn/open-apis/wiki/v2/spaces" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" | jq -r '.data.spaces[] | select(.name=="AI 行研") | .space_id')

# 创建知识库节点
curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/${SPACE_ID}/nodes" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"parent_token":"","title":"文档标题","obj_type":"docx","node_type":"origin"}'
```

### 方式 3：在 OpenClaw 中调用

描述需求即可，AI 会自动检测 bot 身份并执行。

## 参数说明

| 参数 | 说明 | 必填 | 默认值 | 获取方式 |
|------|------|------|--------|----------|
| `space_id` | 知识库空间 ID | 是 | - | `lark-cli wiki spaces list` |
| `title` | 文档标题 | 是 | - | 自定义 |
| `parent_token` | 父节点 token（空=根目录） | 否 | `""` | `lark-cli wiki nodes list` |
| `obj_type` | 对象类型 | 否 | `docx` | `docx`, `sheet`, `bitable`, `mindnote`, `slides` |
| `node_type` | 节点类型 | 否 | `origin` | `origin`（原创）, `shortcut`（快捷方式） |

## 完整流程

### 步骤 1：获取必要参数

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
# 先自动检测 BOT_PROFILE

# 获取机器人 OpenID
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --profile "$BOT_PROFILE" --as bot | jq -r '.bot.open_id')

# 获取知识库 Space ID
SPACE_ID=$(lark-cli wiki spaces list --profile "$BOT_PROFILE" | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
```

### 步骤 2：创建知识库节点

```bash
RESULT=$(lark-cli wiki +node-create --profile "$BOT_PROFILE" --as bot \
  --space-id "${SPACE_ID}" \
  --title "文档标题" \
  --obj-type "docx" 2>&1)

OBJ_TOKEN=$(echo "${RESULT}" | jq -r '.data.obj_token')
```

### 步骤 3：填充文档内容

**⚠️ 不要用裸调 Docx API。** 使用 `feishu_update_doc` 工具或 `lark-cli docs +update`：

```bash
lark-cli docs +update --doc "${OBJ_TOKEN}" --profile "$BOT_PROFILE" --as bot --mode overwrite --markdown '# 标题\n\n正文...'
```

## 获取必要参数（全部自动化）

### 获取 space_id

```bash
lark-cli wiki spaces list --profile "$BOT_PROFILE" | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id'
```

### 获取 parent_token（可选）

```bash
lark-cli wiki nodes list --profile "$BOT_PROFILE" --params '{"space_id":"'${SPACE_ID}'"}' | jq -r '.nodes[] | select(.title=="父文档标题") | .node_token'
```

## 响应示例

```json
{
  "ok": true,
  "identity": "bot",
  "data": {
    "node_token": "LkwkwruRPiN2T5koiXKcLEPknhg",
    "obj_token": "L7jfdfkWEoPUjjxPARecZrLmnNg",
    "title": "文档标题"
  }
}
```

## 常见问题

### Q: 提示 "permission denied" (131006)
**A:** 机器人未添加为知识库管理员。先用 `feishu-wiki-add-bot-admin` skill 添加。

### Q: 创建者仍显示为用户
**A:** 确保使用了 `--profile "$BOT_PROFILE" --as bot`，不要裸用 `--as bot`（那是 lark-cli 默认配置的 ai_bot，不是你自己的 bot）。

### Q: 个人知识库无法创建
**A:** 飞书个人知识库可能限制应用访问，建议使用团队知识库。

### Q: lark-cli 未配置或授权
**A:** 先完成 lark-cli 配置和授权。

```bash
lark-cli auth login --recommend
lark-cli auth list
```

## 注意事项

1. **权限要求**：机器人必须是知识库管理员
2. **身份类型**：必须使用 `--profile "$BOT_PROFILE" --as bot` 参数
3. **对象类型**：`obj_type` 可选 `docx`, `sheet`, `bitable`, `mindnote`, `slides`
4. **参数获取**：所有参数应动态获取，不要硬编码
5. **内容填充**：使用 `lark-cli docs +update` 或 `feishu_update_doc` 工具，不要裸调 Docx API
6. **lark-cli 路径**：`~/.npm-global/bin/lark-cli`
