---
name: ne-weekly-report
description: |
  生成新能源行业研究周报（聚焦浙江），每周爬取多源行业研究内容，去重筛选、
  转化为银行商机清单，推送至飞书群。每周五执行，商机/行动清单/企业动态仅限浙江本地。
---

# 新能源行业研究周报生成 Skill

每周直接爬取多源行业研究内容，生成周报（动态 + 商机），推送至飞书群。

## 复用说明

本 skill 可复用于其他机器人。复用时需要修改「关键参数速查」章节中的值，
**其他内容（研究方法论、抓取流程、报告模板、写入逻辑）保持不变**。

### 每个 agent 需要修改的参数

| 参数 | 说明 | 如何获取 |
|------|------|----------|
| `BOT_PROFILE` | lark-cli profile 名称（对应 agent 自己的 bot） | `lark-cli config init --name <bot_name> --app-id <app_id>` 创建 |
| `WIKI_SPACE_ID` | 飞书知识库 space_id | `lark-cli wiki spaces list` |
| `WIKI_SPACE_NAME` | 知识库名称（用于去重搜索） | 从 wiki spaces list 确认 |
| `SPREADSHEET_TOKEN` | 商机挖掘表格的 spreadsheet_token | 从飞书表格 URL 提取 |
| `SHEET_ID` | 商机挖掘表格的 sheet_id | 从飞书表格 URL 提取 |
| `REGION` | 地域聚焦（如「浙江」「江苏」「广东」） | 根据 agent 定位 |
| `REGION_CITIES` | 地域下属城市列表 | 根据 agent 定位 |
| `WEEKLY_TITLE_PREFIX` | 周报文档标题前缀（如 `ne-weekly`） | 自定义 |

### 配置示例（在 agent 的 SKILL.md 同级创建 `config.json`）

```json
{
  "bot_profile": "ne_bot",
  "wiki_space_id": "7637082931059706850",
  "wiki_space_name": "新能源行研",
  "spreadsheet_token": "C5ZgwhqJciryiTkGLH0cvlXzn5b",
  "sheet_id": "f2ad53",
  "region": "浙江",
  "region_cities": ["杭州","宁波","温州","绍兴","嘉兴","湖州","金华","台州","丽水","衢州","舟山"],
  "weekly_title_prefix": "ne-weekly"
}
```

### 使用方式

执行周报生成前，先读取同级 `config.json`（如有）并覆盖参数；如无则使用默认值。
命令中统一使用 `--profile $BOT_PROFILE --as bot`。

## 何时使用

- 用户说"生成周报"、"出周报"、"新能源周报"、"行业周报"
- 定时任务触发（每周五下午 5 点）
- 补发历史周报

## 核心原则

1. **直接爬取**：每周从多源爬取行业研究内容（行业报告、市场分析、技术趋势、政策动态）
2. **地域聚焦**：**商机地图、行动清单、企业动态仅限目标区域**（如浙江：杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山）；长三角异动作为补充参考
3. **TOP5-8精选**：本周最具实质影响的5-8条事件
4. **商机汇总**：按产品维度汇总本周可介入的商机
5. **单篇控制在2000字以内**
6. **独立运行**：周报由本 skill 独立负责

**研究方向：新能源全产业链**（光伏、风电、储能、氢能、动力电池、新能源汽车、充电桩/换电站、电网及特高压、综合能源服务、碳交易/绿证等）

## Token 优化原则

- **web_search 优先**：用关键词精准搜索新能源行业信息，比爬取大站再筛选高效得多
- **web_fetch 用 text 模式**（`extractMode: "text"`），比 markdown 模式更精简
- **maxChars=6000**，够提取文章摘要，不需要更大
- **表格只查 A 列**去重，不查全表
- **lark-cli 命令按预定义参数执行**，不要反复试错
- **正文点入按需**：只在搜索结果发现重要线索时点入正文（maxChars=4000）

## 工作流

