---
name: swyy-weekly-report
description: |
  生成生物医药行业研究周报（聚焦浙江），每两周爬取近 14 天多源行业研究内容，
  去重筛选并转化为银行商机清单。每两周周五执行，商机/行动清单/企业动态仅限浙江本地。
---

# 生物医药行业研究周报生成 Skill

每两周直接爬取近 14 天多源行业研究内容，生成双版本周报（Word详细报告 + 飞书wiki知识库存档）。

## 复用说明

本 skill 可复用于其他机器人。复用时需要修改「关键参数速查」章节中的值，
**其他内容（研究方法论、抓取流程、报告模板、写入逻辑）保持不变**。

### 每个 agent 需要修改的参数

| 参数 | 说明 | 如何获取 |
|------|------|----------|
| `BOT_PROFILE` | lark-cli profile 名称（对应 agent 自己的 bot） | `lark-cli config init --name <bot_name> --app_id <app_id>` 创建 |
| `WIKI_SPACE_ID` | 飞书知识库 space_id | `lark-cli wiki spaces list` |
| `WIKI_SPACE_NAME` | 知识库名称（用于去重搜索） | 从 wiki spaces list 确认 |
| `SPREADSHEET_TOKEN` | 商机挖掘表格的 spreadsheet_token | 从飞书表格 URL 提取 |
| `SHEET_ID` | 商机挖掘表格的 sheet_id | 从飞书表格 URL 提取 |
| `REGION` | 地域聚焦（如「浙江」「江苏」「广东」） | 根据 agent 定位 |
| `REGION_CITIES` | 地域下属城市列表 | 根据 agent 定位 |
| `WEEKLY_TITLE_PREFIX` | 周报文档标题前缀（如 `生物医药行业周报`） | 自定义 |

### 配置示例（在 agent 的 SKILL.md 同级创建 `config.json`）

```json
{
  "bot_profile": "swyy_bot",
  "wiki_space_id": "7637083944097270734",
  "wiki_space_name": "生物医药行研",
  "spreadsheet_token": "AQjXsU9DehPYPEtDlZbcYY6Wnsf",
  "sheet_id": "cfde3f",
  "region": "浙江",
  "region_cities": ["杭州","宁波","温州","绍兴","嘉兴","湖州","金华","台州","丽水","衢州","舟山"],
  "weekly_title_prefix": "生物医药行业周报"
}
```

### 使用方式

执行周报生成前，先读取同级 `config.json`（如有）并覆盖参数；如无则使用默认值。
命令中统一使用 `--profile $BOT_PROFILE`。

## 何时使用

- 用户说"生成周报"、"出周报"、"生物医药周报"、"行业周报"
- 定时任务触发
- 补发历史周报

## 核心原则

1. **直接爬取**：每两周从多源爬取近 14 天行业研究内容（行业报告、市场分析、技术趋势、政策动态）
2. **地域聚焦**：**商机地图、行动清单、企业动态仅限目标区域**（如浙江：杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山）；长三角异动作为补充参考
3. **TOP5-8精选**：本周最具实质影响的5-8条事件
4. **商机汇总**：按企业维度汇总本周可介入的商机
5. **双版本输出**：Word 版（详细报告） + wiki 版（知识库存档），内容结构一致
6. **独立运行**：周报由本 skill 独立负责

**研究方向：生物医药全产业链**（创新药/小分子/大分子生物药/细胞与基因治疗 CGT/ADC/双抗/mRNA、CXO（CRO/CDMO/CMO）、医疗器械（IVD/影像设备/高值耗材/低值耗材/手术机器人）、疫苗与血制品、体外诊断（化学发光/分子诊断/POCT）、中药/天然药物、合成生物学、AI制药、医美/化妆品、医药商业/流通、医药园区与产业基金、集采/医保谈判/CDE审评动态等）

## Token 优化原则

- **搜索优先用 searxng**（本地 SearXNG 实例），Brave web_search 作为备用；searxng 无 API 限流、无布尔 OR 语法问题、无需逐条串行。统一查询近 14 天；如工具仅支持 day/week/month 档位，用 `--time-range month` 拉宽后按发布日期或正文日期过滤近 14 天内容。
- **web_fetch 用 text 模式**（`extractMode: "text"`），比 markdown 模式更精简
- **maxChars=6000**，够提取文章摘要，不需要更大
- **iFinD 查询聚焦行业**：query 中必须限定生物医药相关关键词，避免返回宽泛金融数据；只保留已授权且稳定的 `search_notice`，不要再调用无权限的热点事件接口
- **iFinD 时间精确到近14天**：time_start/time_end 必须用实际日期，size 控制在 5-10
- **表格去重优先查 A 列**；写入后为排序/清空残留可读取 A:J 的有效范围
- **所有飞书 API 统一走 lark-cli**（sheets/drive/docs/wiki），不用 Python urllib 直接调 API，避免 SSL 代理问题
- **lark-cli 路径**:在 PATH 中可能不可用，实测位置为 `~/.npm-global/bin/lark-cli`。所有脚本中应优先使用绝对路径 `~/.npm-global/bin/lark-cli`。
- **lark-cli 命令按预定义参数执行**，不要反复试错
- **正文点入按需**：只在搜索结果发现重要线索时点入正文（maxChars=4000）
- **searxng 结果直接落盘**:输出是完整 JSON，避免在命令 stdout 中被截断。建议先写入临时文件再解析，不要在 exec 输出中直接解析。

## 执行经验与避坑指南(持续更新)

### 1. 工具调用与路径

- **lark-cli 不在 PATH**: 实测路径为 `~/.npm-global/bin/lark-cli`。所有脚本用绝对路径，别依赖 PATH。
- **lark-cli 输出混入 proxy warning**: 所有 lark-cli 命令 stderr 输出 `[lark-cli] [WARN] proxy detected: HTTPS_PROXY=...`，`| python3` 管道会 JSONDecodeError。lark-cli 输出必须先写文件（`> /tmp/xxx.json 2>&1`），再用 Python 跳过 warning 行找到 `{` 开头解析，不能直接管道。
- **lark-cli 收尾命令必须用绝对路径并显式验收**: cron/agent 的 PATH 不稳定，Wiki 创建、移动、更新、fetch 验证统一使用 `LARK="$HOME/.npm-global/bin/lark-cli"`。命令输出必须落盘，解析 JSON 后判断 `ok` 或关键 token；不要只看 stdout 文本。任何验证命令失败前，禁止先推送群聊摘要。
- **shell 收尾片段禁止写成 `set -e VAR=...`**: `set -e BASE=... LARK=...` 不会给 `BASE`/`LARK` 赋值，只会把它们当作 `set` 参数，后续 `cat "$BASE/..."` 会读错路径并导致 cron 失败。必须写成多行或分号分隔：`set -e; BASE="..."; LARK="..."; ...`。
- **searxng 截断**: 搜索结果 JSON 较大，直接 echo 会被截断。必须先写文件再解析。
- **iFinD search_trending_news 已停用**: 该接口受权限限制，返回 `Tool not allowed`。不要调用；如历史流程中出现，仅记录到执行日志，绝不写入周报正文/wiki/群聊摘要。
- **iFinD search_notice 可能为空**: 语义检索对时间范围和 query 要求严格，可能返回空。为空时正常标注，不影响报告。
- **iFinD 调用方式**: 不能直接向 `call-node.js` 喂 JSON，必须按 skill 要求用 Node `require` 方式调用 `call()` 函数。
- **Brave web_search 严禁并行**: 免费套餐 1 req/s，并行会触发 429。只有 searxng 可并行；Brave 作为兜底时必须串行、每次间隔 ≥1 秒，且不用 OR 语法。**Brave 对中文地域/工业术语索引极差**，宽泛搜索（如「生物医药 浙江 杭州 宁波 产业 2026」）返回 80% 不相关结果。Brave 仅适合精准搜索（具体企业名+融资/公告/一季报等），不要用于地域+行业的宽泛组合搜索。
- **lark-cli docs +update 的 `--content @./file` 必须用相对路径**: 先 `cd` 到 Markdown 所在目录，再用 `--api-version v2 --command overwrite --doc-format markdown --content @./wiki_YYYYMMDD.md`，不要传绝对路径。

### 2. 数据抓取

- **失效名单**: 旧证券时报快讯 `https://www.stcn.com/article/newsflash.html` 返回 404；替代地址 `https://news.stcn.com/` 可访问但内容陈旧（实测停留在 2022），不再作为必抓源。IT之家机器人 404、36氪研究院页面已删除。按规则跳过即可，不要重试。
- **JS 渲染失败**: 所有垂直源返回空白时，跳过并继续。

### 3. 飞书 Wiki

- **Wiki 节点默认挂在「首页」下**: `wiki +node-create --space-id` 创建后默认挂在「首页」节点下（`parent_node_token` 不为空），不是根目录。不要传 `--parent-node-token ""`（无效）。创建后必须用模板检查 `parent_node_token`，如不为空立即 `wiki +move --node-token <token> --target-space-id <space>` 移回根目录。
- **Wiki 单换行会黏行**: 飞书 Markdown 会把单换行合并。企业元数据必须用列表格式，标题和正文之间加空行。
- **Word 下载链接**: 用纯 URL 文本 `**Word版下载：** https://...`，不要写 `<https://...>`，尖括号可能被吞。
- **创建后必须 fetch 回来抽查**: 检查是否有 `推荐等级.*所属行业` 等同行黏连。
- **Wiki 链接统一用租户域名**: 输出 `https://<租户域名>.feishu.cn/wiki/<node_token>`，不要混用 `https://www.feishu.cn/wiki/...`。

### 4. 商机表格去重与写入

- **核心简称去重需别名映射**: 如 `杭州云深处科技有限公司` 和 `云深处科技（杭州）` 去括号后分别为 `云深处科技有限公司` 和 `云深处科技`，无法匹配。建议加入别名/简称映射表。
- **核心简称需去公司后缀**: 仅去括号不够。还要去掉 `股份有限公司`、`有限责任公司`、`有限公司` 等后缀，并维护别名表（如 `浙江拱东医疗器械` → `浙江拱东医疗`），否则同一企业可能重复写入。
- **状态保留规则**: 更新已有商机时，状态列保持不变。新增商机统一填「待联系」。表中会出现 `active`/`待联系` 混用，这是符合规则的。
- **排序 key 有 None 值**: 创建日期列可能有空值/None。排序时必须做 `str(r[8] or '')` 安全转换，直接比较会报 TypeError。
- **清理空行要验证**: `+delete-dimension` 后仍可能看到空白残留。先用空值覆盖 `A{end+1}:J{end+20}`，再删到 `row_count`，最后用 `sheets +info` 确认 `row_count == end_row`。

