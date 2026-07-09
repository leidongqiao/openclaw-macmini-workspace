---
name: "synwiki-sync"
description: "Sync weekly industry reports from researcher workspaces to synwiki and publish to Feishu wiki as bot"
---

# synwiki-sync

同步各行业周报文件到 synwiki 目录并发布到飞书知识库（机器人身份）。

## 流程概览

1. **清理**：清空 `synwiki/` 下所有文件（保留子目录）
2. **拷贝**：从 6 个 researcher workspace 找到本周最新周报 → 拷贝到对应 synwiki 子目录
3. **发布**：以机器人身份将 .md 文件创建为飞书知识库节点

## 配置映射

```bash
SYNWIKI_ROOT="/Users/leidongqiao/.openclaw/workspace/workspace-specialresearch/synwiki"
```

| 行业 | 源目录 | 文件名模式 | synwiki 子目录 | Wiki 父节点 token |
|------|--------|-----------|---------------|-------------------|
| 人工智能 | `workspace-AIResearcher/reports/ai-weekly/` | `人工智能行业周报-YYYYMMDD.md` | `人工智能/` | `Vu3SwsJ05iCMA1k8LvBcGg2in9d` |
| 半导体 | `workspace-BDTresearcher/reports/bdt-weekly/` | `半导体行业周报-YYYYMMDD.md` | `半导体/` | `RhYewGHOzixfrikqu7ectouDnBh` |
| 智能制造 | `workspace-IMresearcher/reports/im-weekly/` | `智能制造行业周报-YYYYMMDD.md` | `智能制造/` | `XN3Lw44b8i9hXUkMIQ2clS9nnYf` |
| 新能源 | `workspace-NEresearcher/reports/ne-weekly/` | `新能源行业周报-YYYYMMDD.md` | `新能源/` | `VWPXwgUqyings6kRc8Ucbwlgnce` |
| 生物医药 | `workspace-SWYYresearcher/reports/biomed-weekly/` | `生物医药行业周报-YYYYMMDD.md` | `生物医药/` | `IuvHw09upiUHuuk2cDYcSpiUn4g` |
| 互联网 | `workspace-WEBresearcher/reports/web-weekly/` | `互联网行业周报-YYYYMMDD.md` | `互联网/` | `JO90w8ahli2o9AkyX6fcDww7nWb` |

## 执行步骤

### Step 1: 清理 synwiki 目录下的所有文件

```bash
SYNWIKI="/Users/leidongqiao/.openclaw/workspace/workspace-specialresearch/synwiki"

# 删除所有文件（包括隐藏文件），保留目录结构
find "$SYNWIKI" -type f -delete

echo "✅ synwiki 文件清理完成"
```

### Step 2: 拷贝本周最新周报

本周定义为周一到周日。先计算本周起止日期：

```bash
SYNWIKI="/Users/leidongqiao/.openclaw/workspace/workspace-specialresearch/synwiki"
WORKSPACE_BASE="/Users/leidongqiao/.openclaw/workspace"

# 计算本周一（ISO Monday）和本周日
MONDAY=$(date -v-monday '+%Y%m%d')
SUNDAY=$(date -v+6d -v-monday '+%Y%m%d')

echo "📅 本周范围: ${MONDAY} ~ ${SUNDAY}"
```

对每个行业执行：

