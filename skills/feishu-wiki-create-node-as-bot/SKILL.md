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
   
   使用 `feishu-wiki-add-bot-admin` skill 先将机器人添加为知识库管理员：
   ```bash
   lark-cli wiki members create --as user \
     --params '{"space_id":"<space_id>"}' \
     --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
   ```

2. **获取 tenant_access_token**
   
   使用应用身份调用 API 需要 tenant_access_token。

## 使用方法

### 方式 1：使用脚本（推荐）

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/feishu-wiki-create-node-as-bot

# 运行脚本
./scripts/create-wiki-node.sh <space_id> <title> [parent_token]
```

**示例：**
```bash
# 在知识库根目录创建文档
./scripts/create-wiki-node.sh 7631092179137579973 "西湖印象"

# 在指定父节点下创建子文档
./scripts/create-wiki-node.sh 7631092179137579973 "西湖历史" LjMywprkiiKLAxkCtfvcGXoynXe
```

### 方式 2：直接使用 API

```bash
# 1. 获取 tenant_access_token
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_xxxxxxxxxxxxx",
    "app_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  }'

# 2. 创建知识库节点
curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/<space_id>/nodes" \
  -H "Authorization: Bearer <tenant_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_token": "",
    "title": "文档标题",
    "obj_type": "docx",
    "node_type": "origin"
  }'
```

### 方式 3：使用 lark-cli

```bash
lark-cli wiki +node-create \
  --params '{"space_id":"<space_id>","title":"文档标题","obj_type":"docx"}'
```

### 方式 4：在 OpenClaw 中调用

在 OpenClaw 会话中描述需求，AI 会自动执行：
```
以机器人身份在知识库 7631092179137579973 中创建文档"西湖印象"
```

## 参数说明

| 参数 | 说明 | 必填 | 默认值 | 示例 |
|------|------|------|--------|------|
| `space_id` | 知识库空间 ID | 是 | - | `7631092179137579973` |
| `title` | 文档标题 | 是 | - | `西湖印象` |
| `parent_token` | 父节点 token（空表示根目录） | 否 | `""` | `LjMywprkiiKLAxkCtfvcGXoynXe` |
| `obj_type` | 对象类型 | 否 | `docx` | `docx`, `sheet`, `bitable` |
| `node_type` | 节点类型 | 否 | `origin` | `origin`, `shortcut` |

## 完整流程

### 步骤 1：检查机器人权限

```bash
lark-cli wiki members list --params '{"space_id":"<space_id>"}'
```

确认机器人（openid）在成员列表中，且角色为 `admin`。

### 步骤 2：创建知识库节点

```bash
./scripts/create-wiki-node.sh <space_id> "文档标题"
```

### 步骤 3：填充文档内容

创建节点后，使用 Docx API 填充内容：

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/<obj_token>/raw_content" \
  -H "Authorization: Bearer <tenant_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# 标题\n\n正文内容..."
  }'
```

或使用 `feishu_update_doc` 工具。

## 获取必要参数

### 获取 space_id

**方法 A：从 URL 获取**
- 进入知识库 → 设置页面
- URL 格式：`https://xxx.feishu.cn/wiki/settings/<space_id>`

**方法 B：使用 API**
```bash
lark-cli wiki spaces list
```

### 获取 parent_token

**方法 A：从知识库页面获取**
- 进入父文档，URL 中包含 node_token

**方法 B：使用 API**
```bash
lark-cli wiki nodes list --params '{"space_id":"<space_id>"}'
```

### 获取应用凭证

从飞书开放平台获取：
- 应用 ID（app_id）
- 应用密钥（app_secret）

## 响应示例

### 成功响应
```json
{
  "code": 0,
  "data": {
    "node": {
      "node_token": "LkwkwruRPiN2T5koiXKcLEPknhg",
      "obj_token": "L7jfdfkWEoPUjjxPARecZrLmnNg",
      "title": "西湖印象",
      "obj_type": "docx",
      "creator": "ou_89e1f41a6cb21a4a8203a50dcff87515",
      "owner": "ou_89e1f41a6cb21a4a8203a50dcff87515"
    }
  },
  "msg": "success"
}
```

### 错误响应
```json
{
  "code": 131006,
  "msg": "permission denied: wiki space permission denied"
}
```

## 常见问题

### Q: 提示 "permission denied"
**A:** 机器人未被添加为知识库管理员。先执行：
```bash
lark-cli wiki members create --as user \
  --params '{"space_id":"<space_id>"}' \
  --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
```

### Q: 创建者仍显示为用户
**A:** 确保使用 `tenant_access_token`（应用身份）而非 `user_access_token`。

### Q: 无法填充文档内容
**A:** 使用 `obj_token` 而非 `node_token` 调用 Docx API。

### Q: 个人知识库无法创建
**A:** 飞书个人知识库可能限制应用访问，建议使用团队知识库。

## 相关 API 文档

- [创建知识空间节点](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/create)
- [获取知识空间节点列表](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/list)
- [Docx API 文档](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/docx-v1/document/create)

## 注意事项

1. **权限要求**：机器人必须是知识库管理员
2. **身份类型**：必须使用应用身份（tenant_access_token）
3. **对象类型**：`obj_type` 可选 `docx`, `sheet`, `bitable`, `mindnote`, `slides`
4. **节点类型**：`node_type` 可选 `origin`（原创）, `shortcut`（快捷方式）
5. **内容填充**：创建节点后需单独调用 Docx API 填充内容
