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
if [ "$WORKSPACE_NAME" = "workspace-specialresearch" ]; then
  BOT_PROFILE="speres_bot"
else
  AGENT_PREFIX=$(echo "$WORKSPACE_NAME" | sed -E 's/^workspace-//; s/^([A-Za-z]+).*/\1/' | tr '[:upper:]' '[:lower:]')
  BOT_PROFILE=$(jq -r ".channels.feishu.accounts | to_entries[] | select(.value.appId != null) | .key" ~/.openclaw/openclaw.json 2>/dev/null | grep "^${AGENT_PREFIX}_" | head -1)
  [ -z "$BOT_PROFILE" ] && BOT_PROFILE=$(jq -r '.profile // empty' ~/.lark-cli/config.json 2>/dev/null)
fi

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

# 专班行研库 space_id（不要使用 spaces[0]，避免误发到其他知识库）
SPACE_ID="7659307909225941978"

echo "📚 Space ID: ${SPACE_ID}"

TOTAL_CREATED=0
TOTAL_SKIPPED=0

# 按固定顺序遍历行业目录
for dir_name in "人工智能" "半导体" "智能制造" "新能源" "生物医药" "互联网"; do
  parent_token="${WIKI_PARENTS[$dir_name]}"
  source_dir="${SYNWIKI}/${dir_name}"
  
  # 收集目录下所有 .md 文件
  md_files=()
  for f in "${source_dir}"/*.md; do
    [ -f "$f" ] && md_files+=("$f")
  done
  
  if [ ${#md_files[@]} -eq 0 ]; then
    echo "⏭️  [${dir_name}] 无 .md 文件，跳过"
    TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    continue
  fi
  
  echo "📤 [${dir_name}] 检查到 ${#md_files[@]} 个文件，准备发布..."
  
  # 记录已创建的节点：node_token|filename（用于后续排序）
  created_nodes=()
  
  for md_file in "${md_files[@]}"; do
    filename=$(basename "$md_file" .md)
    md_dir=$(dirname "$md_file")
    md_name=$(basename "$md_file")
    
    # 如果同名节点已存在，则更新原节点内容；否则创建新节点
    existing_row=$(lark-cli wiki +node-list \
      --as bot \
      --profile "${BOT_PROFILE}" \
      --space-id "${SPACE_ID}" \
      --parent-node-token "${parent_token}" \
      --page-all \
      --page-limit 10 \
      -q '(.data.nodes // .data.items // [])[] | [.title, .node_token, .obj_token] | @tsv' 2>/dev/null | \
      sed 's/^"//; s/"$//; s/\\t/\t/g' | \
      awk -F'\t' -v title="$filename" '$1==title {print $2 "\t" $3; exit}')
    
    if [ -n "$existing_row" ]; then
      node_token=${existing_row%%$'\t'*}
      obj_token=${existing_row#*$'\t'}
      echo "  ↻ 已存在，更新内容: ${filename}"
    else
      # 创建 wiki 节点，标题与文件名一致
      result=$(curl -s -X POST "https://open.feishu.cn/open-apis/wiki/v2/spaces/${SPACE_ID}/nodes" \
        -H "Authorization: Bearer ${TENANT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"parent_node_token": "'"${parent_token}"'", "title": "'"${filename}"'", "obj_type": "docx", "node_type": "origin"}')
      
      obj_token=$(echo "$result" | jq -r '.data.obj_token // empty')
      node_token=$(echo "$result" | jq -r '.data.node_token // empty')
      
      if [ -z "$obj_token" ] || [ -z "$node_token" ]; then
        echo "  ❌ 创建失败 [${filename}]: $(echo "$result" | jq -r '.msg // .code_msg // "unknown"')"
        continue
      fi
    fi
    
    # 写入 markdown 内容（使用 lark-cli，机器人身份）
    update_result=$(cd "$md_dir" && lark-cli docs +update --api-version v2 \
      --doc "${obj_token}" \
      --profile "${BOT_PROFILE}" \
      --as bot \
      --command overwrite \
      --doc-format markdown \
      --content @"${md_name}" 2>&1)
    
    if echo "$update_result" | grep -q '"ok": true'; then
      echo "  ✅ ${filename}"
    else
      echo "  ⚠️  ${filename} (内容写入: ${update_result:0:80})"
    fi
    
    created_nodes+=("${node_token}|${filename}")
    TOTAL_CREATED=$((TOTAL_CREATED + 1))
    sleep 0.5
  done
  
  # --- 按文件日期倒序重排节点（最新在前）---
  if [ ${#created_nodes[@]} -gt 1 ]; then
    echo "    🔄 按日期倒序重排 ${#created_nodes[@]} 个节点（最新→最旧）..."
    
    # 按日期正序排序（旧→新），依次 move 回父节点下
    # 飞书 wiki 同父节点 move 后会把被移动节点放到末尾；旧→新 move 后，列表呈现最新→最旧
    IFS=$'\n' sorted_nodes=($(printf '%s\n' "${created_nodes[@]}" | sort -t'|' -k2))
    unset IFS
    
    for entry in "${sorted_nodes[@]}"; do
      ntoken=${entry%%|*}
      move_result=$(lark-cli wiki +move \
        --as bot \
        --profile "${BOT_PROFILE}" \
        --node-token "${ntoken}" \
        --source-space-id "${SPACE_ID}" \
        --target-parent-token "${parent_token}" 2>&1)
      
      if ! echo "$move_result" | grep -q '"ok": true'; then
        echo "    ⚠️  重排失败: ${move_result:0:120}"
      fi
      sleep 0.3
    done
    echo "    ✅ 重排完成"
  fi

  # --- 更新行业主节点目录页 ---
  parent_obj_token=$(lark-cli wiki +node-get \
    --as bot \
    --profile "${BOT_PROFILE}" \
    --token "https://ccn65szgfwm8.feishu.cn/wiki/${parent_token}" \
    -q '.data.obj_token' 2>/dev/null | tail -1 | tr -d '"')
  
  directory_file=$(mktemp "${TMPDIR:-/tmp}/synwiki-directory.XXXXXX")
  {
    printf '# %s\n\n' "$dir_name"
    printf '## 目录\n\n'
    
    child_rows=$(lark-cli wiki +node-list \
      --as bot \
      --profile "${BOT_PROFILE}" \
      --space-id "${SPACE_ID}" \
      --parent-node-token "${parent_token}" \
      --page-all \
      --page-limit 10 \
      -q '(.data.nodes // .data.items // [])[] | [.title, .node_token] | @tsv' 2>/dev/null | \
      sed 's/^"//; s/"$//; s/\\t/\t/g')
    
    sorted_child_rows=$(printf '%s\n' "$child_rows" | awk -F'\t' 'NF>=2 {date=""; if (match($1, /[0-9]{8}/)) date=substr($1, RSTART, RLENGTH); print date "\t" $1 "\t" $2}' | sort -r)
    if [ -z "$sorted_child_rows" ]; then
      printf -- '- 暂无子节点\n'
    else
      printf '%s\n' "$sorted_child_rows" | while IFS=$'\t' read -r _date title node; do
        printf -- '- [%s](https://ccn65szgfwm8.feishu.cn/wiki/%s)\n' "$title" "$node"
      done
    fi
  } > "$directory_file"
  
  if [ -n "$parent_obj_token" ]; then
    directory_dir=$(dirname "$directory_file")
    directory_name=$(basename "$directory_file")
    directory_result=$(cd "$directory_dir" && lark-cli docs +update --api-version v2 \
      --doc "${parent_obj_token}" \
      --profile "${BOT_PROFILE}" \
      --as bot \
      --command overwrite \
      --doc-format markdown \
      --content @"${directory_name}" 2>&1)
    
    if echo "$directory_result" | grep -q '"ok": true'; then
      echo "    ✅ 已更新主节点目录"
    else
      echo "    ⚠️  主节点目录更新失败: ${directory_result:0:120}"
    fi
  else
    echo "    ⚠️  无法获取主节点 obj_token，跳过目录更新"
  fi
done

echo ""
echo "========================================"
echo "✅ synwiki-sync 完成"
echo "   创建: ${TOTAL_CREATED} 个节点"
echo "   跳过: ${TOTAL_SKIPPED} 个行业"
echo "========================================"
```

### 注意事项

1. **目标知识库固定是专班行研库**：入口 URL 为 `https://ccn65szgfwm8.feishu.cn/wiki/JQrjw9p5jiIEqGkDaUCcujaUnhd?fromScene=spaceOverview`，`space_id=7659307909225941978`。不要用 `spaces[0]`，否则可能误发到 `AI行研` 等其他知识库。
2. **bot profile 固定优先 `speres_bot`**：不要裸用 `--as bot`，也不要依赖 lark-cli 默认 profile；默认 profile 可能是 `ai_bot`。
3. **不要让用户做 OAuth 授权**：本流程应使用机器人身份和 tenant token。遇到读节点权限问题，先检查 bot profile、知识库成员权限和应用 Wiki scope，不要误走 user OAuth。
4. **解析 wiki 节点要传完整 URL 或明确 wiki token**：`lark-cli wiki +node-get` 传裸 token 时可能被当成文档 obj_token，优先传 `https://ccn65szgfwm8.feishu.cn/wiki/<node_token>`。
5. **lark-cli 输出可能混入代理 warning**：需要机器解析字段时优先使用 `-q`，或确保 stderr 不污染 JSON；不要直接把混有 warning 的输出喂给 `jq`。
6. **`docs +update --content` 只能用当前目录下的相对路径**：写周报正文或目录页前先 `cd "$(dirname "$file")"`，然后用 `--content @"$(basename "$file")"`。
7. **同名周报不要重复创建**：创建前先列父节点子节点；若标题已存在，更新原节点内容并参与排序。
8. **节点排序用 `lark-cli wiki +move`**：不要调用旧的 `PUT /wiki/v2/spaces/{space_id}/nodes/{node_token}/move`，该路径会 404。对同父节点按旧→新依次 move，可得到新→旧的展示顺序。
9. **主节点也要更新目录页**：发布/更新子节点后，必须覆盖更新每个行业主节点页面，内容为 `# 行业名` + `## 目录` + 按日期倒序排列的子节点链接。
10. **节点标题**：wiki 节点标题与 `.md` 文件名（不含 `.md` 后缀）完全一致。
11. **日期范围**：本周定义为周一到周日。如果本周文件尚未生成，对应行业会被跳过。
12. **文件格式**：仅处理 `.md` 文件，`.docx` 文件不处理。
13. **限流**：每个节点创建后 sleep 0.5s，重排 move 操作后 sleep 0.3s。
14. **新能源/生物医药**：这两个行业当前没有 `.md` 格式周报（只有 `.docx`），会被优雅跳过。