```bash
# 行业映射表：行业名|源相对路径|文件名前缀|synwiki子目录
INDUSTRIES=(
  "人工智能|workspace-AIResearcher/reports/ai-weekly|人工智能行业周报|人工智能"
  "半导体|workspace-BDTresearcher/reports/bdt-weekly|半导体行业周报|半导体"
  "智能制造|workspace-IMresearcher/reports/im-weekly|智能制造行业周报|智能制造"
  "新能源|workspace-NEresearcher/reports/ne-weekly|新能源行业周报|新能源"
  "生物医药|workspace-SWYYresearcher/reports/biomed-weekly|生物医药行业周报|生物医药"
  "互联网|workspace-WEBresearcher/reports/web-weekly|互联网行业周报|互联网"
)

for entry in "${INDUSTRIES[@]}"; do
  IFS='|' read -r name src_rel prefix dest_dir <<< "$entry"
  
  SRC_DIR="${WORKSPACE_BASE}/${src_rel}"
  DEST_DIR="${SYNWIKI}/${dest_dir}"
  
  # 确保目标目录存在
  mkdir -p "$DEST_DIR"
  
  echo "📂 [$name] 搜索: ${SRC_DIR}"
  
  # 查找本周内的 .md 文件（文件名包含 YYYYMMDD 格式日期）
  LATEST_FILE=""
  LATEST_DATE=""
  
  for f in "${SRC_DIR}"/${prefix}-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].md; do
    [ -f "$f" ] || continue
    
    # 从文件名提取日期
    FNAME=$(basename "$f")
    FDATE=$(echo "$FNAME" | grep -oE '[0-9]{8}' | tail -1)
    [ -z "$FDATE" ] && continue
    
    # 检查是否在本周范围内
    if [[ "$FDATE" -ge "$MONDAY" && "$FDATE" -le "$SUNDAY" ]]; then
      if [[ -z "$LATEST_DATE" || "$FDATE" -gt "$LATEST_DATE" ]]; then
        LATEST_DATE="$FDATE"
        LATEST_FILE="$f"
      fi
    fi
  done
  
  if [ -n "$LATEST_FILE" ]; then
    cp "$LATEST_FILE" "$DEST_DIR/"
    echo "  ✅ 已拷贝: $(basename "$LATEST_FILE")"
  else
    echo "  ⚠️  本周（${MONDAY}~${SUNDAY}）无匹配文件，跳过"
  fi
done
```

**容错说明**：某些行业（如新能源、生物医药）可能没有 `.md` 格式的周报（只有 `.docx`），或本周尚未生成新报告。此时跳过该行业，不中断整体流程。

### Step 3: 发布到飞书知识库（机器人身份）

#### 3a. 检测 bot profile

```bash
export PATH="$HOME/.npm-global/bin:$PATH"

WORKSPACE_NAME=$(basename "/Users/leidongqiao/.openclaw/workspace/workspace-specialresearch")
AGENT_PREFIX=$(echo "$WORKSPACE_NAME" | sed -E 's/^workspace-//; s/^([A-Za-z]+).*/\1/' | tr '[:upper:]' '[:lower:]')
BOT_PROFILE=$(jq -r ".channels.feishu.accounts | to_entries[] | select(.value.appId != null) | .key" ~/.openclaw/openclaw.json 2>/dev/null | grep "^${AGENT_PREFIX}_" | head -1)
[ -z "$BOT_PROFILE" ] && BOT_PROFILE=$(jq -r '.profile // empty' ~/.lark-cli/config.json 2>/dev/null)

echo "🤖 BOT_PROFILE: ${BOT_PROFILE}"
```

#### 3b. 获取 tenant_access_token

```bash
APP_ID=$(jq -r ".channels.feishu.accounts.${BOT_PROFILE}.appId" ~/.openclaw/openclaw.json)
APP_SECRET=$(jq -r ".channels.feishu.accounts.${BOT_PROFILE}.appSecret" ~/.openclaw/openclaw.json)

TENANT_TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"${APP_ID}\",\"app_secret\":\"${APP_SECRET}\"}" | jq -r '.tenant_access_token')

echo "🔑 Token 获取成功: ${TENANT_TOKEN:0:10}..."
```

#### 3c. 遍历 synwiki 子目录并创建 wiki 节点