### 第一步：信息抓取（必抓源 + 搜索为主 + 垂直源补充）

**必抓源（4个，不可跳过）：**

```
1. 同花顺首页 → web_fetch https://www.10jqka.com.cn/ (extractMode="text", maxChars=6000)
2. 财联社电报 → web_fetch https://www.cls.cn/telegraph (extractMode="text", maxChars=6000)
3. 新华网科技 → web_fetch https://www.xinhuanet.com/tech/ (extractMode="text", maxChars=6000)
4. 经济观察网 → web_fetch https://www.eeo.com.cn/ (extractMode="text", maxChars=6000)
```

**核心策略：必抓源打底，web_search 精准搜索补充，垂直源进一步补充。**

**第二轮：web_search 精准搜索（5个查询，并行执行）：**

```
1. "光伏" OR "太阳能" OR "硅料" OR "光伏组件" → web_search（近7天，count=10）
2. "风电" OR "海上风电" OR "风机" OR "风场" → web_search（近7天，count=10）
3. "储能" OR "锂电" OR "钠电池" OR "户储" OR "大储" → web_search（近7天，count=10）
4. "氢能" OR "燃料电池" OR "电解槽" OR "绿氢" → web_search（近7天，count=10）
5. "新能源融资" OR "新能源上市" OR "新能源政策" OR "新能源汽车" → web_search（近7天，count=10）
```

**第三轮：新能源垂直源补充（并行，4个）：**

```
6. 北极星太阳能光伏网 → web_fetch https://guangfu.bjx.com.cn/ (extractMode="text", maxChars=6000)
7. 储能科学与技术 / 储能头条 → web_fetch https://www.escn.com.cn/ (extractMode="text", maxChars=6000)
8. 高工锂电 GGII → web_fetch https://www.gg-lb.com/ (extractMode="text", maxChars=6000)
9. 风电网 → web_fetch https://www.chinawind.com.cn/ (extractMode="text", maxChars=6000)
```

**第四轮：本地新能源专项搜索（1个）：**

```
10. "新能源 [地域名]" OR "光伏 [核心城市]" OR "储能 [另一城市]" OR "风电 [地域名]" → web_search（近7天，count=10）
```

**按需补充：**
- 从搜索结果中发现重要文章时，点入正文抓取（web_fetch, extractMode="text", maxChars=4000）
- 如需更全面的市场/财经视角，可补充搜索："新能源 行业 周报" OR "光伏 产业 趋势" OR "储能 市场 分析"（count=5）

**抓取规则：**
- 必抓源不可跳过，即使返回空白/JS 渲染失败也要记录并继续
- web_search + 垂直源并行执行
- 如果 web_fetch 返回空白/JS 渲染失败，跳过该源，不要重试
- 关注 **近 7 天内** 发生的事件（周报覆盖一周范围）
- 关注目标区域及周边地区的新能源企业动态优先

### 第二步：筛选与分类

从抓取的信息中筛选出符合以下标准的条目：

**入选标准（满足任一即可）：**
- 政策发布/修订（影响资金流向或授信风险）
- 企业融资/上市/定增公告
- 产能建设/项目开工/电站并网/产线投产
- 订单/中标/框架协议公告
- 技术突破/产品发布（新电池技术、大兆瓦风机、新型储能等）
- 价格变动（硅料/硅片/电池片/组件、碳酸锂/电芯、风机投标价等，影响产业链成本）
- 风险信号（订单下修、减持、诉讼、产能过剩预警等）

**排除标准：**
- 行业常识科普
- 长期趋势分析（无具体事件）
- 与新能源行业（光伏、风电、储能、氢能、动力电池、新能源汽车、充电桩等）无关的内容
- 纯股市行情分析（无产业事件支撑）

**地域标签：**
- `[<地域>]` / `[<核心城市>]` / ... 等
- 周边省份/区域标签
- `[其他]` / `[全球]`

