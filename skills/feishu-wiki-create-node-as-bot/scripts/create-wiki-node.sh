#!/bin/bash
# 以机器人身份创建飞书知识库节点
# 用法：./create-wiki-node.sh <space_id> <title> [parent_token] [content]

set -e

SPACE_ID="${1:-}"
TITLE="${2:-}"
PARENT_TOKEN="${3:-}"
CONTENT="${4:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🦞 以机器人身份创建飞书知识库节点${NC}"
echo ""

# 检查参数
if [ -z "$SPACE_ID" ]; then
    echo -e "${RED}错误：请提供知识库 space_id${NC}"
    echo "用法：$0 <space_id> <title> [parent_token] [content]"
    echo ""
    echo "示例："
    echo "  $0 7631092179137579973 \"西湖印象\""
    echo "  $0 7631092179137579973 \"西湖历史\" LjMywprkiiKLAxkCtfvcGXoynXe"
    exit 1
fi

if [ -z "$TITLE" ]; then
    echo -e "${RED}错误：请提供文档标题${NC}"
    echo "用法：$0 <space_id> <title> [parent_token] [content]"
    exit 1
fi

# 检查 lark-cli 是否安装
if ! command -v lark-cli &> /dev/null; then
    echo -e "${YELLOW}未找到 lark-cli，正在安装...${NC}"
    npm install -g @larksuite/cli
fi

# 检查配置
echo "检查 lark-cli 配置..."
APP_ID=$(lark-cli config show 2>/dev/null | grep '"appId"' | cut -d'"' -f4)

if [ -z "$APP_ID" ]; then
    echo -e "${RED}错误：lark-cli 未配置${NC}"
    echo "运行以下命令初始化配置："
    echo "  lark-cli config init"
    exit 1
fi

echo -e "${GREEN}✓ 应用 ID: $APP_ID${NC}"

# 获取 tenant_access_token
echo ""
echo "获取 tenant_access_token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$(lark-cli config show 2>/dev/null | grep '"appSecret"' | cut -d'"' -f4)\"
  }")

TENANT_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TENANT_TOKEN" ]; then
    echo -e "${RED}错误：获取 tenant_access_token 失败${NC}"
    echo "响应：$TOKEN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ 获取 token 成功${NC}"

# 创建知识库节点
echo ""
echo "正在创建知识库节点..."
echo "  知识库 space_id: $SPACE_ID"
echo "  文档标题：$TITLE"
echo "  父节点 token: ${PARENT_TOKEN:-根目录}"
echo ""

CREATE_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/$SPACE_ID/nodes" \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"parent_token\": \"$PARENT_TOKEN\",
    \"title\": \"$TITLE\",
    \"obj_type\": \"docx\",
    \"node_type\": \"origin\"
  }")

# 检查结果
if echo "$CREATE_RESPONSE" | grep -q '"code":0'; then
    echo -e "${GREEN}✓ 创建成功！${NC}"
    
    # 提取节点信息
    NODE_TOKEN=$(echo "$CREATE_RESPONSE" | grep -o '"node_token":"[^"]*"' | cut -d'"' -f4)
    OBJ_TOKEN=$(echo "$CREATE_RESPONSE" | grep -o '"obj_token":"[^"]*"' | cut -d'"' -f4)
    OWNER=$(echo "$CREATE_RESPONSE" | grep -o '"owner":"[^"]*"' | cut -d'"' -f4)
    
    echo ""
    echo "节点信息："
    echo "  node_token: $NODE_TOKEN"
    echo "  obj_token: $OBJ_TOKEN"
    echo "  创建者：$OWNER"
    echo ""
    echo "文档链接：https://www.feishu.cn/wiki/$NODE_TOKEN"
    
    # 如果有内容，填充文档
    if [ -n "$CONTENT" ]; then
        echo ""
        echo "正在填充文档内容..."
        
        CONTENT_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/$OBJ_TOKEN/raw_content" \
          -H "Authorization: Bearer $TENANT_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{\"content\": $CONTENT}")
        
        if echo "$CONTENT_RESPONSE" | grep -q '"code":0'; then
            echo -e "${GREEN}✓ 内容填充成功${NC}"
        else
            echo -e "${YELLOW}⚠ 内容填充失败，可稍后手动编辑${NC}"
        fi
    fi
else
    echo -e "${RED}✗ 创建失败${NC}"
    echo ""
    echo "错误信息："
    echo "$CREATE_RESPONSE" | jq . 2>/dev/null || echo "$CREATE_RESPONSE"
    exit 1
fi

echo ""
echo -e "${GREEN}完成！${NC}"
