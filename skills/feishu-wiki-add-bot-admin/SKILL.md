---
name: feishu-wiki-add-bot-admin
description: |
  将机器人/应用添加为飞书团队知识库的管理员。
  使用 lark-cli 工具，通过用户身份调用 Wiki API 添加机器人成员。
---

# 将机器人添加为飞书知识库管理员

本技能用于将机器人（应用）添加为飞书团队知识库的管理员，使机器人能够以应用身份创建、编辑知识库文档。

## 使用场景

- 需要以机器人身份创建知识库文档（创建者显示为机器人）
- 需要机器人编辑团队知识库中的文档
- 需要自动化管理知识库内容

## 前置条件

1. **安装 lark-cli**（如未安装）：
   ```bash
   npm install -g @larksuite/cli
   ```

2. **完成 lark-cli 用户授权**：
   ```bash
   lark-cli auth login --recommend
   ```
   打开输出的链接完成 OAuth 授权

3. **获取机器人 openid**：
   ```bash
   curl -s -X GET "https://open.feishu.cn/open-apis/bot/v3/info" \
     -H "Authorization: Bearer <tenant_access_token>"
   ```
   或使用应用身份调用：
   ```bash
   lark-cli auth status --as bot
   ```

## 使用方法

### 基本用法

```bash
lark-cli wiki members create --as user \
  --params '{"space_id":"<知识库 space_id>"}' \
  --data '{"member_id":"<机器人 openid>","member_type":"openid","member_role":"admin"}'
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `space_id` | 知识库空间 ID | `7631092179137579973` |
| `member_id` | 机器人的 openid | `ou_89e1f41a6cb21a4a8203a50dcff87515` |
| `member_type` | 成员类型，固定为 `openid` | `openid` |
| `member_role` | 角色：`admin`（管理员）或 `member`（成员） | `admin` |

### 完整示例

```bash
# 1. 检查 lark-cli 配置
lark-cli config show

# 2. 检查用户登录状态
lark-cli auth list

# 3. 如未登录，先授权
lark-cli auth login --recommend

# 4. 获取机器人 openid（可选，如已知可跳过）
# 从飞书开放平台应用信息页获取，或通过 bot/info API 获取

# 5. 添加机器人到知识库
lark-cli wiki members create --as user \
  --params '{"space_id":"7631092179137579973"}' \
  --data '{"member_id":"ou_89e1f41a6cb21a4a8203a50dcff87515","member_type":"openid","member_role":"admin"}'

# 6. 验证添加结果
lark-cli wiki members list \
  --params '{"space_id":"7631092179137579973"}'
```

## 获取知识库 space_id

### 方法 1：从 URL 获取
进入知识库设置页面，URL 格式：
```
https://xxx.feishu.cn/wiki/settings/<space_id>
```

### 方法 2：使用 API 获取
```bash
lark-cli wiki spaces list
```

### 方法 3：使用 feishu_wiki_space 工具
调用 `feishu_wiki_space` 工具的 `list` action 获取知识库列表。

## 获取机器人 openid

### 方法 1：使用 bot/info API
```bash
curl -s -X GET "https://open.feishu.cn/open-apis/bot/v3/info" \
  -H "Authorization: Bearer <tenant_access_token>"
```

### 方法 2：从飞书开放平台获取
1. 打开飞书开放平台：https://open.feishu.cn/
2. 进入应用管理 → 选择应用
3. 在"机器人"功能页查看机器人信息

### 方法 3：使用 lark-cli
```bash
lark-cli config show
```

## 验证添加结果

```bash
lark-cli wiki members list \
  --params '{"space_id":"<space_id>"}'
```

成功添加后，返回结果中应包含机器人信息：
```json
{
  "code": 0,
  "data": {
    "members": [
      {
        "member_id": "ou_89e1f41a6cb21a4a8203a50dcff87515",
        "member_role": "admin",
        "member_type": "openid"
      }
    ]
  }
}
```

## 后续操作

添加成功后，可以使用应用身份（tenant_access_token）执行以下操作：

### 创建知识库文档
```bash
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

### 或使用 feishu_create_doc 工具
```json
{
  "title": "文档标题",
  "wiki_space": "<space_id>",
  "markdown": "文档内容"
}
```

## 常见问题

### Q: 提示 "permission denied"
**A:** 确保：
1. 使用 `--as user` 参数（使用用户身份）
2. 当前用户是知识库管理员
3. lark-cli 已完成用户授权

### Q: 提示 "invalid member_type"
**A:** `member_type` 必须为 `openid`，不要使用 `user` 或 `app`。

### Q: 个人知识库无法添加应用
**A:** 飞书个人知识库可能限制只能添加用户。建议创建团队知识库。

### Q: lark-cli 未找到命令
**A:** 使用完整路径 `~/.npm-global/bin/lark-cli` 或检查 npm 全局安装路径。

## 相关 API 文档

- [添加知识空间成员](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-member/create)
- [获取知识空间成员列表](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-member/list)
- [lark-cli wiki 命令](https://github.com/larksuite/cli#wiki)

## 注意事项

1. **权限要求**：执行此操作的用户必须是知识库管理员
2. **身份类型**：必须使用 `--as user` 参数，应用身份无权限添加成员
3. **成员类型**：`member_type` 固定为 `openid`
4. **角色类型**：`member_role` 可选 `admin`（管理员）或 `member`（普通成员）
5. **知识库类型**：团队知识库支持添加应用，个人知识库可能有限制
