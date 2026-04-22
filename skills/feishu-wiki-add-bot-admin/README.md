# feishu-wiki-add-bot-admin

将机器人添加为飞书团队知识库管理员的 Skill。

## 功能

- 将机器人/应用添加为飞书知识库管理员
- 支持添加为管理员（admin）或普通成员（member）
- 自动验证添加结果

## 安装

本 Skill 已内置于 OpenClaw 工作区，无需额外安装。

**依赖：**
- `lark-cli`（如未安装会自动安装）
- 飞书用户 OAuth 授权

## 使用方法

### 方式 1：使用脚本（推荐）

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/feishu-wiki-add-bot-admin

# 运行脚本
./scripts/add-bot-to-wiki.sh <space_id> <bot_openid> [role]
```

**示例：**
```bash
./scripts/add-bot-to-wiki.sh 7631092179137579973 ou_89e1f41a6cb21a4a8203a50dcff87515 admin
```

### 方式 2：直接使用 lark-cli

```bash
lark-cli wiki members create --as user \
  --params '{"space_id":"<space_id>"}' \
  --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
```

### 方式 3：在 OpenClaw 中调用

在 OpenClaw 会话中描述需求，AI 会自动执行：
```
帮我将机器人添加为知识库 7631092179137579973 的管理员
```

## 参数说明

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `space_id` | 知识库空间 ID | 是 | `7631092179137579973` |
| `bot_openid` | 机器人的 openid | 是 | `ou_89e1f41a6cb21a4a8203a50dcff87515` |
| `role` | 角色：admin/member | 否 | `admin`（默认） |

## 前置准备

### 1. 首次使用需要授权

```bash
lark-cli auth login --recommend
```

打开输出的链接完成 OAuth 授权。

### 2. 获取知识库 space_id

**方法 A：从 URL 获取**
- 进入知识库 → 设置页面
- URL 格式：`https://xxx.feishu.cn/wiki/settings/<space_id>`

**方法 B：使用 API**
```bash
lark-cli wiki spaces list
```

### 3. 获取机器人 openid

**方法 A：使用 API**
```bash
curl -s -X GET "https://open.feishu.cn/open-apis/bot/v3/info" \
  -H "Authorization: Bearer <tenant_access_token>"
```

**方法 B：从开放平台**
- 飞书开放平台 → 应用管理 → 机器人 → 机器人信息

## 验证结果

```bash
lark-cli wiki members list --params '{"space_id":"<space_id>"}'
```

## 后续操作

添加成功后，机器人可以：

1. **创建知识库文档**
   ```bash
   lark-cli wiki +node-create \
     --params '{"space_id":"<space_id>","title":"文档标题","obj_type":"docx"}'
   ```

2. **编辑文档内容**
   使用 `feishu_update_doc` 工具或 Docx API

3. **管理知识库节点**
   ```bash
   lark-cli wiki nodes --help
   ```

## 常见问题

### Q: 提示 "permission denied"
确保：
- 使用 `--as user` 参数
- 当前用户是知识库管理员
- 已完成 lark-cli 用户授权

### Q: 提示 "need_user_authorization"
运行 `lark-cli auth login --recommend` 完成授权。

### Q: 个人知识库无法添加
飞书个人知识库可能限制只能添加用户，建议创建团队知识库。

## 文件结构

```
feishu-wiki-add-bot-admin/
├── SKILL.md                          # 技能说明文档
├── README.md                         # 本文件
└── scripts/
    └── add-bot-to-wiki.sh            # 自动化脚本
```

## 相关文档

- [飞书知识库 API](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-overview)
- [lark-cli 文档](https://github.com/larksuite/cli)
- [添加知识空间成员 API](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-member/create)

## 更新日志

- 2026-04-22: 初始版本，支持添加机器人到知识库
