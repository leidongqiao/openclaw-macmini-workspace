---
name: feishu-wiki-add-bot-admin
description: |
  将机器人添加为飞书团队知识库的管理员。
  使用 lark-cli 工具,通过用户身份调用 Wiki API 添加机器人成员。
  这是使用 feishu-wiki-create-node-as-bot 的前置步骤。
---

# 将机器人添加为飞书知识库管理员

本技能用于将机器人(应用)添加为飞书团队知识库的管理员,使机器人能够以应用身份创建、编辑知识库文档。

## 使用场景

- 需要以机器人身份创建知识库文档(创建者显示为机器人)
- 需要机器人编辑团队知识库中的文档
- 使用 `feishu-wiki-create-node-as-bot` skill 的前置步骤

## 前置条件

1. **安装 lark-cli**(如未安装):
   ```bash
   npm install -g @larksuite/cli
   ```

2. **完成 lark-cli 用户授权**:
   ```bash
   lark-cli auth login --recommend
   ```
   打开输出的链接完成 OAuth 授权

3. **自动获取必要参数**(全部使用命令获取,不要硬编码):
   ```bash
   # 获取机器人 OpenID(自动)
   BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
   echo "🤖 机器人 OpenID: ${BOT_OPENID}"

   # 获取知识库 Space ID(按名称匹配)
   SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
   echo "📚 知识库 Space ID: ${SPACE_ID}"
   ```

## 使用方法

### 方式 1:完整脚本(推荐,所有参数自动获取)

```bash
#!/bin/bash
set -e

echo "🔧 开始添加机器人到知识库管理员..."

# 1. 自动获取机器人 OpenID
echo "📌 获取机器人 OpenID..."
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
if [ -z "${BOT_OPENID}" ] || [ "${BOT_OPENID}" == "null" ]; then
  echo "❌ 无法获取机器人 OpenID"
  exit 1
fi
echo "✅ 机器人 OpenID: ${BOT_OPENID}"

# 2. 自动获取知识库 Space ID(按名称匹配)
echo "📌 获取知识库 Space ID..."
SPACE_NAME="AI 行研"  # 修改为你的知识库名称
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="'${SPACE_NAME}'") | .space_id')
if [ -z "${SPACE_ID}" ] || [ "${SPACE_ID}" == "null" ]; then
  echo "❌ 未找到知识库:${SPACE_NAME}"
  echo "可用知识库:"
  lark-cli wiki spaces list | jq -r '.spaces[].name'
  exit 1
fi
echo "✅ 知识库 Space ID: ${SPACE_ID}"

# 3. 添加机器人到知识库(使用用户身份)
echo "📌 添加机器人为管理员..."
RESULT=$(lark-cli wiki members create --as user \
  --params '{"space_id":"'${SPACE_ID}'"}' \
  --data '{"member_id":"'${BOT_OPENID}'","member_type":"openid","member_role":"admin"}' 2>&1)

# 4. 检查结果
if echo "${RESULT}" | grep -q '"ok": true'; then
  echo "✅ 添加成功!"
  echo "📋 详细信息:"
  echo "${RESULT}" | jq .
else
  echo "❌ 添加失败"
  echo "${RESULT}"
  exit 1
fi

# 5. 验证添加结果
echo "📌 验证添加结果..."
lark-cli wiki members list --params '{"space_id":"'${SPACE_ID}'"}' | \
  jq '.data.members[] | select(.member_id=="'${BOT_OPENID}'")'
```

### 方式 2:单行命令(适合快速执行)

```bash
# 一行命令完成(自动获取所有参数)
lark-cli wiki members create --as user \
  --params '{"space_id":"'$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')'"}' \
  --data '{"member_id":"'$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')'","member_type":"openid","member_role":"admin"}'
```

### 方式 3:在 OpenClaw 中调用

在 OpenClaw 会话中描述需求,AI 会自动获取参数并执行:
```
将机器人添加为"AI 行研"知识库的管理员
```