### 5. Word/Wiki 格式分离

- 建议用脚本生成两份：docx(去 Markdown 符号) 和 md(保留 Markdown)。
- Word 版用 python-docx 时，`- **` 等标记需去除，段落用纯文本。

## 工作流

### 第〇步：总体要求（分析师角色与全局规则）

你以平安银行杭州分行"首席行业分析师"身份进行分析，当前分析对象为生物医药。

核心职责不是简单汇总新闻，而是通过行业政策、政府规划、全国行业动态、浙江区域动态、重点企业动态和上下游产业链变化，挖掘可营销商机，并为客户经理生成清晰、简洁、可执行的企业推荐与银行产品配置方案。

分析必须服务于以下目标：
1. 生物医药近期为什么值得关注？
2. 浙江地区有哪些区域机会？
3. 哪些浙江企业值得优先拜访？
4. 推荐这些企业的理由是什么？
5. 平安银行有哪些展业机会？
6. 应该用哪些产品切入？
7. 客户经理该如何开口沟通？

**全局规则（13条，贯穿所有步骤）：**

1. 必须联网获取最新信息，不得只依赖历史知识。
2. 必须关注全国行业动态、浙江地区行业动态、相关企业动态、上下游产业链动态。
3. 第一大板块只分析全国层面、国家层面、行业层面动态，**不放浙江内容**。凡是浙江相关政策、规划、项目、产业集群、区域机会，统一放入第二部分。
4. 第二大板块单独分析浙江地区动态与区域机会。
5. 第三大板块为重点企业推荐。
6. 企业推荐部分必须说明"推荐理由"和"银行展业机会"。
7. 企业信息要简洁，但需要体现企业高层和核心团队背景，包括学校、专业、导师、职业生涯、产业资源等公开信息。
8. 平安银行产品推荐必须基于本地产品资料（`~/.openclaw/workspace/file/productFile.docx`），**不得虚构产品名称、额度、期限、费率或准入条件**。如果产品资料中没有明确参数，写"待沟通"。
9. 内容要清晰明了，不要写成长篇研究报告。
10. 无法确认的信息写"待核实"或"未披露"。
11. 每条重要判断都要形成闭环：事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作；但「近期政策变动」板块不要每条政策都单独写闭环，应先把政策内容写充分，最后统一写一段综合影响闭环。
12. 周报正文不要在句中写来源括注，例如"（5月14日吹风会，杭州网/人民网浙江）""（来源：XXX）"。如需保留依据，可在文末或开头"资料来源"统一概括，不要影响客户经理阅读。
13. **禁止将抓取日志和报错写入周报。** 数据源抓取状态（如"证券时报快讯返回404""iFinD公告语义检索返回空""热点事件接口无权限""垂直源XX首页偏产品介绍""JS渲染失败""跳过该源"等）是执行过程的调试信息，绝不出现在周报正文、wiki存档或群聊推送摘要中。报告开头/文末的"资料来源"只列出实际采用的信息源名称（如财联社、新华网、searxng搜索等），不写抓取结果、报错码、空返回等过程信息。

### 第一步：信息抓取（必抓源 + 搜索为主 + 垂直源补充）

**必抓源（3个，不可跳过）：**

```
1. 财联社电报 → web_fetch https://www.cls.cn/telegraph (extractMode="text", maxChars=6000)
2. 新华网科技 → web_fetch https://www.xinhuanet.com/tech/ (extractMode="text", maxChars=6000)
3. 36氪快讯 → web_fetch https://36kr.com/newsflashes (extractMode="text", maxChars=6000)
```

⚠️ **已移除的必抓源（经实测内容质量差或不可靠）：**
- ~~同花顺首页（10jqka.com.cn）~~：返回内容极少（<600字符），且多为通用财经新闻，与生物医药关联度低
- ~~经济观察网（eeo.com.cn）~~：readability 提取返回仅150字符，JS 渲染严重，实际无法抓取有效内容
- ~~证券时报快讯（stcn.com/article/newsflash.html）~~：旧地址 404；替代 `https://news.stcn.com/` 可访问但内容陈旧，实测停留在 2022，不再作为必抓源。若未来恢复，可作为可选补充源重新加入。

**如果上述3个必抓源中仍有返回空白/JS渲染失败的，跳过该源，记录并继续，不重试。**

**核心策略：必抓源打底，web_search 精准搜索补充，垂直源进一步补充。**

**第二轮：searxng 精准搜索（5个查询，并行执行）：**

⚠️ **优先用 searxng，不用 web_search（Brave）。Brave 不支持布尔 OR 语法，会把 `"A" OR "B"` 当精确匹配处理，返回大量无关结果。searxng 无此问题，且无 API 限流。**

```bash
SEARXNG_SCRIPT="~/.openclaw/skills/searxng/scripts/searxng.py"
SEARXNG_CMD="python3 $SEARXNG_SCRIPT search"

# 5个查询并行执行
1. $SEARXNG_CMD "创新药 新药获批 IND NDA CDE审评 临床试验 2026" -n 10 --time-range month --format json
2. $SEARXNG_CMD "CXO CRO CDMO 药物研发 医药外包 2026" -n 10 --time-range month --format json
3. $SEARXNG_CMD "医疗器械 IVD 高值耗材 影像设备 手术机器人 三类器械 2026" -n 10 --time-range month --format json
4. $SEARXNG_CMD "集采 医保谈判 医保目录 带量采购 DRG DIP 2026" -n 10 --time-range month --format json
5. $SEARXNG_CMD "生物医药 细胞治疗 基因治疗 ADC 双抗 融资 上市 2026" -n 10 --time-range month --format json
```
执行后必须按发布日期/正文日期过滤，只保留近 14 天内容；无法确认日期的结果，只有在正文明确属于本期周期时才采用。

**如果 searxng 实例不可用（返回空或连接失败），回退到 Brave web_search，但此时不用 OR 语法，改用空格分隔关键词：**
```
1. web_search("创新药 新药获批 IND NDA CDE审评", freshness="month", count=10)
2. web_search("CXO CRO CDMO 药物研发 医药外包", freshness="month", count=10)
3. web_search("医疗器械 IVD 高值耗材 影像设备", freshness="month", count=10)
4. web_search("集采 医保谈判 医保目录 带量采购", freshness="month", count=10)
5. web_search("生物医药 细胞治疗 基因治疗 ADC 双抗", freshness="month", count=10)
```
Brave 结果同样必须过滤到近 14 天。

⚠️ **Brave web_search 串行执行**（免费套餐限流1次/秒），每次间隔1秒。searxng 可并行执行。

**第三轮：生物医药垂直源补充（并行，2-3个）：**

```
6. 医药魔方 → web_fetch https://www.pharmcube.com/ (extractMode="text", maxChars=6000)
7. 生物谷 → web_fetch https://www.bioon.com/ (extractMode="text", maxChars=6000)
8. 药智网 → web_fetch https://www.yaozh.com/ (extractMode="text", maxChars=6000)
```

⚠️ **已移除的垂直源（经实测不可靠）：**
- ~~米内网/中国药店（menet.com.cn）~~：JS 渲染严重，readability 提取返回空白
- ~~丁香园/Insight数据库（dxy.cn）~~：内容混杂且需要登录，实际无法抓取有效行业信息

**如果垂直源返回空白/JS 渲染失败/fetch failed，跳过该源，不重试。**

**第四轮：本地生物医药专项搜索（1个，searxng）：**

```
10. $SEARXNG_CMD "生物医药 [地域名] 创新药 [核心城市] CXO 医疗器械" -n 10 --time-range month --format json
```
本地专项搜索同样只采用近 14 天内的有效线索。

**第五轮：iFinD 金融数据补充（2个公告查询，聚焦近14天生物医药行业）：**

⚠️ **iFinD 执行说明：**
- **必须执行公告语义检索**，不可跳过。iFinD 能提供上市公司公告语义检索，是其他源无法替代的。
- **为什么之前被跳过**：调用前未先测试 iFinD 环境是否可用，导致直接进入后续步骤。本次执行应先在循环外做一次快速探测（如 search_notice 测试 query），确认 `ok: true` 后再执行 2 个公告查询。
- **如果探测失败**：检查 `~/.openclaw/skills/ifind-finance-data/` 目录下是否有有效的密钥配置文件。如无配置，跳过本轮并仅记录执行日志，不写入周报正文/wiki/群聊摘要。
- **执行顺序**：探测 → 成功则执行 11/12 → 失败则记录原因，继续后续步骤。
- **不要调用** `search_trending_news`：该接口当前无权限，返回 403 `Tool not allowed`，已从固定流程移除。

```
11. search_notice（公告语义检索）：
    query="创新药 OR 新药获批 OR CXO OR CRO OR CDMO OR 医疗器械 OR IVD OR 疫苗 OR 细胞治疗 OR 基因治疗",
    time_start="近14天前日期（YYYY-MM-DD）", time_end="今天日期（YYYY-MM-DD）", size=10
    → 精准抓取近14天生物医药相关上市公司公告（融资/定增/产能/中标/重大合同/新药获批）

12. search_notice（公告语义检索）：
    query="集采 OR 医保谈判 OR 医保目录 OR 带量采购 OR NDA OR IND OR CDE OR 临床试验 OR 三类器械 OR 注册证",
    time_start="近14天前日期（YYYY-MM-DD）", time_end="今天日期（YYYY-MM-DD）", size=10
    → 精准抓取近14天集采/医保/审评相关上市公司公告

```

**iFinD 调用说明：**
- 使用 Node.js 方案（`call-node.js`，无需额外依赖）：`node ~/.openclaw/skills/ifind-finance-data/call-node.js`
- 使用 Python 方案：`python3 ~/.openclaw/skills/ifind-finance-data/call.py`
- 优先使用 Node.js 方案（环境要求更低）
- **强制调用签名**：`call-node.js` 的函数签名是 `call(serverType, toolName, params)`，公告检索必须写成 `call('news', 'search_notice', params)`。**禁止写成** `call('search_notice', params)`，否则会报 `unknown server_type: search_notice`。
- **不要直接执行 `node call-node.js search_notice ...`**；必须用 Node `require` 方式调用 `call()`。可直接复制以下模板：