**重要性评级：**
- ★★★★★：国家级政策 / 百亿级投资 / 行业拐点
- ★★★★：省级政策 / 十亿级融资 / 重大订单
- ★★★：企业级公告 / 产能变动 / 价格变动
- ★★：一般动态
- ★：值得关注但影响有限

### 第三步：筛选 TOP5-8 要闻

从近 7 天事件中筛选出 TOP5-8 条最具实质影响的要闻：

**筛选标准（按权重排序）：**
1. 国家级政策/百亿级投资（★★★★★）
2. 省级政策/十亿级融资/重大订单（★★★★）
3. 产能变动/价格变动/重大产品发布（★★★）

**排除：**
- 已标注 status=closed 且无后续影响的事件
- 重要性 ≤2 的一般动态
- 纯股市行情（无产业事件支撑）

### 第四步：区域地市动态

按目标区域下属地市汇总近 7 天关键变化：

```
[<城市A>] 融资X起，产能X条，政策X项
[<城市B>] ...
[<城市C>] ...
```

（**仅展示有实际动态的城市**，无事件的城市直接省略，不显示「暂无」；如全部城市无动态则标注"本周暂无重大区域事件"）

**标注关键节点：**
- 项目开工/电站并网/产线投产
- 政策细则落地
- 企业融资/上市
- 订单/中标/框架协议

### 第五步：区域企业动态

从事件日志中提取所有目标区域标签的事件，按企业整理：

```
企业 | 事件 | 资金需求/业务机会 | 优先级
XX新能源（<城市>）| IPO受理 | 8亿募资专户 | P0
XX储能（<城市>）| 项目公告 | 项目融资 | P1
XX光伏（<城市>）| 中标大单 | 订单融资 | P1
```

### 第六步：区域商机地图（按产品维度）

将近 7 天目标区域本地商机按银行产品归类：

```
产品维度：
- 募集资金监管：X家企业，预计X亿
- 项目融资/固定资产贷款：X家企业，预计X亿
- 订单融资/保理：X家企业，预计X亿
- 流贷追加：X家企业，预计X亿
- 绿色信贷/碳减排支持工具：X家企业，预计X亿
- 供应链金融：X家企业，预计X亿
- 汇率锁汇（出口型新能源企业）：X家企业，预计X亿
```

### 第七步：区域行动清单

按分类输出具体行动（仅限目标区域企业）：

```
必访X家 | 储备X家 | 预警X条

必访：
• [浙江客户名]：[拜访理由+话题]
• ...

储备：
• [浙江客户名]：[储备理由+产品]
• ...

预警：
• [风险信号]：[应对措施]
• ...
```

### 第八步：更新/追加商机到表格

周报中的商机数据写入「商机挖掘」电子表格。

**🔴 关键规则（必须严格遵守）：**
- **只写入「必访」名单中的企业**，「储备」类企业不写入表格，「预警」类不写入表格
- **只写入目标区域本地企业**，非目标区域企业一律不写入表格
- **写入前必须去重**：先读取 A 列，用「规范化核心简称精确匹配」判断是否已存在
- **禁止重复写入同一企业**：同一核心简称只保留一行，已有行则更新，无则追加

**去重逻辑（严格执行）：**

⚠️ **第一步：规范化核心简称提取（关键！）**
1. 先将括号统一为全角：`(` → `（`, `)` → `）`
2. 然后去掉所有 `（...）` 修饰（地域、股票代码、备注等），得到**核心简称**

⚠️ **第二步：对已有 A 列的每一行也做同样的规范化**
对 A 列每个已有名称，同样去掉 `（...）` 得到已有核心简称。

⚠️ **第三步：精确匹配核心简称**
将新商机的核心简称与已有行的核心简称做**完全匹配**（==），不是包含匹配。
- 如果核心简称相同 → **原地更新该行**，**保持A列原名称不变**，只更新 B~J 列
- 如果没有任何已有行的核心简称匹配 → **追加新行**