AI 会自动:
1. 调用 `lark-cli api GET /open-apis/bot/v3/info` 获取机器人 OpenID
2. 调用 `lark-cli wiki spaces list` 获取 Space ID
3. 使用 `lark-cli wiki members create --as user` 添加管理员

## 参数说明

| 参数 | 说明 | 必填 | 默认值 | 获取方式 |
|------|------|------|--------|----------|
| `space_id` | 知识库空间 ID | 是 | - | `lark-cli wiki spaces list` |
| `member_id` | 机器人的 OpenID | 是 | - | `lark-cli api GET /open-apis/bot/v3/info` |
| `member_type` | 成员类型 | 是 | `openid` | 固定值 |
| `member_role` | 角色 | 是 | `admin` | `admin`(管理员)或 `member`(成员) |

**注意:** 所有参数应使用命令动态获取,不要硬编码示例值。

## 获取必要参数(全部自动化)

### 获取 space_id

**方法 1:使用 lark-cli(推荐)**
```bash
# 列出所有知识库
lark-cli wiki spaces list

# 按名称过滤(推荐)
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
echo "${SPACE_ID}"
```

**方法 2:从 URL 获取**
- 进入知识库 → 设置页面
- URL 格式:`https://xxx.feishu.cn/wiki/settings/<space_id>`

### 获取机器人 OpenID

**方法 1:使用 lark-cli(推荐)**
```bash
# 获取当前应用的机器人信息
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
echo "机器人 OpenID: ${BOT_OPENID}"
```

**方法 2:从飞书开放平台获取**
1. 打开飞书开放平台:https://open.feishu.cn/
2. 进入应用管理 → 选择应用
3. 在"机器人"功能页查看机器人信息

**方法 3:使用 API**
```bash
# 需要先获取 tenant_access_token
curl -s -X GET "https://open.feishu.cn/open-apis/bot/v3/info" \
  -H "Authorization: Bearer <tenant_access_token>" | jq -r '.bot.open_id'
```

## 验证添加结果

```bash
# 1. 自动获取 space_id
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')

# 2. 获取机器人 OpenID
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')

# 3. 列出成员并过滤机器人
lark-cli wiki members list --params '{"space_id":"'${SPACE_ID}'"}' | \
  jq '.data.members[] | select(.member_id=="'${BOT_OPENID}'")'
```

成功添加后,返回结果应显示:
```json
{
  "member_id": "ou_xxxxxxxxxxxxx",
  "member_role": "admin",
  "member_type": "openid"
}
```

## 后续操作

添加成功后,可以使用 `feishu-wiki-create-node-as-bot` skill 以机器人身份创建文档:

```bash
# 自动获取 space_id
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')

# 以机器人身份创建文档
lark-cli wiki +node-create --as bot \
  --space-id "${SPACE_ID}" \
  --title "文档标题" \
  --obj-type "docx"
```

## 常见问题

### Q: 提示 "permission denied"
**A:** 确保:
1. 使用 `--as user` 参数(使用用户身份)
2. 当前用户是知识库管理员
3. lark-cli 已完成用户授权

**排查步骤:**
```bash
# 1. 检查用户登录状态
lark-cli auth list

# 2. 检查当前用户是否是知识库管理员
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="AI 行研") | .space_id')
lark-cli wiki members list --params '{"space_id":"'${SPACE_ID}'"}' | jq '.data.members[] | select(.member_role=="admin")'

# 3. 如未登录,先授权
lark-cli auth login --recommend
```

### Q: 提示 "invalid member_type"
**A:** `member_type` 必须为 `openid`,不要使用 `user` 或 `app`。

### Q: 提示 "need_user_authorization"
**A:** 运行 `lark-cli auth login --recommend` 完成授权。

### Q: 个人知识库无法添加应用
**A:** 飞书个人知识库可能限制只能添加用户。建议创建团队知识库。

### Q: 无法获取机器人 OpenID
**A:** 确保 lark-cli 已正确配置应用。

```bash
# 检查配置
lark-cli config show

# 重新配置应用
lark-cli config init --new
```

### Q: 找不到知识库 space_id
**A:** 确认知识库名称正确,或列出所有知识库查看。