```bash
node - <<'NODE' > "$BASE/ifind_notices.json" 2> "$BASE/ifind_notices.err"
const { call } = require('/Users/leidongqiao/.openclaw/skills/ifind-finance-data/call-node.js');
(async()=>{
  const time_start = 'YYYY-MM-DD'; // 近14天前实际日期
  const time_end = 'YYYY-MM-DD';   // 今天实际日期
  const probe = await call('news','search_notice',{query:'创新药 生物医药',time_start,time_end,size:1});
  if (!probe.ok) { console.log(JSON.stringify({probe}, null, 2)); return; }
  const q1 = await call('news','search_notice',{query:'创新药 OR 新药获批 OR CXO OR CRO OR CDMO OR 医疗器械 OR IVD OR 疫苗 OR 细胞治疗 OR 基因治疗',time_start,time_end,size:10});
  const q2 = await call('news','search_notice',{query:'集采 OR 医保谈判 OR 医保目录 OR 带量采购 OR NDA OR IND OR CDE OR 临床试验 OR 三类器械 OR 注册证',time_start,time_end,size:10});
  console.log(JSON.stringify({probe,q1,q2}, null, 2));
})().catch(e=>{ console.error(e); process.exit(1); });
NODE
```
- 每次调用后检查 `ok` 字段确认是否成功，失败则跳过该查询
- **`ok:true` 只代表接口调用成功，不代表有有效公告**；还必须解析返回正文是否包含“查询结果为空”。为空只记执行日志，不写入周报正文/wiki/群聊摘要。
- **时间参数必须用近 14 天的实际日期（YYYY-MM-DD 格式），不可用模糊描述**
- **行业限定**：query 中必须包含生物医药相关关键词（创新药/CXO/医疗器械/集采等），避免返回无关公告
- 如果 iFinD 密钥未配置或调用全部失败，跳过本轮，继续后续步骤；相关失败原因只记执行日志，不写入周报正文/wiki/群聊摘要

**按需补充：**
- 从搜索结果中发现重要文章时，点入正文抓取（web_fetch, extractMode="text", maxChars=4000）
- 如需更全面的市场/财经视角，可补充搜索："生物医药 行业 周报" OR "创新药 产业 趋势" OR "医疗器械 市场 分析"（count=5）

**抓取规则：**
- 必抓源不可跳过，即使返回空白/JS 渲染失败也要记录并继续
- web_search + 垂直源并行执行
- 如果 web_fetch 返回空白/JS 渲染失败，跳过该源，不要重试
- 关注 **近 14 天内** 发生的事件（周报覆盖两周范围）
- 关注目标区域及周边的生物医药企业动态优先

### 第二步：信息跟踪范围

按指令定义的四大维度分类和组织抓取到的信息：

#### 1. 全国行业动态

重点关注：
- 国家政策、产业政策、监管政策（医保/集采/CDE审评指导原则）
- 行业供需变化、价格变化、技术路线变化
- 扩产、并购、上市、融资、发债、重大项目
- 招投标、中标、大客户合作
- 出口、跨境、海外建厂、海外订单（CXO海外订单、医疗器械出海）
- 风险事件：临床试验失败、处罚、诉讼、亏损、债务压力、停产等

#### 2. 浙江区域动态

重点关注：
- 浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州等地政策
- 政府规划与产业方向必须优先聚焦浙江；浙江公开信息不足时，可补充长三角（上海/江苏/安徽）相关规划作为参考，但需明确标注地域且不得替代浙江结论
- 浙江"415X"先进制造业集群（生物医药、生命健康）
- 专精特新、小巨人、高新技术企业、隐形冠军
- 地方重大项目、产业园区、医药GMP认证、创新药产业化、CXO基地、医疗器械注册人制度等
- 浙江在生物医药中的产业集群（杭州钱塘新区医药港、绍兴滨海新区、台州原料药基地等）、重点企业、上下游配套和区域优势

#### 3. 企业动态

重点关注能转化为银行商机的信号：
- 扩产、拿地、环评、GMP车间建设、产业化基地开工
- 中标、新订单、新客户合作（集采中标、CXO大订单、医院采购）
- 出口增长、海外布局、跨境业务（License-out、海外临床、FDA申报）
- 上市辅导、定增、发债、融资（IPO受理、新药管线融资）
- 应收账款增加、存货增加（原料药/医药流通）、现金流压力
- 新药获批（IND/NDA/临床批件）、三类医疗器械注册证
- 成为链主企业、核心供应商、重点培育企业
- 司法、处罚、失信、经营异常等风险信号

#### 4. 上下游产业链动态

分析企业所在产业链：
- 上游：原料药（API）、药用辅料、包材、实验耗材、科研仪器、CRO早期研发服务
- 中游：药物研发、临床试验、CDMO生产、医疗器械制造、IVD生产
- 下游：医药商业/流通、医院/终端销售、医保支付
- 哪个环节景气上升（如ADC/CGT赛道、创新药出海）
- 哪个环节资金占用加大（如创新药研发周期长、原料药库存积压）
- 哪个环节适合供应链金融（如医药流通应收账款）
- 哪个核心企业可带动批量获客（如大型CXO平台、龙头药企）

**地域标签：**
- `[浙江]` / `[杭州]` / `[宁波]` / `[绍兴]` 等
- `[上海]` / `[江苏]` / `[南京]` / `[苏州]` / `[南通]` 等
- `[安徽]` / `[其他]` / `[全球]`

**重要性评级：**
- ★★★★★：国家级政策（医保目录调整/集采新规/CDE重磅指导原则）/ 百亿级投资 / 行业拐点
- ★★★★：省级政策 / 十亿级融资 / 重大集采中标 / 重磅新药获批
- ★★★：企业级公告（IND/NDA/临床进展）/ 产能变动 / 集采价格变动
- ★★：一般动态
- ★：值得关注但影响有限

### 第三步：分析逻辑

按照指令定义的闭环进行分析：

```
政策/资讯变化
→ 行业影响
→ 浙江区域机会
→ 企业经营信号
→ 上下游产业链传导
→ 企业金融需求
→ 平安银行产品匹配
→ 客户经理营销动作
```

**分析要求：**
- 每条重要判断都要形成闭环：事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作
- 「近期政策变动」写法：政策情况要比普通新闻更详细，说明发布主体、发布时间/背景、核心条款/支持方向、约束或机会点；不要在每条政策后都写"影响闭环"，而是在该小节末尾统一写一段"综合影响闭环"。
- 「政府规划与产业方向」写法：重点聚焦浙江地区（浙江省、杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山等）；若浙江本地信息不足，可扩展至长三角（上海、江苏、安徽）作为补充参考，并明确标注地域。
- 「来源引用」写法：正文不要出现"（日期，媒体/网站）""（来源：媒体名）"这类来源括注；日期可自然融入事实表述，来源统一放在报告开头或文末"资料来源"中概括。
- 第一大板块只分析全国层面、国家层面、行业层面动态，**不放浙江内容**
- 浙江相关政策、规划、项目、产业集群、区域机会统一放入第二部分
- 第一大板块不写浙江省或浙江各地市内容

### 第四步：企业推荐判断规则

#### 1. 推荐理由

推荐理由应来自事实信号，例如：
- 所属行业符合国家或浙江重点支持方向（创新药、高端医疗器械、CXO等）
- 企业处于景气上行或结构性机会赛道（如ADC/CGT出海、医疗器械国产替代）
- 企业位于浙江优势产业集群（杭州医药港、台州原料药、绍兴滨海等）
- 企业近期出现扩产、GMP建设、中标、License-out、融资等积极信号
- 企业在产业链中具备核心企业、链主企业、优质供应商或优质经销商地位
- 企业高层或团队具备较强产业、技术、资本、客户资源背景（如科学家创业、大药企高管出身）
- 企业具备银行授信、票据、供应链、跨境、现金管理、代发等切入空间
- 风险信号相对可控

#### 2. 银行展业机会

必须从企业经营活动推导银行业务机会：
- 扩产/GMP车间/产业化基地建设 → 项目贷款、设备融资、科技创新和技术更新改造再贷款、平安租赁
- 订单增长/集采中标/CXO大单 → 短贷、普惠信用贷、银票贴现、国内信用证、订单融资
- 应收账款增加/账期较长（医药流通/原料药） → 付融通、保理、商票保贴、商票e贴
- 供应链上下游关系明确（CXO-药企、原料-制剂、流通-医院） → 订单融资、订货贷、平台数字贷、供应链金融
- 出口/海外业务（License-out、FDA申报、海外临床、CXO海外订单） → 跨境支付结算、人民币国际证+福费廷、外币存款、跨境资金管理、平安避险
- 资金账户分散/管理复杂 → 数字财资、资产池、慧收款、移企付、口袋管家
- 员工规模较大/企业主需求明显 → 平安薪、个贷、家族信托、财富权益

### 第五步：企业高层与团队背景要求

企业关键信息中必须体现高层和团队背景，但要简洁。

重点关注：
- 董事长、实控人、总经理、CFO、CTO、核心创始人、首席科学家
- 教育背景：毕业学校、专业、学位
- 科研背景：导师、实验室、研究方向、学术成果（如院士团队、海归科学家、CRO/大药企背景），如公开可查
- 职业经历：曾任职企业（恒瑞/药明/复星/罗氏/辉瑞等）、产业经历、管理经历、创业经历
- 产业资源：是否来自龙头企业、高校科研院所（浙大/中科院等）、政府平台、上市公司、外企、核心客户体系
- 银行关注点：其背景是否有助于判断企业技术实力、客户资源、融资能力、资本市场潜力或决策链条

注意：
- 只使用公开可查信息。
- 不得虚构个人履历。
- 未披露的信息写"未披露"或"待核实"。

### 第六步：产品匹配规则

你只能基于本地产品资料（`~/.openclaw/workspace/file/productFile.docx`）中的平安银行产品库推荐产品，不得虚构产品名称、额度、期限、费率或准入条件。

如果产品资料中没有明确参数，写"待沟通"。

产品配置不要堆砌，采用"主推产品 + 配套产品"的方式。每家企业一般推荐2-4类产品即可。

优先使用以下产品方向：

