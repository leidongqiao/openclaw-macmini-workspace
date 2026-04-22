# feishu-wiki-create-node-as-bot

以机器人身份创建飞书知识库节点的 Skill。

## 功能

- 以机器人（应用）身份创建知识库文档节点
- 创建者显示为机器人而非用户
- 支持创建到根目录或指定父节点下
- 可选填充文档内容

## 安装

本 Skill 已内置于 OpenClaw 工作区，无需额外安装。

**依赖：**
- `lark-cli`（如未安装会自动安装）
- 机器人已添加为知识库管理员

## 使用方法

### 方式 1：使用脚本（推荐）

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/feishu-wiki-create-node-as-bot

# 运行脚本
./scripts/create-wiki-node.sh <space_id> <title> [parent_token] [content]
```

**示例：**
```bash
# 在知识库根目录创建文档
./scripts/create-wiki-node.sh 7631092179137579973 "西湖印象"

# 在指定父节点下创建子文档
./scripts/create-wiki-node.sh 7631092179137579973 "西湖历史" LjMywprkiiKLAxkCtfvcGXoynXe

# 创建并填充内容（Markdown 格式）
./scripts/create-wiki-node.sh 7631092179137579973 "西湖印象" "" "# 西湖印象\n\n## 引言\n\n欲把西湖比西子..."
```

### 方式 2：使用 lark-cli

```bash
# 创建节点
lark-cli wiki +node-create \
  --params '{"space_id":"7631092179137579973","title":"西湖印象","obj_type":"docx"}'
```

### 方式 3：直接使用 API

```bash
# 1. 获取 tenant_access_token
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a96ac00a307bdbb5",
    "app_secret": "kNnMvrpGiTijnLLGv53szfWD2lZTTwVM"
  }'

# 2. 创建知识库节点
curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/7631092179137579973/nodes" \
  -H "Authorization: Bearer <tenant_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_token": "",
    "title": "西湖印象",
    "obj_type": "docx",
    "node_type": "origin"
  }'
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
| `content` | 文档内容（Markdown） | 否 | - | `"# 标题\n\n正文..."` |

## 前置准备

### 1. 添加机器人到知识库管理员

使用 `feishu-wiki-add-bot-admin` skill：

```bash
lark-cli wiki members create --as user \
  --params '{"space_id":"<space_id>"}' \
  --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
```

### 2. 获取必要参数

**space_id**：从知识库设置页面 URL 获取
- URL 格式：`https://xxx.feishu.cn/wiki/settings/<space_id>`

**parent_token**（可选）：从父文档 URL 获取
- URL 格式：`https://xxx.feishu.cn/wiki/<node_token>`

**bot_openid**：从飞书开放平台或 bot/info API 获取

## 输出示例

```
🦞 以机器人身份创建飞书知识库节点

检查 lark-cli 配置...
✓ 应用 ID: cli_a96ac00a307bdbb5

获取 tenant_access_token...
✓ 获取 token 成功

正在创建知识库节点...
  知识库 space_id: 7631092179137579973
  文档标题：西湖印象
  父节点 token: 根目录

✓ 创建成功！

节点信息：
  node_token: LkwkwruRPiN2T5koiXKcLEPknhg
  obj_token: L7jfdfkWEoPUjjxPARecZrLmnNg
  创建者：ou_89e1f41a6cb21a4a8203a50dcff87515

文档链接：https://www.feishu.cn/wiki/LkwkwruRPiN2T5koiXKcLEPknhg

完成！
```

## 后续操作

### 编辑文档内容

使用 `feishu_update_doc` 工具或 Docx API：

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/<obj_token>/raw_content" \
  -H "Authorization: Bearer <tenant_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "# 标题\n\n正文内容..."}'
```

### 创建子节点

```bash
./scripts/create-wiki-node.sh <space_id> "子文档标题" <parent_node_token>
```

### 查看节点列表

```bash
lark-cli wiki nodes list --params '{"space_id":"<space_id>"}'
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

### Q: 脚本提示 "appSecret not found"
**A:** 运行 `lark-cli config init` 完成配置。

### Q: 个人知识库无法创建
**A:** 飞书个人知识库可能限制应用访问，建议使用团队知识库。

## 文件结构

```
feishu-wiki-create-node-as-bot/
├── SKILL.md                          # 技能说明文档
├── README.md                         # 本文件
└── scripts/
    └── create-wiki-node.sh           # 自动化脚本
```

## 相关 Skill

- **feishu-wiki-add-bot-admin**: 将机器人添加为知识库管理员
- **feishu-create-doc**: 以用户身份创建飞书文档
- **feishu-update-doc**: 更新飞书文档内容

## 相关文档

- [飞书知识库 API](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-overview)
- [创建知识空间节点](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-node/create)
- [lark-cli 文档](https://github.com/larksuite/cli)

## 更新日志

- 2026-04-22: 初始版本，支持以机器人身份创建知识库节点