⚠️ **严禁**：
- 更新行时修改A列客户名称（包括加后缀、改格式等），必须保持原名称不变
- 用包含匹配（如"光伏"匹配到"光伏科技"），必须用核心简称完全匹配

**写入流程（严格执行）：**
1. 读取 A 列全量数据
2. 对 A 列每个非空名称做规范化：去掉括号内容，得到**已有核心简称列表**
3. 对本次商机先去重：按核心简称合并同名企业，每个核心简称只保留一条
4. 对每个去重后的商机：提取核心简称 → 精确匹配 → 匹配到则更新，未匹配则追加
5. ⚠️ **更新已有商机时，创建日期（I列）必须更新为当前日期（YYYY-MM-DD）**
6. ⚠️ **如果匹配到的已有行状态为终态（closed/已关闭/已落地），则跳过该行，不更新**
7. ⚠️ **新增商机的状态列统一填写「待联系」，不要写 active/open**
8. ⚠️ **更新已有商机时，状态列保持不变，不修改**
9. ⚠️ **写入完成后，必须对整个表格进行时间倒序重排 + 清理残留空行**（见下方「表格排序与清理」）

**字段顺序**：客户名称、行业/领域、触发信号、优先级、推荐方案、预计金额、联系人、状态、创建日期、备注

**⚠️ 表格排序与清理（每次写入后必须执行）：**

使用 Python 脚本完全读取表格数据、按日期倒序排序、写回并清理残留行：
```python
import json, subprocess, urllib.request, urllib.error

SPREADSHEET_TOKEN = "C5ZgwhqJciryiTkGLH0cvlXzn5b"
SHEET_ID = "f2ad53"
APP_ID = "cli_a97152fac6b81bd4"
APP_SECRET = subprocess.run(
    ['bash', '-c', 'jq -r \'.channels.feishu.accounts.ne_bot.appSecret\' ~/.openclaw/openclaw.json'],
    capture_output=True, text=True
).stdout.strip()

def get_tenant_token():
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp["tenant_access_token"]

def api_call(token, method, path, body=None):
    url = f"https://open.feishu.cn{path}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp

# 1. 获取 token 并读取全表
token = get_tenant_token()
resp = api_call(token, "GET", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A1:J100")
rows = resp["data"]["valueRange"]["values"]

header = rows[0]
data_rows = [r for r in rows[1:] if len(r) > 0 and r[0] and r[0].strip()]

# 2. 按日期列（index 8）倒序排列（最新在前）
data_rows.sort(key=lambda x: x[8] if len(x) > 8 and x[8] else '', reverse=True)

# 3. 写入排序后的数据
end_row = 1 + len(data_rows)
api_call(token, "PUT", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A2:J{end_row}", {
    "valueRange": {"values": data_rows}
})

# 4. 清理 end_row+1 之后的残留空行
api_call(token, "POST", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/sheets/{SHEET_ID}/dimensionRanges/delete", {
    "ranges": [{"dimension": "ROWS", "startIndex": end_row, "endIndex": 200}]
})
```

⚠️ **关键说明：**
- 使用当前 bot 的 tenant_access_token 直接调 Sheets API，不依赖 lark-cli 配置
- 排序后必须删除 end_row 之后的所有行，否则会残留空行和旧数据
- 如果之前写入范围小于实际数据量（如写了 A2:J26 但旧数据在 52-53 行），中间会留下大量空行，必须删除

### 第九步：生成周报

使用以下模板（飞书群聊优化版，**禁止使用** `━` 分隔线）：

**⚠️ 标题中的「浙江」需替换为实际地域名，企业动态中的城市需替换为实际城市。**