1. **账户与资金管理**
   数字财资、资产池、慧收款、移企付、平安结算通、产业结算通、口袋管家

2. **融资与授信**
   - 短贷：平安透、网上自由贷
   - 普惠金融信用贷、普惠金融科创贷、普惠金融担保贷、普惠金融抵押贷
   - 银票极速贴现、银票无感贴现、国内信用证开证及融资
   - 科技创新和技术更新改造再贷款

3. **供应链金融**
   订单融资、付融通、商票保贴、商票贴现、商票e贴、订货贷、平台数字贷、普惠金融场景化方案

4. **跨境与出海**
   - 跨境支付结算、跨境贸易金融、跨境资金管理、外币存款
   - 人民币国际证+福费廷、境内企业外债贷款、非居民全球授信、平安避险、新银关通

5. **资本市场与综合金融**
   - 并购融资、银团融资、债券承销、债生态业务、资本市场融资、结构金融
   - 平安证券债券承销、平安租赁、保险资金债权投资计划、集合资金信托计划、永续债权投资计划/永续信托计划

6. **员工与企业主服务**
   平安薪、橙e贷、星链贷、普金信用贷、家族信托、私人理财权益、信用卡权益

### 第七步：生成周报（双版本输出）

**生成两种格式的周报，内容结构一致，输出方式不同：**

#### 版本A：Word 版（行业分析指令格式）

按以下完整结构生成详细行业分析报告，使用华文楷体：

```
# 生物医药行业商机周报

## 一、行业动态与发展总结
（仅全国/国家/行业层面，不含浙江内容）

### 1. 近期政策变动
（政策情况要写详细：发布主体/时间背景/核心条款/支持方向/约束要求；本小节末尾统一写一段“综合影响闭环”，不要每条政策各写一个闭环）

梳理近期国家部委、行业主管部门发布的相关政策、监管要求、产业扶持、财政补贴、设备更新、绿色低碳、专精特新、外贸稳增长、科技创新等政策变化。

要求：
- 不要简单罗列政策标题。
- 要说明政策对【目标行业】的影响。
- 要说明可能带来的银行业务机会。
- 如政策发布日期、发布部门、政策名称可查，应简要注明。
- 浙江省及浙江地市政策不要放在这里。

### 2. 政府规划与产业方向

只梳理国家层面的产业规划、重大项目规划、重点产业布局和未来产业方向。

重点关注：
- 国家级产业规划
- 国家战略性新兴产业
- 国家未来产业方向
- 全国层面的设备更新、绿色制造、智能制造、科技创新等方向
- 国家级重大工程、重大项目、产业基金或政策工具
- 对企业扩产、技改、融资、产业链协同的影响

### 3. 行业发展趋势

总结行业当前的发展阶段、景气度、需求变化、技术路线、价格变化、竞争格局和资本市场表现。

要求说明：
- 行业处于上行、分化、调整还是出清阶段
- 哪些细分赛道更有机会
- 哪些企业类型更值得银行关注
- 哪些风险需要提前识别

### 4. 上下游产业链动态

分析全国或行业层面的上游、中游、下游最新变化。

重点判断：
- 上游原材料、设备、零部件价格或供应变化
- 中游企业扩产、订单、产能利用率变化
- 下游需求、出口、客户结构、渠道变化
- 哪个环节资金占用变大
- 哪个环节适合供应链金融、票据、保理、订单融资、订货贷等产品切入

## 二、浙江地区动态与区域机会

### 1. 浙江政策与政府规划

梳理浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州等重点城市近期政策、产业规划、园区规划、招商引资、设备更新、技改补贴、绿色制造、智能制造等动态。

要求：
- 说明政策或规划对本地企业的影响。
- 说明可能带来的银行授信、票据、供应链、跨境、现金管理等机会。
- 如政策发布日期、发布部门、政策名称可查，应简要注明。

### 2. 浙江重点产业与区域机会

重点关注：
- 浙江“415X”先进制造业集群
- 【目标行业】在浙江的重点产业集群、重点园区和重点城市
- 专精特新、小巨人、高新技术企业、隐形冠军
- 产业园区、开发区、重点项目、产业基金、招商落地项目

要求说明：
- 哪些产业集群正在释放机会
- 哪些区域更值得客户经理重点扫客
- 哪些企业类型更可能产生融资、供应链、跨境或现金管理需求

### 3. 浙江上下游产业链动态

分析浙江本地产业链上下游变化：
- 上游原材料、设备、零部件供应
- 中游制造、加工、集成、平台企业
- 下游客户、外贸订单、经销商、终端应用
- 哪些环节资金占用增加
- 哪些环节适合批量获客或供应链金融切入
- 哪些核心企业可以带动上下游企业营销

### 4. 银行展业机会

用3-5条总结浙江地区最值得平安银行杭州分行关注的展业机会。

要求：
- 必须结合浙江本地政策、产业集群、企业动态和产业链变化。
- 必须说明对应的银行业务机会。
- 尽量落到具体产品方向，如授信融资、票据、保理、供应链金融、跨境结算、现金管理、代发、财富管理等。

## 三、重点企业推荐

选择3-8家最值得客户经理跟进的浙江企业。每家企业按照以下模板输出。
⚠️ **硬性结构要求（不可压缩/不可省略）**：每一家企业必须严格保留下列字段和小标题；不得把“企业关键信息”合并成一段，也不得把“推荐理由”“银行展业机会”改写成无结构长段。若资料不足，字段仍保留，并写“未披露/待核实”。生成完成后必须逐家自检：是否包含【推荐等级、所属行业、所在地区、产业链位置、推荐方向、企业关键信息-基本情况、企业关键信息-高层与团队背景、企业关键信息-银行关注点、推荐理由、银行展业机会、推荐产品组合、客户经理切入话术、风险提示】；缺一项必须返工。

### 企业名称：XXX公司

**推荐等级：** 高 / 中 / 低
**所属行业：**
**所在地区：**
**产业链位置：** 上游 / 中游 / 下游 / 平台型 / 服务商
**推荐方向：** 流动资金 / 供应链金融 / 跨境结算 / 票据 / 现金管理 / 代发 / 财富管理 / 综合金融等。

**企业关键信息：**
- **基本情况：** 主营业务、成立时间、所在地、企业性质、商业模式、产业链位置。
- **高层与团队背景：** 董事长/实控人/总经理/CFO/CTO的教育背景、学校、导师、职业经历、产业资源；未公开标注"未披露/待核实"。
- **银行关注点：** 管理层背景对企业技术实力、客户资源、融资能力、资本运作或决策路径的影响。

**推荐理由：**
- 基于政策、行业、浙江区域、企业动态、产业链位置、团队背景等事实信号写2-4点。
- 必须说明该企业为什么值得客户经理优先跟进。
- 不要只写企业好，要说明“好在哪里、机会在哪里、现在为什么值得看”。

**银行展业机会：**
- 从企业经营变化推导银行业务机会。
- 说明企业在授信融资、票据、保理、供应链金融、跨境结算、现金管理、代发、财富管理等方面的潜在需求。
- 必须讲清楚“企业经营场景 → 金融需求 → 平安银行可切入产品”。

**推荐产品组合：**
不用表格。用一段自然语言总结，必须包含“主推产品 + 配套产品 + 切入理由”。每家企业一般推荐2-4类产品即可，避免堆砌。例如：建议以【主推产品】切入，解决企业【核心经营/资金场景】；配套使用【产品1、产品2】，用于【具体理由】。资料未披露的额度、期限、费率或准入条件写“待沟通”。

**客户经理切入话术：**
简短、自然、可直接拜访使用的话术，避免生硬推销。

**风险提示：**
诉讼、负债率、应收账款、客户集中度、行业波动、政策依赖、核心团队稳定性等；无明显风险写"暂无明显公开风险，仍需结合征信、流水、财报、合同、客户结构和实地尽调确认"。

## 四、客户经理行动建议

用3-5条给出当天或近期最值得执行的动作，例如：
- 优先拜访哪些企业
- 从哪个业务场景切入
- 先聊哪些经营问题
- 准备哪些产品方案或材料
- 需要内部联动哪些产品经理或审批资源
```

**Word 输出要求：**
- **固定保存目录**：`/Users/leidongqiao/.openclaw/workspace/workspace-SWYYresearcher/reports/biomed-weekly/`（即 SWYY Researcher 工作空间的 `reports/biomed-weekly/`），不得保存到其他目录；如目录不存在先创建。
- **同步至本地上传目录**：Word 文件保存到固定目录后，必须执行以下步骤：
  1. 清空 `/Users/leidongqiao/Documents/codex project/local-uploader/data/生物医药` 目录下的所有文件（保留目录本身，不删除目录）
  2. 将生成的 Word 周报文件拷贝一份到该目录
- 推荐执行命令：
  ```bash
  UPLOAD_DIR="/Users/leidongqiao/Documents/codex project/local-uploader/data/生物医药"
  find "$UPLOAD_DIR" -maxdepth 1 -type f -delete
  cp "$WORD_FILE" "$UPLOAD_DIR/"
  ls -la "$UPLOAD_DIR"
  ```
- 文件名格式：`生物医药行业周报-YYYYMMDD.docx`（与 wiki 节点标题一致；实际日期格式为 yyyyMMdd）
- **同名覆盖检查**:生成前先检查该目录下是否已有同名文件,若存在则直接覆盖,不保留重复文件。
- 字体使用华文楷体
- **Word 样式优化**：Word 版必须是干净的报告排版，不要把 Markdown 原始符号带入正文；生成 docx 时需去掉 `- **`、`**`、表格竖线等 Markdown 标记。普通段落用自然段，企业信息可用短段落或简洁项目符号，但不要让每段前面都出现 `- **`。推荐产品组合不得用表格。

##### Word 下载链接

Word 文件上传飞书 Drive 后获取 `file_token`，拼接下载链接：
```
https://<租户域名>.feishu.cn/file/<file_token>
```
例如：`https://qcn8k445rrbc.feishu.cn/file/DWMabuSB5og3PbxtC0OcY4kQnQg`

**使用方法（含同名覆盖）：**

⚠️ **上传前必须检查 Drive 中是否存在同名文件，如有则先删除再上传，确保 Drive 中只保留最新版本。**

