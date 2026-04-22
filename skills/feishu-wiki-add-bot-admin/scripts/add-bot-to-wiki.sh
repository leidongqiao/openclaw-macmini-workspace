#!/bin/bash
# 将机器人添加为飞书知识库管理员
# 用法：./add-bot-to-wiki.sh <space_id> <bot_openid> [role]

set -e

SPACE_ID="${1:-}"
BOT_OPENID="${2:-}"
ROLE="${3:-admin}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🦞 将机器人添加为知识库管理员${NC}"
echo ""

# 检查参数
if [ -z "$SPACE_ID" ]; then
    echo -e "${RED}错误：请提供知识库 space_id${NC}"
    echo "用法：$0 <space_id> <bot_openid> [role]"
    echo ""
    echo "示例："
    echo "  $0 7631092179137579973 ou_89e1f41a6cb21a4a8203a50dcff87515 admin"
    exit 1
fi

if [ -z "$BOT_OPENID" ]; then
    echo -e "${RED}错误：请提供机器人 openid${NC}"
    echo "用法：$0 <space_id> <bot_openid> [role]"
    exit 1
fi

# 检查 lark-cli 是否安装
if ! command -v lark-cli &> /dev/null; then
    echo -e "${YELLOW}未找到 lark-cli，正在安装...${NC}"
    npm install -g @larksuite/cli
fi

# 检查用户登录状态
echo "检查 lark-cli 登录状态..."
USER_COUNT=$(lark-cli auth list 2>/dev/null | grep -c "userOpenId" || echo "0")

if [ "$USER_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}未检测到用户登录，请先授权${NC}"
    echo ""
    echo "运行以下命令完成授权："
    echo "  lark-cli auth login --recommend"
    echo ""
    echo "然后重新运行此脚本"
    exit 1
fi

echo -e "${GREEN}✓ 用户已登录${NC}"

# 添加机器人到知识库
echo ""
echo "正在添加机器人到知识库..."
echo "  知识库 space_id: $SPACE_ID"
echo "  机器人 openid: $BOT_OPENID"
echo "  角色：$ROLE"
echo ""

RESULT=$(lark-cli wiki members create --as user \
  --params "{\"space_id\":\"$SPACE_ID\"}" \
  --data "{\"member_id\":\"$BOT_OPENID\",\"member_type\":\"openid\",\"member_role\":\"$ROLE\"}" \
  2>&1)

# 检查结果
if echo "$RESULT" | grep -q '"code": 0'; then
    echo -e "${GREEN}✓ 添加成功！${NC}"
    echo ""
    echo "机器人已成为知识库的 $ROLE"
    echo ""
    echo "下一步：使用 feishu-wiki-create-node-as-bot skill 创建文档"
    echo "  ~/.openclaw/workspace/skills/feishu-wiki-create-node-as-bot/scripts/create-wiki-node.sh \\
    $SPACE_ID \"文档标题\""
else
    echo -e "${RED}✗ 添加失败${NC}"
    echo ""
    echo "错误信息："
    echo "$RESULT"
    exit 1
fi

# 验证添加结果
echo ""
echo "验证添加结果..."
lark-cli wiki members list --params "{\"space_id\":\"$SPACE_ID\"}" | \
  jq ".data.members[] | select(.member_id == \"$BOT_OPENID\")"

echo ""
echo -e "${GREEN}完成！${NC}"