```
📌 新能源行业周报·<地域> | YYYY.MM.DD-MM.DD（近7天）

━━━━━━━━━━━━━━━━━━━━━
📈 浙江新能源脉搏（TOP5-8要闻）
━━━━━━━━━━━━━━━━━━━━━

1. 事件一句话 | 影响★★★★★ | X月X日
2. 事件一句话 | 影响★★★★ | X月X日
3. 事件一句话 | 影响★★★★ | X月X日
4. 事件一句话 | 影响★★★ | X月X日
5. 事件一句话 | 影响★★★ | X月X日

━━━━━━━━━━━━━━━━━━━━━
🗺️ 浙江地市动态
━━━━━━━━━━━━━━━━━━━━━

[杭州]
- XX公司签约XGW光伏组件项目（X月X日）
- XX储能项目并网发电（X月X日）

[宁波]
- XX企业获X亿融资用于氢能产线（X月X日）

[绍兴]
- ...

━━━━━━━━━━━━━━━━━━━━━
📊 浙江企业动态
━━━━━━━━━━━━━━━━━━━━━

【XX新能源】（杭州）
事件：IPO受理 | 机会：8亿募资专户 | 优先级：P0

【XX储能】（宁波）
事件：项目中标 | 机会：项目融资 | 优先级：P1

【XX光伏】（绍兴）
事件：产能扩张 | 机会：固贷追加 | 优先级：P1

━━━━━━━━━━━━━━━━━━━━━
💰 浙江商机地图（按产品）
━━━━━━━━━━━━━━━━━━━━━

- 募集资金监管：X家企业，预计X亿
- 项目融资/固贷：X家企业，预计X亿
- 订单融资/保理：X家企业，预计X亿
- 流贷追加：X家企业，预计X亿
- 绿色信贷/碳减排支持工具：X家企业，预计X亿
- 供应链金融：X家企业，预计X亿
- 汇率锁汇（出口型企业）：X家企业，预计X亿

━━━━━━━━━━━━━━━━━━━━━
📋 浙江行动清单
━━━━━━━━━━━━━━━━━━━━━

🔴 必访X家

**[P0] XX新能源（杭州）**
- 企业概况：行业地位 + 核心业务
- 拜访原因：具体事件/信号（附数据）
- 拜访话题：① 具体话题1 ② 具体话题2 ③ 具体话题3

**[P0] XX储能（宁波）**
- 企业概况：...
- 拜访原因：...
- 拜访话题：...

🟡 储备X家

- XX光伏（绍兴）：15亿融资到账，专户设立+流贷储备
- XX氢能（杭州）：电解槽订单落地，关注项目融资需求

⚠️ 预警X条

- 硅料/组件价格持续下行→光伏制造企业利润承压
- 储能电芯产能过剩→价格战加剧，关注企业现金流风险

━━━━━━━━━━━━━━━━━━━━━
📅 本周关注
━━━━━━━━━━━━━━━━━━━━━

- 今日/本周重大会议/发布会/政策生效日
- 从财联社事件日历中提取新能源相关事项
```

**格式要点：**
- 企业动态用 `【企业名】（城市）` + 事件/机会/优先级单行格式，**不用表格**（飞书群聊不支持 markdown 表格渲染）
- 行动清单用 🔴🟡⚠️ emoji 区分优先级
- 地市动态按城市分块，每块内用 `- `（横杠+空格）无序列表，**禁止用 `•`**
- 要闻用 `|` 分隔事件、影响星级、日期，不用 `→` 箭头
- **每个区块之间必须保留一个空行**，确保飞书群聊正确换行；`- ` 列表项之间也要保留空行
- **分隔线上下各留一个空行**，不要和文字粘连
- 全文**不使用** `━` 作为装饰线，只用 `━━━━━━━━━━━━━━━━━━━━━` 作为大区块分隔
- **⚠️ 区块标题格式（严格执行）**：分隔线与标题之间必须有且仅有一个空行，标题与下方分隔线之间也有且仅有一个空行，必须呈现为3行。例如：
```
━━━━━━━━━━━━━━━━━━━━━
📅 本周关注
━━━━━━━━━━━━━━━━━━━━━
```
**绝对禁止**将分隔线与标题写在同一行（如 `━━━ 📅 本周关注 ━━━`），飞书会将无空行分隔的相邻行合并为一行。