```bash
export BOT_PROFILE
WEEKLY="生物医药行业周报-YYYYMMDD.docx"

# 1. 先列出根目录，查找同名旧文件并删除
lark-cli drive +list --profile "$BOT_PROFILE" > /tmp/drive_list.json 2>&1
python3 - <<'PYEOF'
import json, subprocess, os

text = open('/tmp/drive_list.json').read()
idx = text.find('{')
if idx < 0:
    sys.exit(0)
data = json.loads(text[idx:])
files = data.get('data', {}).get('files', []) or data.get('files', [])
target = os.environ.get('WEEKLY', '')
for f in files:
    ft = f.get('file_token', '')
    fn = f.get('name', '') or f.get('file_name', '')
    if fn == target:
        print(f"Deleting old file: {fn} ({ft})")
        lark_bin = os.path.expanduser('~/.npm-global/bin/lark-cli')
        subprocess.run([lark_bin, 'drive', '+delete',
                        '--profile', os.environ['BOT_PROFILE'],
                        '--file-token', ft, '--type', 'file'],
                       capture_output=True, text=True)
PYEOF

# 2. 上传新文件
lark-cli drive +upload --profile "$BOT_PROFILE" \
  --file "./$WEEKLY" --name "$WEEKLY" > /tmp/drive_upload.json 2>&1
```

3. 从上传返回结果获取 `file_token`
4. 拼接下载链接：`https://<租户域名>.feishu.cn/file/<file_token>`
5. 将该链接写入 wiki 正文开头和推送摘要中

**租户域名获取方式：**
- 从已有的飞书 wiki URL 中提取，例如 `https://qcn8k445rrbc.feishu.cn/wiki/...` 中的 `qcn8k445rrbc`
- 或从 `lark-cli wiki nodes list` 返回的 URL 中提取

**说明：** 该链接在飞书租户内用户已登录状态下可访问下载/预览。

#### 版本B：飞书 wiki 版（知识库存档格式）

- 内容与 Word 版结构一致，适配飞书文档 Markdown 格式
- **固定保存目录**：`/Users/leidongqiao/.openclaw/workspace/workspace-SWYYresearcher/reports/biomed-weekly/`（即 SWYY Researcher 工作空间的 `reports/biomed-weekly/`），不得保存到其他目录
- 文件名格式：`生物医药行业周报-YYYYMMDD.md`（与 wiki 节点标题一致；实际日期格式为 yyyyMMdd）
- **同名覆盖检查**:生成前先检查该目录下是否已有同名文件,若存在则直接覆盖,不保留重复文件。
- 通过第九步写入知识库
- wiki 正文开头（标题下方、覆盖周期/资料来源前）必须写入：`**Word版下载：** [点击下载Word版周报](飞书Drive下载链接)`。
- ⚠️ **wiki 正文中的 Word 下载链接必须用纯 URL 文本**，格式为 `**Word版下载：** https://.../file/...`，不要写成 `<https://...>`；飞书文档转换可能吞掉尖括号链接，导致 wiki 中只剩空的“Word版下载”。
- ⚠️ **飞书 wiki 排版硬规则：不要依赖单换行。** 飞书文档会把普通 Markdown 单换行合并，导致“推荐等级/所属行业/所在地区/产业链位置/推荐方向”等字段黏在一行。
- ⚠️ **企业元数据必须用列表格式**（`- 推荐等级：高`），不要用 `**推荐等级：** 高`（飞书 Markdown 会把连续行合并到一行，导致所有字段挤在一起），格式如下：
  ```markdown
  - **推荐等级：** 高
  - **所属行业：** XXX
  - **所在地区：** 杭州
  - **产业链位置：** 中游/平台型
  - **推荐方向：** XXX
  ```
- ⚠️ **企业关键信息也必须用列表格式并逐项换行**，不要写成一整段；固定格式如下：
  ```markdown
  **企业关键信息:**
  - **基本情况:** XXX
  - **高层与团队背景:** XXX
  - **银行关注点:** XXX
  ```
  写入 wiki 后抽查时,除企业元数据黏连外,还必须检查是否存在 `企业关键信息.*基本情况.*高层与团队背景.*银行关注点` 或 `基本情况.*高层与团队背景` 同一行黏连；发现即重写修复。
- ⚠️ **Word 与 Wiki 格式分离**：Word 版去掉所有 Markdown 标记（纯段落 + 华文楷体）；Wiki 版保留完整 Markdown（标题、列表、加粗、分隔线）。两者内容相同，格式各自适配平台。写入 wiki 后必须 fetch 回来抽查一次，重点检查是否存在 `推荐等级.*所属行业`、`所属行业.*所在地区`、`所在地区.*产业链位置`、`产业链位置.*推荐方向` 这类同一行黏连；发现即重写修复。


### 第八步：更新/追加商机到表格

从第七步周报的「四、客户经理行动建议」中提取需要跟进的浙江生物医药企业，写入「商机挖掘」电子表格。

**🔴 关键规则（必须严格遵守）：**
- **从行动建议提取**：从周报「四、客户经理行动建议」中提取明确提及的浙江生物医药企业，这些是需要客户经理优先跟进的商机
- **只写入目标区域本地企业**，非目标区域企业一律不写入表格
- **写入前必须去重**：先读取 A 列，用「规范化核心简称精确匹配」判断是否已存在
- **禁止重复写入同一企业**：同一核心简称只保留一行，已有行则更新，无则追加

**去重逻辑（严格执行）：**

⚠️ **第一步：规范化核心简称提取（关键！）**
1. 先将括号统一为全角：`(` → `（`, `)` → `）`
2. 然后去掉所有 `（...）` 修饰（地域、股票代码、备注等），得到**核心简称**
3. 再去掉常见公司后缀：`股份有限公司`、`有限责任公司`、`有限公司`、`集团股份`、`集团` 等，得到**核心去后缀简称**
4. 应维护一个本轮别名映射表，将明显同一企业的长短名称统一，例如：`浙江拱东医疗器械` → `浙江拱东医疗`，`云深处科技杭州` → `云深处科技`。别名映射只用于去重 key，不改写 A 列原客户名称。

⚠️ **第二步：对已有 A 列的每一行也做同样的规范化**
对 A 列每个已有名称，同样去括号、去公司后缀、过别名映射，得到已有去重 key。

⚠️ **第三步：精确匹配去重 key**
将新商机的去重 key 与已有行的去重 key 做**完全匹配**（==），不是包含匹配。
- 如果去重 key 相同 → **原地更新该行**，**保持A列原名称不变**，只更新 B~J 列
- 如果没有任何已有行的去重 key 匹配 → **追加新行**

⚠️ **严禁**：
- 更新行时修改A列客户名称（包括加后缀、改格式等），必须保持原名称不变
- 用包含匹配（如"生物"匹配到"生物科技"），必须用核心简称完全匹配

**写入流程（严格执行）：**
1. 读取 A 列全量数据
2. 对 A 列每个非空名称做规范化：去括号、去公司后缀、过别名映射，得到**已有去重 key 列表**
3. 对本次商机先去重：按去重 key 合并同名企业，每个去重 key 只保留一条
4. 对每个去重后的商机：提取去重 key → 精确匹配 → 匹配到则更新，未匹配则追加
5. ⚠️ **更新已有商机时，创建日期（I列）必须更新为当前日期（YYYY-MM-DD）**
6. ⚠️ **如果匹配到的已有行状态为终态（closed/已关闭/已落地），则跳过该行，不更新**
7. ⚠️ **新增商机的状态列统一填写「待联系」，不要写 active/open**
8. ⚠️ **更新已有商机时，状态列保持不变，不修改**
9. ⚠️ **写入完成后，必须对整个表格进行时间倒序重排 + 清理残留空行**（见下方「表格排序与清理」）

**字段顺序**：客户名称、行业/领域、触发信号、优先级、推荐方案、预计金额、联系人、状态、创建日期、备注

**⚠️ 表格排序与清理（每次写入后必须执行）：**

**全部使用 lark-cli 完成，不用 Python urllib 直接调 API（避免 SSL 代理问题）。**

流程：
```bash
export BOT_PROFILE SPREADSHEET_TOKEN SHEET_ID
python3 <<'PYEOF'
import json, os, subprocess, sys

LARK = os.path.expanduser('~/.npm-global/bin/lark-cli')
PROFILE = os.environ['BOT_PROFILE']
TOKEN = os.environ['SPREADSHEET_TOKEN']
SHEET = os.environ['SHEET_ID']

def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout[:1000], p.stderr[:1000], file=sys.stderr)
        raise SystemExit(p.returncode)
    return p.stdout

# 1. 读取有效范围，过滤空白行
out = run([LARK, 'sheets', '+read', '--profile', PROFILE,
           '--spreadsheet-token', TOKEN, '--range', f'{SHEET}!A1:J400',
           '--value-render-option', 'ToString'])
rows = json.loads(out).get('data', {}).get('valueRange', {}).get('values') or []
header = rows[0]
data = []
for r in rows[1:]:
    while len(r) < 10: r.append('')
    if r[0] is not None and str(r[0]).strip():
        data.append(['' if v is None else v for v in r[:10]])

# 2. 按创建日期倒序，None 安全转换
data.sort(key=lambda x: str(x[8] or ''), reverse=True)
end_row = 1 + len(data)

# 3. 写回 header + 数据
run([LARK, 'sheets', '+write', '--profile', PROFILE,
     '--spreadsheet-token', TOKEN, '--range', f'{SHEET}!A1:J1',
     '--values', json.dumps([header], ensure_ascii=False)])
if data:
    run([LARK, 'sheets', '+write', '--profile', PROFILE,
         '--spreadsheet-token', TOKEN, '--range', f'{SHEET}!A2:J{end_row}',
         '--values', json.dumps(data, ensure_ascii=False)])

# 4. 先覆盖空值，再删除 end_row 之后的行，避免旧数据/空白残留
blank = [['' for _ in range(10)] for _ in range(20)]
run([LARK, 'sheets', '+write', '--profile', PROFILE,
     '--spreadsheet-token', TOKEN, '--range', f'{SHEET}!A{end_row+1}:J{end_row+20}',
     '--values', json.dumps(blank)])
info = json.loads(run([LARK, 'sheets', '+info', '--profile', PROFILE,
                       '--spreadsheet-token', TOKEN]))
sheets = info['data']['sheets']['sheets'] if isinstance(info['data'].get('sheets'), dict) else info['data'].get('sheets', [])
target = next((s for s in sheets if s.get('sheet_id') == SHEET or s.get('sheetId') == SHEET), sheets[0])
gp = target.get('grid_properties') or target.get('gridProperties') or {}
max_rows = int(gp.get('row_count') or gp.get('rowCount') or 0)
if max_rows > end_row:
    run([LARK, 'sheets', '+delete-dimension', '--profile', PROFILE,
         '--spreadsheet-token', TOKEN, '--sheet-id', SHEET, '--dimension', 'ROWS',
         '--start-index', str(end_row + 1), '--end-index', str(max_rows)])

# 5. 最小验证：row_count 应等于 end_row
print(json.dumps({'rows': len(data), 'end_row': end_row, 'max_rows_before_delete': max_rows}, ensure_ascii=False))
PYEOF
```