```bash
# 列出所有知识库
lark-cli wiki spaces list | jq -r '.spaces[] | "\(.name): \(.space_id)"'

# 检查知识库名称是否匹配(区分大小写)
lark-cli wiki spaces list | jq -r '.spaces[].name'
```

## 相关 API 文档

- [添加知识空间成员](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-member/create)
- [获取知识空间成员列表](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-v2/space-member/list)

## 注意事项

1. **权限要求**：执行此操作的用户必须是知识库管理员
2. **身份类型**：必须使用 `--as user` 参数，应用身份无权限添加成员
3. **成员类型**：`member_type` 固定为 `openid`
4. **角色类型**：`member_role` 可选 `admin`（管理员）或 `member`（普通成员）
5. **知识库类型**：团队知识库支持添加应用，个人知识库可能有限制
6. **参数获取**：所有参数（space_id、bot_openid 等）应动态获取，不要硬编码

## 完整脚本示例

```bash
#!/bin/bash
# 将机器人添加为知识库管理员（完整自动化脚本）
set -e

SPACE_NAME="AI 行研"  # 修改为你的知识库名称

echo "🔧 开始添加机器人到知识库管理员..."

# 1. 获取机器人 OpenID
echo "📌 步骤 1/5: 获取机器人 OpenID..."
BOT_OPENID=$(lark-cli api GET /open-apis/bot/v3/info --as bot | jq -r '.bot.open_id')
if [ -z "${BOT_OPENID}" ] || [ "${BOT_OPENID}" == "null" ]; then
  echo "❌ 无法获取机器人 OpenID"
  exit 1
fi
echo "✅ 机器人 OpenID: ${BOT_OPENID}"

# 2. 获取知识库 Space ID
echo "📌 步骤 2/5: 获取知识库 Space ID..."
SPACE_ID=$(lark-cli wiki spaces list | jq -r '.spaces[] | select(.name=="'${SPACE_NAME}'") | .space_id')
if [ -z "${SPACE_ID}" ] || [ "${SPACE_ID}" == "null" ]; then
  echo "❌ 未找到知识库：${SPACE_NAME}"
  echo "可用知识库："
  lark-cli wiki spaces list | jq -r '.spaces[] | "  - \(.name)"'
  exit 1
fi
echo "✅ 知识库 Space ID: ${SPACE_ID}"

# 3. 检查当前用户权限
echo "📌 步骤 3/5: 检查用户权限..."
USER_INFO=$(lark-cli contact +get-user --as user)
USER_NAME=$(echo "${USER_INFO}" | jq -r '.data.user.name')
USER_OPENID=$(echo "${USER_INFO}" | jq -r '.data.user.open_id')
echo "✅ 当前用户：${USER_NAME} (${USER_OPENID})"

# 4. 添加机器人到知识库
echo "📌 步骤 4/5: 添加机器人为管理员..."
RESULT=$(lark-cli wiki members create --as user \
  --params '{"space_id":"'${SPACE_ID}'"}' \
  --data '{"member_id":"'${BOT_OPENID}'","member_type":"openid","member_role":"admin"}' 2>&1)

if echo "${RESULT}" | grep -q '"code": 0'; then
  echo "✅ 添加成功！"
else
  echo "❌ 添加失败"
  echo "${RESULT}"
  exit 1
fi

# 5. 验证添加结果
echo "📌 步骤 5/5: 验证添加结果..."
MEMBER_INFO=$(lark-cli wiki members list --params '{"space_id":"'${SPACE_ID}'"}' | \
  jq '.data.members[] | select(.member_id=="'${BOT_OPENID}'")')

if [ -n "${MEMBER_INFO}" ]; then
  echo "✅ 验证成功！"
  echo "📋 机器人信息："
  echo "${MEMBER_INFO}" | jq .
else
  echo "⚠️ 验证失败：未找到机器人成员信息"
  exit 1
fi

echo ""
echo "🎉 完成！机器人已成功添加为知识库管理员。"
echo "📎 知识库：${SPACE_NAME}"
echo "🔗 Space ID: ${SPACE_ID}"
```

---

*最后更新：2026-04-24*