### 第十步：写入知识库

**重要：每次生成都覆盖当前同名文件（ne-weekly-YYYYMMDD），不要有重复日期的文档。**

**🔴 关键规则（必须严格遵守）：**
- 文档必须创建在知识库**根目录**（`parent_node_token` 为空字符串），**不能**创建在「首页」或其他节点下面
- 必须使用**机器人身份**（`--as bot`）创建，创建者显示为机器人
- **⚠️ `--as bot` 默认使用 lark-cli 配置的默认应用（通常是 ai_bot），不是当前 agent 自己的 bot。必须使用 `--profile $BOT_PROFILE --as bot`**

**步骤：**

1. **列出知识库所有节点，查找是否已有同名文档（搜索全部节点，不限根目录！）**：
   ```bash
   lark-cli wiki nodes list --params '{"space_id":"$WIKI_SPACE_ID","page_size":50}' --profile $BOT_PROFILE
   ```
   从返回结果中搜索 title 为 `$WEEKLY_TITLE_PREFIX-YYYYMMDD` 的节点，提取 `obj_token` 和 `node_token`。
   ⚠️ **必须搜索所有节点**（不限 `parent_node_token`），否则第一次创建时可能被放在「首页」下，第二次搜不到就重复创建了！
   ⚠️ **如果找到多个同名文档**，选 `obj_edit_time` 最新的那个，用 `docs +update` 覆盖；其余用 `drive files +patch --type docx --file-token <obj_token> --body '{"trash_type":"doc_trash"}'` 删除。

2. **如果找到同名文档**：
   - 使用 `lark-cli docs +update --doc <obj_token> --profile $BOT_PROFILE --as bot --mode overwrite --markdown '<内容>'` 覆盖内容
   - 输出文档链接：`https://www.feishu.cn/wiki/<node_token>`

3. **如果未找到同名文档**：
   - 使用以下命令以**机器人身份**创建（注意必须带 profile）：
     ```bash
     lark-cli wiki +node-create --profile $BOT_PROFILE --as bot \
       --space-id "$WIKI_SPACE_ID" \
       --title "$WEEKLY_TITLE_PREFIX-YYYYMMDD" \
       --obj-type "docx"
     ```
   - 从返回结果提取 `obj_token`（用于内容更新）和 `node_token`（用于 URL）
   - 使用 `lark-cli docs +update --doc <obj_token> --profile $BOT_PROFILE --as bot --mode overwrite --markdown '<内容>'` 写入内容
   - 输出文档链接：`https://www.feishu.cn/wiki/<node_token>`
   - ⚠️ 创建后用 `wiki nodes list` 确认 `parent_node_token`，如果不在根目录，用 `wiki +move --profile $BOT_PROFILE --as bot --node-token <node_token> --target-space-id "$WIKI_SPACE_ID"` 移回根目录。

**禁止**使用 `feishu_wiki_space_node` 工具（该工具可能将文档创建在首页下），必须使用 `lark-cli wiki +node-create --profile $BOT_PROFILE --as bot --space-id` 命令。

### 第十一步：推送至群聊（概要 + 链接）

**🔴 关键规则：推送到群聊的内容是概要和链接，不是全文！**

推送至群聊的消息格式如下：

```markdown
📌 **新能源行业周报·<地域> | YYYY.MM.DD-MM.DD（近7天）**

🔥 TOP5 要闻：
1. [事件一句话]
2. [事件一句话]
3. [事件一句话]
4. [事件一句话]
5. [事件一句话]

🗺️ 浙江地市：杭州 X 条 | 宁波 X 条 | 绍兴 X 条 ...
💰 商机：必访 X 家 | 储备 X 家 | 预警 X 条

📄 周报全文：<https://www.feishu.cn/wiki/XXXX>
📊 商机表格：<https://xxx.feishu.cn/sheets/XXXX>
```

