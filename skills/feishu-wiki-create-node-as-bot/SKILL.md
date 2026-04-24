---
name: feishu-wiki-create-node-as-bot
description: |
  以机器人身份创建飞书知识库节点（文档）。
  使用应用身份（tenant_access_token）调用 Wiki API，创建者显示为机器人。
---

# 以机器人身份创建飞书知识库节点

本技能用于以机器人（应用）身份在飞书知识库中创建文档节点，创建者显示为机器人而非用户。

## 使用场景

- 需要以机器人身份创建知识库文档（创建者显示为机器人）
- 自动化生成知识库内容
- 批量创建知识库文档

## 前置条件

1. **机器人已添加为知识库管理员**
   
   使用 `feishu-wiki-add-bot-admin` skill 先将机器人添加为知识库管理员。
   
   **自动获取机器人 OpenID：**
   ```bash
   # 获取当前应用的机器人 OpenID
   BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
   echo "机器人 OpenID: ${BOT_OPENID}"
   ```
   
   **添加机器人到知识库：**
   ```bash
   # 先获取 space_id（如果不知道）
   SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="你的知识库名称") | .space_id')
   
   # 添加机器人为管理员
   lark-cli wiki members create --as user \
     --params '{"space_id":"'${SPACE_ID}'"}' \
     --data '{"member_id":"'${BOT_OPENID}'","member_type":"openid","member_role":"admin"}'
   ```

2. **获取 tenant_access_token**
   
   使用应用身份调用 API 需要 tenant_access_token，lark-cli 会自动处理。

## 使用方法

### 方式 1：使用 lark-cli（推荐）

```bash
# 1. 自动获取 space_id（如果不知道）
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
echo "知识库 Space ID: ${SPACE_ID}"

# 2. 创建知识库节点
lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "文档标题" \
  --obj-type "docx"
```

**完整示例（带变量获取）：**
```bash
# 自动获取知识库 ID
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')

# 在知识库根目录创建文档
lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "AI 日报 - $(date +%Y%m%d)" \
  --obj-type "docx"

# 提取 obj_token 用于后续内容更新
OBJ_TOKEN=$(lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "测试文档" \
  --obj-type "docx" | jq -r '.data.obj_token')
```

### 方式 2：直接使用 API（适合脚本）

```bash
# 1. 获取应用凭证（从 lark-cli 配置读取）
APP_ID=$(cat ~/.lark-cli/config.json | jq -r '.apps[0].appId')
APP_SECRET=$(security find-generic-password -s "appsecret:${APP_ID}" -w 2>/dev/null || echo "")

# 2. 获取 tenant_access_token
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"${APP_ID}\",\"app_secret\":\"${APP_SECRET}\"}")

TENANT_TOKEN=$(echo "${TOKEN_RESPONSE}" | jq -r '.tenant_access_token')

# 3. 获取 space_id（自动）
SPACE_ID=$(curl -s -X GET "https://open.feishu.cn/open-apis/wiki/v2/spaces" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" | jq -r '.data.spaces[] | select(.name=="AI 行研") | .space_id')

# 4. 创建知识库节点
curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/${SPACE_ID}/nodes" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_token": "",
    "title": "文档标题",
    "obj_type": "docx",
    "node_type": "origin"
  }'
```

### 方式 3：在 OpenClaw 中调用

在 OpenClaw 会话中描述需求，AI 会自动获取必要参数并执行：
```
以机器人身份在"AI 行研"知识库中创建文档"AI 日报 - 20260424"
```

AI 会自动：
1. 调用 `lark-cli wiki spaces list` 获取 space_id
2. 调用 `lark-cli api GET /open-apis/bot/v3/info` 验证机器人身份
3. 使用 `lark-cli wiki +node-create --as bot` 创建文档

## 参数说明

| 参数 | 说明 | 必填 | 默认值 | 获取方式 |
|------|------|------|--------|----------|
| `space_id` | 知识库空间 ID | 是 | - | `lark-cli wiki spaces list` |
| `title` | 文档标题 | 是 | - | 自定义 |
| `parent_token` | 父节点 token（空表示根目录） | 否 | `""` | `lark-cli wiki nodes list` |
| `obj_type` | 对象类型 | 否 | `docx` | `docx`, `sheet`, `bitable`, `mindnote`, `slides` |
| `node_type` | 节点类型 | 否 | `origin` | `origin`（原创）, `shortcut`（快捷方式） |

