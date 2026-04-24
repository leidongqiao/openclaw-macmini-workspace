# feishu-wiki-add-bot-admin

将机器人添加为飞书团队知识库管理员的 Skill。

## 功能

- 将机器人/应用添加为飞书知识库管理员
- 支持添加为管理员（admin）或普通成员（member）
- 自动验证添加结果
- **这是 `feishu-wiki-create-node-as-bot` 的前置技能**

## 快速开始

```bash
# 1. 确保 lark-cli 已安装和授权
lark-cli auth login --recommend

# 2. 添加机器人到知识库
lark-cli wiki members create --as user \
  --params '{"space_id":""}' \
  --data '{"member_id":"","member_type":"openid","member_role":"admin"}'

# 3. 验证结果
lark-cli wiki members list --params '{"space_id":""}'
```

## 完整流程

### 步骤 1：安装 lark-cli（如未安装）
```bash
npm install -g @larksuite/cli
```

### 步骤 2：用户授权
```bash
lark-cli auth login --recommend
```
打开输出的链接完成 OAuth 授权。

### 步骤 3：获取必要参数

**space_id**：从知识库设置页面 URL 获取
- URL：`https://xxx.feishu.cn/wiki/settings/<space_id>`

**bot_openid**：从飞书开放平台或 bot/info API 获取

### 步骤 4：添加机器人
```bash
lark-cli wiki members create --as user \
  --params '{"space_id":"<space_id>"}' \
  --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
```

### 步骤 5：验证
```bash
lark-cli wiki members list --params '{"space_id":"<space_id>"}'
```

## 后续技能

添加成功后，可以使用 **`feishu-wiki-create-node-as-bot`** skill 以机器人身份创建文档：

```bash
~/.openclaw/workspace/skills/feishu-wiki-create-node-as-bot/scripts/create-wiki-node.sh \
  <space_id> "文档标题"
```

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| permission denied | 确保使用 `--as user`，当前用户是知识库管理员 |
| invalid member_type | `member_type` 必须为 `openid` |
| need_user_authorization | 运行 `lark-cli auth login --recommend` |
| 个人知识库无法添加 | 使用团队知识库 |

## 相关文档

- [添加知识空间成员 API](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-member/create)
- [lark-cli 文档](https://github.com/larksuite/cli)