⚠️ **关键说明：**
- **所有飞书 API 操作统一走 lark-cli**（sheets/drive/docs/wiki），不用 Python urllib
- lark-cli 会自动处理代理和认证，无需手动获取 tenant_access_token
- `+delete-dimension` 的 `--end-index` 必须 ≤ sheet 实际行数，先通过 `+info` 获取
- 排序后必须清理 end_row 之后的所有行，否则会残留空行和旧数据

### 第九步：写入知识库（飞书 wiki 版）

**写入内容：第七步版本B（飞书 wiki 版），结构与 Word 版一致，适配飞书 Markdown 格式。**

**重要：每次生成都覆盖当前同名文件（生物医药行业周报-YYYYMMDD），不要有重复日期的文档。**

**Word 下载链接位置要求：** Word 版上传飞书 Drive 后获取 file_token，拼接下载链接 `https://<租户域名>.feishu.cn/file/<file_token>`；wiki 正文开头（标题下方、覆盖周期/资料来源前）必须写入 `**Word版下载：** <下载链接>`，推送摘要中的「周报全文（Word）」也必须使用该下载链接。

**🔴 输出链接格式强制规则（所有输出场景通用）：**
- Word 版：只输出 `https://<租户域名>.feishu.cn/file/<file_token>` 下载链接，**禁止输出本地路径**（如 `/Users/.../reports/.../xxx.docx`）
- Wiki 版：只输出 `https://<租户域名>.feishu.cn/wiki/<node_token>` 存档链接
- 商机表格：只输出 `https://<租户域名>.feishu.cn/sheets/<spreadsheet_token>` 表格链接
- **所有对用户的最终输出中，任何文件引用都必须是可点击的飞书链接，绝不允许出现本地文件系统路径**

**🔴 关键规则（必须严格遵守）：**
- 文档必须创建在知识库**根目录**（`parent_node_token` 为空字符串），**不能**创建在「首页」或其他节点下面
- **📅 时间倒序排列**：新周报 wiki 节点必须排在知识库根目录列表的「商机挖掘表格」节点**后面**，确保周报按**时间倒序**排列（最新周报在最前面，紧跟商机挖掘表格之后）。
- 必须使用**机器人身份**（lark-cli profile 对应 bot 应用）。**`--profile $BOT_PROFILE` 已经指定了机器人身份，不需要额外 `--as bot`**。

**步骤：**

1. **列出知识库所有节点，查找是否已有同名文档（搜索全部节点，不限根目录！）**：
   ```bash
   LARK="$HOME/.npm-global/bin/lark-cli"
   "$LARK" wiki nodes list --params '{"space_id":"'$WIKI_SPACE_ID'","page_size":50}' --profile "$BOT_PROFILE"
   ```
   从返回结果中搜索 title 为 `$WEEKLY_TITLE_PREFIX-YYYYMMDD` 的节点（例：`生物医药行业周报-20260612`），提取 `obj_token` 和 `node_token`。
   ⚠️ **必须搜索所有节点**（不限 `parent_node_token`），否则第一次创建时可能被放在「首页」下，第二次搜不到就重复创建了！
   ⚠️ **如果找到多个同名文档**，选 `obj_edit_time` 最新的那个，用 `docs +update` 覆盖；其余用 `drive files +patch --type docx --file-token <obj_token> --body '{"trash_type":"doc_trash"}'` 删除。

2. **如果找到同名文档**：
   - 将 wiki Markdown 写入本地文件（如 `wiki_YYYYMMDD.md`），先 `cd` 到该文件所在目录，再使用 `lark-cli docs +update --api-version v2 --doc <obj_token> --profile $BOT_PROFILE --as bot --command overwrite --doc-format markdown --content @./wiki_YYYYMMDD.md` 覆盖内容；**不要**用 `@/Users/.../wiki.md` 绝对路径
   - 输出文档链接：`https://<租户域名>.feishu.cn/wiki/<node_token>`

3. **如果未找到同名文档**：
   - 使用以下命令以**机器人身份**创建（注意必须带 profile，输出先落盘再解析）：
     ```bash
     LARK="$HOME/.npm-global/bin/lark-cli"
     "$LARK" wiki +node-create --profile "$BOT_PROFILE" \
       --space-id "$WIKI_SPACE_ID" \
       --title "$WEEKLY_TITLE_PREFIX-YYYYMMDD" \
       --obj-type "docx" > /tmp/wiki_create.json 2>&1
     ```
   - **位置检查与 move（强制模板，每次创建新节点必须复制执行）**：
     ```bash
     # 解析创建结果的 parent_node_token（注意 lark-cli 输出混入 proxy warning，必须先落盘解析）
     PARENT_TOKEN=$(python3 -c "
     import json, sys
     text = open('/tmp/wiki_create.json').read()
     idx = text.find('{')
     if idx < 0:
         print('wiki_create output has no JSON object', file=sys.stderr); sys.exit(1)
     data = json.loads(text[idx:])
     if not data.get('ok', True):
         print(data, file=sys.stderr); sys.exit(1)
     print(data['data'].get('parent_node_token',''))
     ")
     NODE_TOKEN=$(python3 -c "
     import json, sys
     text = open('/tmp/wiki_create.json').read()
     idx = text.find('{')
     if idx < 0:
         sys.exit(1)
     data = json.loads(text[idx:])
     token = data['data'].get('node_token','')
     if not token:
         print('node_token missing', file=sys.stderr); sys.exit(1)
     print(token)
     ")
     OBJ_TOKEN=$(python3 -c "
     import json, sys
     text = open('/tmp/wiki_create.json').read()
     idx = text.find('{')
     if idx < 0:
         sys.exit(1)
     data = json.loads(text[idx:])
     token = data['data'].get('obj_token','')
     if not token:
         print('obj_token missing', file=sys.stderr); sys.exit(1)
     print(token)
     ")

     if [ -n "$PARENT_TOKEN" ]; then
       echo "⚠️ Node created under parent '$PARENT_TOKEN', moving to root..."
       "$LARK" wiki +move --profile "$BOT_PROFILE" \
         --node-token "$NODE_TOKEN" \
         --target-space-id "$WIKI_SPACE_ID" > /tmp/wiki_move_root.json 2>&1
       python3 - <<'PY'
import json, pathlib, sys
text = pathlib.Path('/tmp/wiki_move_root.json').read_text(errors='ignore')
idx = text.find('{')
if idx < 0:
    print(text[-1000:], file=sys.stderr)
    sys.exit(1)
data = json.loads(text[idx:])
if not data.get('ok', True):
    print(data, file=sys.stderr)
    sys.exit(1)
PY
     else
       echo "✅ Node already at root"
     fi
     ```
   - 从返回结果提取 `obj_token`（用于内容更新）和 `node_token`（用于 URL）
   - 将 wiki Markdown 写入本地文件（如 `wiki_YYYYMMDD.md`），先 `cd` 到该文件所在目录，再使用 `lark-cli docs +update --api-version v2 --doc <obj_token> --profile $BOT_PROFILE --as bot --command overwrite --doc-format markdown --content @./wiki_YYYYMMDD.md` 写入内容；**不要**用绝对路径
   - 输出文档链接：`https://<租户域名>.feishu.cn/wiki/<node_token>`

4. **Wiki 节点排序调整（新建节点时必须执行）：**
   - 新周报节点创建并移到根目录后，需要确保其排在「商机挖掘表格」节点**后面**（实现时间倒序：最新周报紧跟表格之后）。
   - 先获取根目录节点列表，找到「商机挖掘表格」的 `node_token`：
     ```bash
     LARK="$HOME/.npm-global/bin/lark-cli"
     "$LARK" wiki nodes list --params '{"space_id":"'$WIKI_SPACE_ID'","page_size":50}' --profile "$BOT_PROFILE" > /tmp/wiki_root_nodes.json 2>&1
     ```
   - 解析返回结果，找到 title 包含「商机挖掘」的节点 `node_token`，记为 `$TABLE_NODE_TOKEN`。
   - ⚠️ **`lark-cli wiki +move` 不支持 `--insert-after` 参数**，无法在 wiki 内指定兄弟节点的插入顺序。飞书 wiki 根目录节点默认按创建时间倒序排列，新节点自然排在旧节点前面，**跳过此步骤即可**。

5. **创建/更新后必须做两项验证（不要只看命令成功）：**
   - 位置验证：再次 `wiki nodes list`，确认本次 `node_token` 的 `parent_node_token == ""`。如不为空，立刻执行 `wiki +move`。
   - 格式验证：执行 `docs +fetch` 抽查字段是否黏连。注意 `docs +fetch` 可能把换行以字面量 `\n` 输出，检查前必须先把 `\\n` 还原成真实换行；正则必须按行检查，**禁止用会跨行误报的全文 `.*` 检查**。可复制：

```bash
LARK="$HOME/.npm-global/bin/lark-cli"
"$LARK" docs +fetch --doc "$OBJ_TOKEN" --profile "$BOT_PROFILE" > wiki_fetch_YYYYMMDD.md 2>&1
python3 - <<'PY'
import json, pathlib, re, sys
text = pathlib.Path('wiki_fetch_YYYYMMDD.md').read_text(errors='ignore')
idx = text.find('{')
if idx < 0:
    print('docs fetch output has no JSON object', file=sys.stderr)
    print(text[-1000:], file=sys.stderr)
    sys.exit(1)
data = json.loads(text[idx:])
if not data.get('ok', False):
    print(data, file=sys.stderr)
    sys.exit(1)
text = data.get('data', {}).get('markdown', text)
text = text.replace('\\n', '\n')  # 避免 fetch 输出转义换行导致误报
bad = []
for line in text.splitlines():
    if re.search(r'推荐等级.*所属行业|所属行业.*所在地区|所在地区.*产业链位置|产业链位置.*推荐方向|企业关键信息.*基本情况|基本情况.*高层与团队背景', line):
        bad.append(line[:200])
print({'bad_lines': bad[:5], 'bad_count': len(bad)})
if bad:
    sys.exit(1)
PY
```

   - 如果验证失败，不要把“抓取/验证日志”写进周报；只修正 Markdown 空行后重新 `docs +update`。