**注意：** 不要硬编码示例中的值（如 `7631092179137579973`），应使用命令动态获取。

## 完整流程

### 步骤 1：获取必要参数（全部自动获取）

```bash
# 获取机器人 OpenID
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
echo "🤖 机器人 OpenID: ${BOT_OPENID}"

# 获取知识库 Space ID（按名称匹配）
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
echo "📚 知识库 Space ID: ${SPACE_ID}"

# 检查机器人权限
lark-cli wiki members list --params '{"space_id":"'${SPACE_ID}'"}' | jq '.data.members[] | select(.member_id=="'${BOT_OPENID}'")'
```

### 步骤 2：创建知识库节点

```bash
# 创建文档（机器人身份）
RESULT=$(lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "文档标题" \
  --obj-type "docx" 2>&1)

# 提取 obj_token（用于内容更新）
OBJ_TOKEN=$(echo "${RESULT}" | jq -r '.data.obj_token')
echo "📄 文档 obj_token: ${OBJ_TOKEN}"
```

### 步骤 3：填充文档内容

**方式 A：使用 lark-cli（需要 docx 权限）**
```bash
lark-cli docx update --as bot \
  --obj-token "${OBJ_TOKEN}" \
  --content "# 标题\n\n正文内容..."
```

**方式 B：使用 feishu_update_doc 工具（推荐）**
```bash
# 在 OpenClaw 中调用
feishu_update_doc \
  --doc_id "${OBJ_TOKEN}" \
  --mode overwrite \
  --markdown "# 标题\n\n正文内容..."
```

## 获取必要参数（全部自动化）

### 获取 space_id

**方法 A：使用 lark-cli（推荐）**
```bash
# 列出所有知识库
lark-cli wiki spaces list

# 按名称过滤（推荐）
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
echo "${SPACE_ID}"
```

**方法 B：从 URL 获取**
- 进入知识库 → 设置页面
- URL 格式：`https://xxx.feishu.cn/wiki/settings/<space_id>`

### 获取 parent_token（可选，根目录创建不需要）

```bash
# 列出知识库所有节点
lark-cli wiki nodes list --params '{"space_id":"'${SPACE_ID}'"}'

# 按标题查找父节点
PARENT_TOKEN=$(lark-cli wiki nodes list --params '{"space_id":"'${SPACE_ID}'"}' | \
  jq -r '.nodes[] | select(.title=="父文档标题") | .node_token')
```

### 获取机器人 OpenID

```bash
# 使用 lark-cli 获取当前应用的机器人信息
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
echo "机器人 OpenID: ${BOT_OPENID}"
```

### 获取应用凭证（lark-cli 自动管理）

```bash
# 查看当前配置
lark-cli config show

# app_id 在配置文件中
APP_ID=$(cat ~/.lark-cli/config.json | jq -r '.apps[0].appId')

# app_secret 在钥匙串中（macOS）
APP_SECRET=$(security find-generic-password -s "appsecret:${APP_ID}" -w)
```

## 响应示例

### 成功响应（lark-cli）
```json
{
  "ok": true,
  "identity": "bot",
  "data": {
    "node_token": "LkwkwruRPiN2T5koiXKcLEPknhg",
    "obj_token": "L7jfdfkWEoPUjjxPARecZrLmnNg",
    "title": "文档标题",
    "obj_type": "docx",
    "space_id": "7630717889183534041"
  }
}
```

**提取关键字段：**
```bash
# 提取 obj_token（用于内容更新）
OBJ_TOKEN=$(echo "${RESULT}" | jq -r '.data.obj_token')

# 提取 node_token（用于节点管理）
NODE_TOKEN=$(echo "${RESULT}" | jq -r '.data.node_token')
```

### 错误响应
```json
{
  "ok": false,
  "identity": "bot",
  "error": {
    "type": "api_error",
    "code": 131006,
    "message": "API call failed: [131006] permission denied: wiki space permission denied"
  }
}
```