**推送内容要求：**
- 只输出 TOP5-8 要闻标题（一句话）
- 区域地市动态概览
- 商机汇总数字（必访/储备/预警数量）
- 周报文档链接（wiki URL）
- 商机挖掘表格链接（sheets URL）
- **不要**输出周报全文内容

### 第十二步：输出完成

输出完成后，由调用方（定时任务等）通过 delivery 配置推送到飞书群，无需在 skill 内执行推送。

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
2. **地域限制**：商机地图、行动清单、企业动态仅限目标区域本地企业
3. **禁止推荐不合规业务**
4. **Markdown 格式**：使用 Markdown 格式输出
5. **知识库标题**：ne-weekly-YYYYMMDD
6. **知识库写入**：必须使用 `lark-cli wiki +node-create --profile $BOT_PROFILE --as bot --space-id $WIKI_SPACE_ID` 创建，禁止使用 `feishu_wiki_space_node` 工具。去重时**搜索全部节点**（不限 parent_node_token），避免重复创建
7. **群聊推送**：推送概要 + 链接，不是全文
8. **商机挖掘表格**：写入前必须去重，只写目标区域本地企业。更新已有商机时日期必须更新为当天。写入后必须按时间倒序重排并清理残留空行
9. **⚠️ 表格写入用当前 bot 的 tenant_access_token 直接调 API**：lark-cli 默认配置的是 ai_bot，`--as bot` 会报 `91403 Forbidden`。正确做法：用 lark-cli profile（`--profile $BOT_PROFILE --as bot`）或直接通过 appId/appSecret 获取 tenant_access_token，调 Sheets API 写入。每个 agent 对应自己的 bot，不要混用。
10. **web_search 限流**：Brave 免费套餐限流 1 次/秒，多轮搜索需串行执行或混用 SearXNG skill（`SEARXNG_URL=http://localhost:8080 python3 ~/.openclaw/skills/searxng/scripts/searxng.py search "query" -n 10 --format json`）
11. **代理配置**：Gateway 进程需配置代理环境变量（`HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:7890`），否则 Brave API 连接超时。lark-cli 会检测到代理变量并发出警告，不影响功能

## 文件路径

```
skills/ne-weekly-report/
├── SKILL.md                    # 本文件
└── references/
    └── (预留)
```

## 关键参数速查

**⚠️ 以下为当前 agent（NE Researcher）的参数。其他 agent 复用时需要替换为自己的值。**

```bash
# lark-cli profile（必须为当前 agent 自己的 bot 创建）
BOT_PROFILE: "ne_bot"

# 商机挖掘表格
SPREADSHEET_TOKEN: "C5ZgwhqJciryiTkGLH0cvlXzn5b"
SHEET_ID: "f2ad53"
去重查询: f2ad53!A:A（只查客户名称列）
追加写入: f2ad53!A:J

# 知识库
WIKI_SPACE_ID: "7637082931059706850"
WIKI_SPACE_NAME: "新能源行研"
WEEKLY_TITLE_PREFIX: "ne-weekly"
节点标题: ne-weekly-YYYYMMDD

# 地域
REGION: "浙江"
REGION_CITIES: ["杭州","宁波","温州","绍兴","嘉兴","湖州","金华","台州","丽水","衢州","舟山"]
```

### 其他 agent 复用步骤

1. 为当前 agent 的 bot 创建 lark-cli profile：
   ```bash
   echo -n "$APP_SECRET" | lark-cli config init --app-id "$APP_ID" --brand feishu --name <bot_name> --app-secret-stdin
   ```
2. 将该 bot 添加为知识库管理员：
   ```bash
   lark-cli wiki members create --as user --params '{"space_id":"$WIKI_SPACE_ID"}' --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
   ```
3. 创建或获取商机挖掘表格，记录 `spreadsheet_token` 和 `sheet_id`
4. 修改本 SKILL.md 中的参数（或创建同级 `config.json`）
5. 在 cron 定时任务中设置 `BOT_PROFILE` 环境变量或写入配置文件