**禁止**使用 `feishu_wiki_space_node` 工具（该工具可能将文档创建在首页下），必须使用 `lark-cli wiki +node-create --profile $BOT_PROFILE --space-id` 命令。

### 第十步：推送至群聊（极简概要 + 链接，200字左右）

**🔴 关键规则：推送到群聊的内容是极简概要和链接，不是全文！手机端必须能一次读完。**

**长度限制：正文控制在 200 字左右（不含链接 URL），最多不超过 300 字。**

推送至群聊的消息格式如下：

```markdown
📌 【目标行业】商机周报·浙江｜YYYY.MM.DD-MM.DD
🔥 主线：XXX、XXX、XXX
🏠 浙江机会：XXX
🏢 优先跟进：XXX、XXX、XXX
🎯 切入方向：XXX/XXX/XXX

Word:<a href="飞书Drive下载链接">Word版下载</a>
Wiki:<a href="https://www.feishu.cn/wiki/XXXX">知识库存档</a>
商机表:<a href="https://xxx.feishu.cn/wiki/XXXX">商机挖掘</a>
```

#### 10.1 同步至工作空间

推送前,先把要推送的摘要写一份到本地工作空间:

1. **清空目录:**删除 `reports/summary/` 目录下所有文件(目录本身保留)。
2. **写入文件:**将即将推送的群聊摘要内容写入 `reports/summary/SWYY-summary.md`。

```bash
# 清空目录
rm -f ~/.openclaw/workspace/workspace-SWYYresearcher/reports/summary/*
# 写入摘要
echo '<摘要内容>' > ~/.openclaw/workspace/workspace-SWYYresearcher/reports/summary/SWYY-summary.md
```

#### 10.2 推送至群聊

**推送内容要求：**
- 行业动态：只提炼 2-3 个主线关键词，不逐条列新闻
- 浙江区域：只写 1 句机会集中方向
- 企业推荐：只列重点 3 家以内，不写推荐理由
- 行动建议：只写 1 句“优先跟进 + 切入方向”
- 样式要求：正文四行呈现，固定为「🔥 主线 / 🏠 浙江机会 / 🏢 优先跟进 / 🎯 切入方向」，不要写成一大段话
- Word 周报飞书 Drive 下载链接（不要只放本地路径）
- 周报 wiki 存档链接
- 商机挖掘表格链接（sheets URL）
- 链接格式要求：群聊摘要必须使用 **飞书 post 富文本消息** 格式发送（`msg_type=post`），Word/Wiki/商机表三个链接必须用 `<a>` 标签包裹（`{"tag":"a","text":"点击打开","href":"URL"}`），**禁止使用裸 URL 或 Markdown 链接格式**；飞书 post 富文本中裸 URL 不一定会被自动识别成可点击链接。
- 群聊摘要发送方式：优先使用 `feishu_im_user_message`（或对应身份的消息工具），`msg_type=post`，`content` 为飞书富文本 JSON 数组，每个链接独立用 `a` tag 包裹。
- **不要**输出周报全文内容
- **不要**使用长分隔线、长清单、TOP5-8逐条新闻、企业推荐理由、执行日志

**🔒 群聊最终回复锁（防止误推全文/日志）：**
1. 任何会被 delivery / cron / 群聊看到的最终 assistant 回复，**必须且只能**使用本步骤的「200字左右极简概要 + 三个链接」格式。
2. **禁止**把以下内容作为最终群聊推送：执行日志、完成情况清单、工具调用结果、文件本地路径、Markdown/wiki 源稿、Word 正文全文、调试说明。
3. 推送前必须自检 4 项，缺一不可：
   - 已压缩为 2-3 个主线关键词，不是 TOP 新闻长清单；
   - Word 链接是飞书 Drive/file 下载链接,不是本地路径,且使用 `<a href="URL">标签文本</a>` 格式;
   - wiki 链接是 `https://www.feishu.cn/wiki/...`,且使用 `<a href="URL">标签文本</a>` 格式;
   - 商机表格链接是 sheets URL,且使用 `<a href="URL">标签文本</a>` 格式。
4. 如果 Word Drive 链接、wiki 链接或 sheets 链接任一缺失，**不要推送群聊摘要**；先补齐链接，再输出第十步模板。
5. 若需要向用户说明执行状态，只能在非群聊/人工排查上下文说明；在群聊定时任务中，最终输出仍必须是第十步摘要模板。

### 第十一步：表达风格

面向客户经理，不面向学术研究。写作风格规则：

1. **面向客户经理**：语言专业、直接、可执行，不是学术研究。
2. **不堆砌新闻**：不要简单罗列新闻标题，要说明影响和机会。
3. **不堆砌产品**：产品配置不要堆砌，采用"主推产品 + 配套产品"方式，每家企业一般推荐2-4类；重点企业推荐中的「推荐产品组合」用一段话总结，不用表格。
4. **企业重点讲清4件事**：推荐理由 → 银行展业机会 → 推荐产品组合 → 客户经理怎么开口。
5. **简要呈现企业基本信息**：不需要机械罗列全部工商信息。
6. **帮助形成判断**：输出要帮助客户经理回答——今天该联系谁、为什么联系、聊什么产品、怎么切入。
7. **Word输出**：字体使用华文楷体；版式要像正式报告，去掉 Markdown 原始符号（尤其是 `- **`、`**`、表格分隔线），避免每段前面都有项目符号和加粗标记。
8. **正文去来源括注**：周报正文去掉媒体/网站来源括注；不要出现"（日期，来源）""（来源：XXX）"。资料来源只在报告开头或文末统一概括。

### 第十二步：输出完成

输出完成后，由调用方（定时任务等）通过 delivery 配置推送到飞书群，无需在 skill 内执行推送。

**cron 执行硬规则：**
- 在定时任务中不要调用 `message` 工具手动推送群聊摘要；最终 assistant 回复必须就是第十步的极简摘要，交给 cron `delivery.mode=announce` 投递。
- 群聊摘要只能在 Word 上传、Wiki 写入/位置/格式验证、商机表写入全部成功后作为最终回复输出。
- 如果最后任一命令失败，停止并输出排查摘要，不能先发群消息再继续执行会失败的命令；否则会出现“周报已发 + cron 又发失败告警”的双消息问题。

## 特殊场景

### 信息源全部失败

如果所有 web_fetch 都失败或返回空白：
1. 不要编造内容
2. 告知用户信息源抓取失败，建议手动提供素材
3. 或基于已知信息生成最小化版本并标注"信息有限"

### 用户要求手动生成

用户说"生成上周周报"时，同样执行以上流程。

## 注意事项

1. **不编造数据**：所有企业、金额、日期必须来自爬取的实际信息
2. **产品资料**：产品推荐必须基于 `~/.openclaw/workspace/file/productFile.docx`，不得虚构产品名称、额度、期限、费率或准入条件
3. **地域限制**：本地行业动态、行动清单仅限浙江本地企业；非生物医药主业的大企业动态不纳入本地行业动态
4. **禁止推荐不合规业务**
5. **双版本输出**：Word 版用于详细报告（华文楷体），wiki 版用于知识库存档（飞书 Markdown 格式），内容结构一致
6. **知识库标题**：生物医药行业周报-YYYYMMDD（实际日期格式为 yyyyMMdd，如 `生物医药行业周报-20260612`）
7. **知识库写入**：必须使用 `"$HOME/.npm-global/bin/lark-cli" wiki +node-create --profile "$BOT_PROFILE" --space-id "$WIKI_SPACE_ID"` 创建，禁止使用 `feishu_wiki_space_node` 工具。去重时**搜索全部节点**（不限 parent_node_token），避免重复创建
8. **群聊推送**：推送概要 + 链接，不是全文
9. **商机挖掘表格**：数据来源为周报「四、客户经理行动建议」中提及的企业。写入前必须去重，只写浙江本地企业。更新已有商机时日期必须更新为当天。写入后必须按时间倒序重排并清理残留空行
10. **搜索优先 searxng**：searxng 无 API 限流、无布尔 OR 语法问题。查询近 14 天时用 `python3 ~/.openclaw/skills/searxng/scripts/searxng.py search "query" -n 10 --time-range month --format json` 拉宽后按发布日期/正文日期过滤近 14 天。Brave web_search 仅作为备用，且不用 OR 语法（Brave 不支持），改用空格分隔关键词并过滤近 14 天。
11. **代理配置**：Gateway 进程需配置代理环境变量（`HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:7890`），否则 Brave API 连接超时。lark-cli 会检测到代理变量并发出警告，不影响功能。
12. **Word 下载链接**：Word 文件上传飞书 Drive 后获取 file_token，拼接下载链接 `https://<租户域名>.feishu.cn/file/<file_token>`；将该链接写在 wiki 正文开头和推送摘要中。
13. **Word 输出**：字体使用华文楷体，固定保存到 `/Users/leidongqiao/.openclaw/workspace/workspace-SWYYresearcher/reports/biomed-weekly/`，文件名格式 `生物医药行业周报-YYYYMMDD.docx`（与 wiki 节点标题一致；实际日期格式为 yyyyMMdd）；生成后必须上传飞书 Drive 获取下载链接；**上传前检查 Drive 中同名旧文件并删除，确保只保留最新版本**；**向用户输出时只提供飞书 Drive 下载链接，禁止输出本地文件路径**；Word 正文必须清理 Markdown 标记，推荐产品组合不用表格。
14. **正文来源格式**：周报正文去掉媒体/网站来源括注；不要出现"（日期，来源）""（来源：XXX）"。资料来源只在报告开头或文末统一概括。
15. **iFinD 公告检索必须执行**：不可跳过。先在循环外做一次快速探测确认环境可用，再执行 2 个 `search_notice` 查询；不要调用无权限的 `search_trending_news`。
16. **所有飞书 API 统一走 lark-cli**：sheets/drive/docs/wiki 操作全部用 lark-cli，不用 Python urllib 直接调 API（HTTPS_PROXY 代理会导致 SSL 证书验证失败）。
17. **lark-cli 本地文件路径**：`drive +upload --file` 和 `docs +update --content @./file` 都优先使用当前工作目录下的相对路径。操作前先 `cd` 到文件所在目录，使用 `./文件名` 或 `@./文件名`，不要传绝对路径。
18. **lark-cli wiki 创建后需检查位置**：`wiki +node-create` 默认可能放在「首页」子节点下，创建后需检查 `parent_node_token`，如在子节点下需 `wiki +move` 移回根目录。所有收尾命令都必须用 `LARK="$HOME/.npm-global/bin/lark-cli"` 绝对路径，并先完成验证再输出最终摘要。