## 常见问题

### Q: 提示 "permission denied"
**A:** 机器人未被添加为知识库管理员。

**解决步骤：**
```bash
# 1. 获取机器人 OpenID
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')

# 2. 获取 space_id
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')

# 3. 添加机器人（用用户身份）
lark-cli wiki members create --as user \
  --params '{"space_id":"'${SPACE_ID}'"}' \
  --data '{"member_id":"'${BOT_OPENID}'","member_type":"openid","member_role":"admin"}'
```

### Q: 创建者仍显示为用户
**A:** 确保使用 `--as bot` 参数，lark-cli 会自动使用 `tenant_access_token`。

```bash
# ✅ 正确：使用 --as bot
lark-cli wiki +node-create --as bot --space-id "xxx" --title "xxx"

# ❌ 错误：使用 --as user（创建者会显示为用户）
lark-cli wiki +node-create --as user --space-id "xxx" --title "xxx"
```

### Q: 无法提取 obj_token
**A:** 使用 `jq` 正确解析 JSON 输出。

```bash
# 保存完整输出
RESULT=$(lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "文档标题" \
  --obj-type "docx" 2>&1)

# 提取 obj_token
OBJ_TOKEN=$(echo "${RESULT}" | jq -r '.data.obj_token')

# 调试：查看完整输出
echo "${RESULT}" | jq .
```

### Q: 个人知识库无法创建
**A:** 飞书个人知识库可能限制应用访问，建议使用团队知识库。

### Q: lark-cli 未配置或授权
**A:** 先完成 lark-cli 配置和授权。

```bash
# 配置应用
lark-cli config init --new

# 用户授权
lark-cli auth login --recommend

# 检查状态
lark-cli auth list
lark-cli config show
```

## 相关 API 文档

- [创建知识空间节点](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/create)
- [获取知识空间节点列表](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/list)
- [Docx API 文档](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/docx-v1/document/create)

## 注意事项

1. **权限要求**：机器人必须是知识库管理员（使用 `feishu-wiki-add-bot-admin` skill 添加）
2. **身份类型**：必须使用 `--as bot` 参数，lark-cli 会自动使用应用身份
3. **对象类型**：`obj_type` 可选 `docx`, `sheet`, `bitable`, `mindnote`, `slides`
4. **节点类型**：`node_type` 可选 `origin`（原创）, `shortcut`（快捷方式）
5. **内容填充**：创建节点后需单独调用 Docx API 或使用 `feishu_update_doc` 工具
6. **参数获取**：所有参数（space_id、bot_openid 等）应动态获取，不要硬编码

## 完整脚本示例

```bash
#!/bin/bash
# AI 日报自动生成脚本
set -e

# 配置
SPACE_NAME="AI 行研"
DATE=$(date +%Y%m%d)
TITLE="AI 日报 - ${DATE}"

# 1. 获取 space_id（自动）
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="'${SPACE_NAME}'") | .space_id')
if [ -z "${SPACE_ID}" ]; then
  echo "❌ 未找到知识库：${SPACE_NAME}"
  exit 1
fi
echo "📚 知识库 Space ID: ${SPACE_ID}"

# 2. 获取机器人 OpenID（自动）
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
echo "🤖 机器人 OpenID: ${BOT_OPENID}"

# 3. 创建文档节点
RESULT=$(lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "${TITLE}" \
  --obj-type "docx" 2>&1)

# 4. 提取 obj_token
OBJ_TOKEN=$(echo "${RESULT}" | jq -r '.data.obj_token')
if [ -z "${OBJ_TOKEN}" ]; then
  echo "❌ 创建失败"
  echo "${RESULT}"
  exit 1
fi
echo "✅ 文档创建成功：${OBJ_TOKEN}"
echo "🔗 文档链接：https://www.feishu.cn/wiki/${OBJ_TOKEN}"

# 5. 更新文档内容（使用 feishu_update_doc 工具）
# 在 OpenClaw 中调用：
# feishu_update_doc --doc_id "${OBJ_TOKEN}" --mode overwrite --markdown "# ${TITLE}\n\n内容..."
```

---

*最后更新：2026-04-24*