```bash
# 行业→父节点 token 映射
declare -A WIKI_PARENTS
WIKI_PARENTS[人工智能]="Vu3SwsJ05iCMA1k8LvBcGg2in9d"
WIKI_PARENTS[半导体]="RhYewGHOzixfrikqu7ectouDnBh"
WIKI_PARENTS[智能制造]="XN3Lw44b8i9hXUkMIQ2clS9nnYf"
WIKI_PARENTS[新能源]="VWPXwgUqyings6kRc8Ucbwlgnce"
WIKI_PARENTS[生物医药]="IuvHw09upiUHuuk2cDYcSpiUn4g"
WIKI_PARENTS[互联网]="JO90w8ahli2o9AkyX6fcDww7nWb"

# 获取知识库 space_id
SPACE_ID=$(curl -s -X GET "https://open.feishu.cn/open-apis/wiki/v2/spaces" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" | jq -r '.data.spaces[0].space_id')

echo "📚 Space ID: ${SPACE_ID}"

TOTAL_CREATED=0
TOTAL_SKIPPED=0

# 按固定顺序遍历（保证创建顺序可预期）
for dir_name in "人工智能" "半导体" "智能制造" "新能源" "生物医药" "互联网"; do
  PARENT_TOKEN="${WIKI_PARENTS[$dir_name]}"
  SOURCE_DIR="${SYNWIKI}/${dir_name}"
  
  MD_FILES=()
  for f in "${SOURCE_DIR}"/*.md; do
    [ -f "$f" ] && MD_FILES+=("$f")
  done
  
  if [ ${#MD_FILES[@]} -eq 0 ]; then
    echo "⏭️  [${dir_name}] 无 .md 文件，跳过"
    TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    continue
  fi
  
  # 按文件名倒序处理（最新文件最后创建，排在知识库最前）
  IFS=$'\n' SORTED_FILES=($(printf '%s\n' "${MD_FILES[@]}" | sort -r))
  unset IFS
  
  echo "📤 [${dir_name}] 发布 ${#SORTED_FILES[@]} 个文件..."
  
  for md_file in "${SORTED_FILES[@]}"; do
    FILENAME=$(basename "$md_file" .md)
    
    # 创建 wiki 节点
    RESULT=$(curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/${SPACE_ID}/nodes" \
      -H "Authorization: Bearer ${TENANT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"parent_node_token\": \"${PARENT_TOKEN}\",
        \"title\": \"${FILENAME}\",
        \"obj_type\": \"docx\",
        \"node_type\": \"origin\"
      }")
    
    OBJ_TOKEN=$(echo "$RESULT" | jq -r '.data.obj_token // empty')
    
    if [ -z "$OBJ_TOKEN" ]; then
      echo "  ❌ 创建失败 [${FILENAME}]: $(echo "$RESULT" | jq -r '.msg // .code_msg // "unknown"')"
      continue
    fi
    
    # 写入 markdown 内容（使用 lark-cli，机器人身份）
    UPDATE_RESULT=$(lark-cli docs +update --api-version v2 \
      --doc "${OBJ_TOKEN}" \
      --profile "${BOT_PROFILE}" \
      --as bot \
      --command overwrite \
      --doc-format markdown \
      --content @"${md_file}" 2>&1)
    
    if echo "$UPDATE_RESULT" | grep -q '"code": 0'; then
      echo "  ✅ ${FILENAME}"
      TOTAL_CREATED=$((TOTAL_CREATED + 1))
    else
      echo "  ⚠️  ${FILENAME} (内容写入: ${UPDATE_RESULT:0:80})"
      TOTAL_CREATED=$((TOTAL_CREATED + 1))
    fi
    
    sleep 0.5
  done
done

echo ""
echo "========================================"
echo "✅ synwiki-sync 完成"
echo "   创建: ${TOTAL_CREATED} 个节点"
echo "   跳过: ${TOTAL_SKIPPED} 个行业"
echo "========================================"
```

### 注意事项

1. **权限**：确保机器人已添加为知识库管理员（使用 `feishu-wiki-add-bot-admin` skill）
2. **文档创建时间倒序**：脚本按文件名倒序处理，最新文件最后创建，自然排在知识库最前面（飞书默认按创建时间正序展示）
3. **日期范围**：本周定义为周一到周日。如果本周文件尚未生成，对应行业会被跳过
4. **文件格式**：仅处理 `.md` 文件，`.docx` 文件不处理
5. **限流**：每个节点创建后 sleep 0.5s
6. **新能源/生物医药**：这两个行业当前没有 `.md` 格式周报（只有 `.docx`），会被优雅跳过