## 踩坑记录（供后续优化参考）

### 已踩过的坑

1. **Brave 不支持布尔 OR 语法**：`"A" OR "B"` 被当精确匹配，返回大量无关结果。→ 改用 searxng，或 Brave 用空格分隔关键词。
2. **同花顺/经济观察网返回内容极少**：10jqka 返回 <600字符，eeo.com.cn 仅150字符且无关。→ 已从必抓源移除。
3. **米内网/丁香园内容质量差**：menet.com.cn 返回空白，dxy.cn 内容混杂且需要登录。→ 已从垂直源移除。
4. **Brave 多轮搜索 3/5 轮返回空结果**：中文工业术语索引覆盖率有限 + OR 语法问题。→ 优先 searxng。
5. **iFinD 被跳过未执行**：未先做环境探测就跳过。→ 必须先探测再执行。
6. **Python urllib SSL 证书验证失败**：HTTPS_PROXY 代理导致 `self-signed certificate in certificate chain`。→ 全部改用 lark-cli。
7. **lark-cli 上传文件要求相对路径**：绝对路径直接报错。→ 先 `cd` 到目录再用 `./文件名`。
8. **wiki 创建后自动嵌套在「首页」下**：飞书 API 默认把新节点挂在「首页」节点下，**不是根目录**。→ 创建后必须用脚本模板检查 `parent_node_token`，如不为空立即 `wiki +move --target-space-id <space>` 移回根目录。**不要传 `--parent-node-token ""`**（无效）。
9. **lark-cli 子命令语法不统一**：每个子命令 flag 风格不一致，需反复 `--help`。→ 在 skill 中预定义完整命令。
10. **Word 下载链接格式**：`https://<租户域名>.feishu.cn/file/<file_token>`，上传文件后拼接。**向用户输出时只放此链接，禁止出现本地文件路径。**
11. **未并行执行搜索**：skill 说"并行执行"但实际串行。→ searxng 支持并行，Brave 需串行。
12. **2026-05-21 复盘：证券时报旧快讯 404**：`https://www.stcn.com/article/newsflash.html` 已失效；替代 `https://news.stcn.com/` 内容陈旧，不适合周报。→ 已从必抓源移除，不再抓取。
13. **2026-05-21 复盘：Brave 并行触发 429**：并行调用 web_search 会触发免费套餐限流。→ 只允许 searxng 并行；Brave 兜底必须串行且间隔 ≥1 秒。
14. **2026-05-21 复盘：iFinD 热点接口无权限**：`search_trending_news` 返回 403。→ 固定流程只保留 `search_notice` 两个公告查询，热点接口不再调用。
15. **2026-05-21 复盘：docs +update 绝对路径失败**：`--content @/Users/...` 会被拒。→ 先 `cd` 到目录，用 `--api-version v2 --command overwrite --doc-format markdown --content @./wiki_YYYYMMDD.md`。
16. **2026-05-21 复盘：飞书 wiki 单换行黏连**：连续单换行会把字段挤到一行。→ wiki md 写入前每个非空行后加空行；写入后 `docs +fetch`，按行检查 `推荐等级.*所属行业` 等模式。
17. **2026-05-21 复盘：商机表同企不同名重复**：如 `浙江拱东医疗` vs `浙江拱东医疗器械股份有限公司`。→ 去重 key 必须去括号、去公司后缀、过别名映射，再精确匹配。
18. **2026-05-21 复盘：表格空行残留**：删除维度后仍可能看到空白行。→ 先覆盖空值，再删除多余行，最后用 `sheets +info` 验证 `row_count`。
19. **2026-05-21 复盘：链接域名混用**：wiki 输出不要用 `www.feishu.cn`。→ 统一用租户域名 `https://<租户域名>.feishu.cn/wiki/<node_token>`。
20. **2026-05-21 复盘：searxng 本地查询会返回无关结果**：浙江本地检索可能混入展会、招标、博彩/钢铁等无关页，或某些 query 结果极少。→ searxng 结果必须落盘后抽样标题/摘要；本地企业线索不足时，用 Brave 串行补充精准查询（企业名 + 2026 一季报/公告/融资/扩产），但不要并行。
21. **2026-05-21 复盘：iFinD `ok:true` 不代表有有效公告**：环境探测可能成功，但正式 `search_notice` 返回“查询结果为空”。→ 执行并检查 `ok` 与正文内容；为空只记执行日志，不写入周报/wiki/群聊摘要；用上市公司公告、年报/一季报和公开报道补足企业信号。
22. **2026-05-21 复盘：必抓源不等于有效信息源**：财联社、36氪快讯可能与生物医药弱相关；医药魔方首页可能只抓到产品介绍。→ 必抓源仍按流程抓取，但资料来源只列实际采用的信息源；无效抓取状态、空白、报错不要进入正文。
23. **2026-05-21 复盘：同名 wiki 节点已存在时不要重复创建**：如已存在 `生物医药行业周报-YYYYMMDD`，新建会造成重复存档。→ 先 `wiki nodes list` 全量查重；存在同名节点则使用其 `obj_token` 执行 `docs +update --api-version v2 --command overwrite --doc-format markdown --content @./wiki_YYYYMMDD.md`，不存在才创建新节点。
24. **2026-05-21 复盘：Drive 上传成功但可能没有当前用户管理权限**：bot 上传 Word 后 lark-cli 可能提示未给当前 CLI 用户 `full_access`，但 `file_token` 和下载链接可用。→ 不因该 warning 中断流程；如 Joe 后续打不开，再单独处理权限授权。
25. **2026-05-21 复盘：zsh 空 glob 会失败**：`rm -f reports/summary/*` 在目录为空时会触发 `zsh: no matches found`。→ 清理目录用 `find reports/summary -type f -delete`，不要用未匹配的通配符。
26. **2026-05-22 复盘：iFinD 调用签名再次写错**：`call-node.js` 不是 `call('search_notice', params)`，而是 `call('news','search_notice', params)`。→ 第五轮固定复制 iFinD 模板，不要手写调用签名。
27. **2026-05-22 复盘：wiki 黏连检查误报**：`docs +fetch` 可能输出字面量 `\n`，全文正则 `推荐等级.*所属行业` 会把转义换行后的多行误判成同一行。→ 检查前先 `text.replace('\\n','\n')`，再逐行匹配；只在同一真实行命中时才判定黏连。
28. **2026-05-22 复盘：已有经验没有转成强制模板会重复踩坑**：仅写“注意/经验”不够。→ 对 iFinD、wiki 验证、商机表清理这类脆弱步骤，必须在流程正文提供可复制命令模板，并在执行时优先复制模板而非临场重写。
29. **2026-05-23 复盘：Brave 对中文地域/工业术语索引极差**：`web_search("生物医药 浙江 杭州 宁波 产业 2026", freshness="week")` 返回10条中8条不相关（B站视频、社保缴费、摩托车、长鑫半导体等）。→ Brave 补充搜索应使用更精准的关键词组合（如具体企业名+融资/公告/一季报），不要用宽泛的地域+行业组合搜索；优先依赖 searxng 和必抓源。
30. **2026-05-23 复盘：lark-cli proxy warning 混入输出**：所有 lark-cli 命令 stderr 输出 `[lark-cli] [WARN] proxy detected: HTTPS_PROXY=...`，`| python3` 管道会 JSONDecodeError。→ lark-cli 输出必须先写文件，再用 Python 跳过 warning 行找到 `{` 开头解析，不能直接管道。
31. **2026-05-25 复盘：Word 与 Wiki 同名一致 + Drive 同名覆盖**：Word 文件名和 wiki 节点标题统一为 `生物医药行业周报-YYYYMMDD`。Drive 不会自动覆盖同名文件，上传前必须先 `drive +list` 查找同名旧文件并 `drive +delete`，再上传新版本。
32. **2026-06-05 复盘：周报摘要已发但 cron 仍失败**：原因是 agent 在最后命令成功收口前先把摘要推到群，随后某条 `export BOT_PROFILE=... WIKI_SPACE_ID=... NODE_TOKEN=... OBJ_TOKEN=...` 收尾命令失败，cron 最终判定 error 并推送失败告警。→ 修复为：定时任务内禁止手动 `message` 推群；必须先完成 Word/Wiki/表格全部验证，最终 assistant 回复只输出第十步摘要，由 cron delivery 投递。
33. **2026-06-26 复盘：产物已生成但 cron 最后失败**：最后排查命令写成 `set -e BASE="$PWD/reports/biomed-weekly/tmp_20260626" LARK=...`，`BASE` 未真正赋值，后续 `cat "$BASE/final_links_20260626.env"` 读错路径，cron 判定 agent failed 并向群聊投递失败告警。→ 修复为：所有收尾 shell 用 `set -e; BASE="..."; LARK="...";` 或多行赋值；最终输出前不要再运行临时拼接的验收命令，必须先用独立命令确认链接文件存在且三项链接齐全。

## 文件路径

```
skills/swyy-weekly-report/
├── SKILL.md                    # 本文件
└── references/
    └── (预留)
```

## 关键参数速查

```
# lark-cli profile
BOT_PROFILE: "swyy_bot"

# 商机挖掘表格
spreadsheet_token: AQjXsU9DehPYPEtDlZbcYY6Wnsf
sheet_id: cfde3f
去重查询: cfde3f!A:A（只查客户名称列）
追加写入: cfde3f!A:J

# 生物医药行研知识库
space_id: 7637083944097270734
space_name: 生物医药行研
节点标题: 生物医药行业周报-YYYYMMDD
```
