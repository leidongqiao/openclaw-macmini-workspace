---
name: bdt-weekly-report
description: |
 生成半导体行业研究周报(双版本:Word详细报告 + 飞书wiki,聚焦浙江),每14天爬取近14天多源行业研究内容,去重筛选、
 转化为银行商机清单,推送至飞书群。每两周周五执行,商机/行动清单/企业动态仅限浙江本地。
---

# 半导体行业研究周报生成 Skill

每14天直接爬取近14天多源半导体行业研究内容,生成双版本周报(Word详细报告 + 飞书 wiki 知识库存档),推送至飞书群。

## 复用说明

本 skill 可复用于其他机器人。复用时需要修改「关键参数速查」章节中的值,**抓取流程、报告模板、表格写入逻辑、知识库写入逻辑按本文件执行**。

执行周报生成前,先读取同级 `config.json`(如有)并覆盖参数;如无则使用默认值。命令中统一使用 `--profile $BOT_PROFILE --as bot`。

⚠️ **已知坑:`config.json` 可能不存在。** 如果同级 `config.json` 不存在,不要中断任务;直接使用本 skill 默认参数,并在执行日志中记录"未找到配置,使用默认值"。

### 配置示例(在本 SKILL.md 同级创建 `config.json`)

```json
{
  "bot_profile": "bdt_bot",
  "wiki_space_id": "7637077749416610770",
  "wiki_space_name": "半导体行研",
  "spreadsheet_token": "RpI5svn81hl9axtuaqUcwtAenBM",
  "sheet_id": "89c832",
  "region": "浙江",
  "region_cities": ["杭州","宁波","温州","绍兴","嘉兴","湖州","金华","台州","丽水","衢州","舟山"],
  "weekly_title_prefix": "半导体行业周报"
}
```

### lark-cli 路径解析(必须执行)

cron / OpenClaw 非交互 shell 可能不会加载用户终端 PATH,导致本地已安装的 `lark-cli` 报 `command not found`。所有飞书 CLI 命令执行前必须先解析 CLI 路径:

```bash
if command -v lark-cli >/dev/null 2>&1; then
  LARK_CLI="$(command -v lark-cli)"
elif [ -x "$HOME/.npm-global/bin/lark-cli" ]; then
  LARK_CLI="$HOME/.npm-global/bin/lark-cli"
else
  echo "ERROR: lark-cli not found; checked PATH and $HOME/.npm-global/bin/lark-cli" >&2
  exit 1
fi
```

后续命令统一使用 `"$LARK_CLI" --profile $BOT_PROFILE --as bot ...`,不要直接写裸 `lark-cli`。

## 何时使用

- 用户说"生成周报"、"出周报"、"半导体周报"、"行业周报"
- 定时任务触发
- 补发历史周报

## 核心原则

1. **直接爬取**:每14天从多源爬取近14天半导体行业研究内容(行业报告、市场分析、技术趋势、政策动态、企业公告)。
2. **地域聚焦**:**本地行业动态、行动清单、企业推荐仅限浙江本地**(杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山);长三角异动仅作为补充参考。
3. **TOP5-8精选**:本期最具实质影响的 5-8 条要闻。
4. **商机汇总**:按企业维度汇总本期可介入的商机。
5. **双版本输出**:Word 版(详细报告) + wiki 版(知识库存档),内容结构一致。
6. **独立运行**:周报由本 skill 独立负责。

**研究方向:半导体全产业链**:芯片设计、晶圆制造、先进封装、封测、半导体设备、材料、EDA/IP、功率半导体、MEMS、车规芯片、存储、第三代半导体、光电/传感器、半导体零部件等。

## Token 优化原则

- **SearXNG / web_search 精准搜索优先**:用关键词搜索半导体行业信息,比爬取大站再筛选高效得多。
- **web_fetch 用 text 模式**(`extractMode: "text"`),比 markdown 模式更精简。
- **maxChars=6000**,够提取文章摘要,不需要更大。
- **表格只查 A 列**去重,不查全表。
- **lark-cli 命令按预定义参数执行**,不要反复试错。
- **正文点入按需**:只在搜索结果发现重要线索时点入正文(maxChars=4000)。

## 产品资料

产品推荐必须基于本地产品资料文件,不得虚构产品名称、额度、期限、费率或准入条件:
- **产品资料路径**:`~/.openclaw/workspace/file/productFile.docx`
- 生成周报前**必须先读取该文件**,了解平安银行产品库内容。
- 产品资料中没有的参数写"待沟通"。
- 产品配置不要堆砌,采用"主推产品 + 配套产品"方式,每家企业一般推荐 2-4 类。

## 工作流

### 第〇步:总体要求(分析师角色与全局规则)

你以平安银行杭州分行"首席行业分析师"身份进行分析,当前分析对象为【半导体行业】。

核心职责不是简单汇总新闻,而是通过行业政策、政府规划、全国行业动态、浙江区域动态、重点企业动态和上下游产业链变化,挖掘可营销商机,并为客户经理生成清晰、简洁、可执行的企业推荐与银行产品配置方案。

分析必须服务于以下目标:
1. 半导体行业近期为什么值得关注?
2. 浙江地区有哪些区域机会?
3. 哪些浙江半导体企业值得优先拜访?
4. 推荐这些企业的理由是什么?
5. 平安银行有哪些展业机会?
6. 应该用哪些产品切入?
7. 客户经理该如何开口沟通?

**全局规则(贯穿所有步骤):**

1. 必须联网获取最新信息,不得只依赖历史知识。
2. 必须关注全国行业动态、浙江地区半导体动态、相关企业动态、上下游产业链动态。
3. 第一大板块只分析全国层面、国家层面、行业层面动态,**不放浙江内容**。凡是浙江相关政策、规划、项目、产业集群、区域机会,统一放入第二部分。
4. 第二大板块单独分析浙江地区动态与区域机会。
5. 第三大板块为重点企业推荐。
6. 企业推荐部分必须说明"推荐理由"和"银行展业机会"。
7. 企业信息要简洁,但需要体现企业高层和核心团队背景,包括学校、专业、导师、职业生涯、产业资源等公开信息。
8. 平安银行产品推荐必须基于本地产品资料(`~/.openclaw/workspace/file/productFile.docx`),**不得虚构产品名称、额度、期限、费率或准入条件**。如果产品资料中没有明确参数,写"待沟通"。
9. 内容要清晰明了,不要写成长篇学术报告。
10. 无法确认的信息写"待核实"或"未披露"。
11. 每条重要判断都要形成闭环:事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作;但"近期政策变动"板块不要每条政策都单独写闭环,应先把政策内容写充分,最后统一写一段综合影响闭环。
12. 周报正文不要在句中写来源括注,例如"(来源:XXX)"。如需保留依据,可在文末或开头"资料来源"统一概括,不要影响客户经理阅读。
13. **摘要交付优先级最高**:只要 Word、Wiki、商机表三个链接已经生成,任何不影响结果产物的错误(只读校验、JSON解析、重复行检查、排序检查、临时文件清理、CLI warning/notice、展示文件内容、cat/for循环查看日志、诊断命令等)都必须降级为 warning 写入本地诊断文件,不得抛出非零退出,不得让 cron run 进入 error,不得影响最终群聊摘要输出。
14. **摘要生成后工具调用禁令**:`reports/summary/BDT-summary.md` 写入后,不要再执行任何工具调用,包括 cat、for 循环查看日志、只读抽查、诊断命令或展示文件内容。最终 assistant 回复必须且只能输出第十步极简摘要,由 delivery 发送到配置的飞书群聊。

### 第一步:信息抓取(必抓源 + 搜索为主 + 垂直源补充)

**必抓源(4个,不可跳过):**

```
1. 同花顺首页 → web_fetch https://www.10jqka.com.cn/ (extractMode="text", maxChars=6000)
2. 财联社电报 → web_fetch https://www.cls.cn/telegraph (extractMode="text", maxChars=6000)
3. 新华网科技 → web_fetch https://www.xinhuanet.com/tech/ (extractMode="text", maxChars=6000)
4. 经济观察网 → web_fetch https://www.eeo.com.cn/ (extractMode="text", maxChars=6000)
```

**核心策略:必抓源打底,SearXNG 精准搜索补充,垂直源进一步补充;仅在 SearXNG 不可用时回退 web_search。**

**第二轮:SearXNG 精准搜索(5个查询,编号5-9,并行执行):**

> 使用本地 SearXNG 实例:`SEARXNG_URL=${SEARXNG_URL:-http://localhost:8080}`
> ⚠️ **运行器选择(必须执行)**:先检测 `uv` 是否存在;不存在则用 `python3`,不得因 `uv: command not found` 放弃。
> ⚠️ **JSON API 预检(必须执行)**:SearXNG 首页 200 不代表 JSON API 可用。执行搜索前必须先请求一次 `"$SEARXNG_URL/search?q=半导体&format=json&categories=general"`,确认 HTTP 200 且 `content-type` 为 `application/json`。若返回 403,通常是 `/etc/searxng/settings.yml` 中 `search.formats` 只启用了 `html`,需要在持久化配置中加入 `json` 并重启容器;修复前不得把它误判为"无结果"。若无法修复,记录原因后再回退 web_search。

```bash
SEARXNG_URL=${SEARXNG_URL:-http://localhost:8080}
SEARXNG_SCRIPT="$HOME/.openclaw/skills/searxng/scripts/searxng.py"
searxng_search() { if command -v uv >/dev/null 2>&1; then uv run "$SEARXNG_SCRIPT" search "$@"; else python3 "$SEARXNG_SCRIPT" search "$@"; fi; }
```

```
5. 半导体综合 → searxng_search "半导体 OR 芯片 OR 集成电路" -n 10 --format json --time-range month
6. 先进制程/封装 → searxng_search "晶圆制造 OR 先进封装 OR Chiplet OR HBM" -n 10 --format json --time-range month
7. 设备/材料/EDA → searxng_search "半导体设备 OR 光刻机 OR 刻蚀 OR EDA" -n 10 --format json --time-range month
8. 功率/第三代半导体 → searxng_search "功率半导体 OR 碳化硅 OR 氮化镓 OR 车规芯片" -n 10 --format json --time-range month
9. 资本/政策动态 → searxng_search "半导体融资 OR 半导体上市 OR 半导体政策 OR 半导体投资" -n 10 --format json --time-range month
```

> `--time-range month` 用于确保覆盖完整双周窗口;结果整理时必须按发布时间筛选近14天事件,超出14天的信息仅可作为背景,不得作为"本期新信号"。

⚠️ **必须使用 SearXNG,不要用 web_search(Brave 限流 1次/秒)**。如果 SearXNG 不可用,才回退到 web_search 串行执行。

⚠️ **已知坑:SearXNG 结果会跑偏。** `EDA` 容易搜到教育/经济开发署,`HBM` 容易搜到非半导体条目。处理规则:保留有效结果、剔除明显无关项;优先采纳标题/摘要同时包含半导体语境词的结果(芯片、晶圆、封装、存储、设备、材料、功率、SiC、GaN、车规、算力、AI服务器等);若有效结果不足,用更窄补充检索替代,例如 `"HBM 先进封装 半导体"`、`"EDA 芯片设计 半导体"`、`"半导体设备 刻蚀 光刻 中国"`,不要直接改用泛搜索大段爬取。

⚠️ **SearXNG 错误留痕**:若 SearXNG 子查询失败,保存原始错误、HTTP 状态码和 stderr 到 `reports/bdt-weekly/sources/searxng_<编号>.json`,不要只写 `{"error":"failed"}`。否则事后无法区分服务不可达、JSON 未启用、搜索词无结果、上游引擎限流。

**第三轮:半导体垂直源补充(3个,编号10-12,并行):**

> 注:垂直媒体首页多为 JS 动态渲染,若 web_fetch 返回空白或过短内容,直接跳过,不要重试,依赖搜索轮补位。
> 2026-05-21 校验:`news.elecfans.com` 已不可解析,改用电子发烧友行业资讯页;爱集微/集微网首页在 web_fetch 下偶发 fetch failed,优先抓取最新地址,失败时用 SearXNG site 搜索补位。

```
10. 爱集微/集微网 → web_fetch https://www.ijiwei.com/  (extractMode="text", maxChars=6000)
    - 若 web_fetch 失败,回退:searxng_search "site:ijiwei.com OR site:jiwei.cn 半导体 OR 芯片 OR 集成电路" -n 10 --format json --time-range month,并筛选近14天结果
11. 电子发烧友行业资讯 → web_fetch https://www.elecfans.com/news-363.html  (extractMode="text", maxChars=6000)
    - 备用:web_fetch https://www.elecfans.com/news/hangye/  (extractMode="text", maxChars=6000)
12. 电子工程专辑 → web_fetch https://www.eet-china.com/  (extractMode="text", maxChars=6000)
```

**第四轮:浙江区域专项搜索(1个,编号13,用 SearXNG):**

> 复用上方 `searxng_search` 函数

```
13. 浙江区域半导体专项 → searxng_search "半导体 浙江 OR 芯片 杭州 OR 半导体 宁波 OR 集成电路 浙江" -n 10 --format json --time-range month,并筛选近14天结果
```

**第四轮半:浙江非上市/专精特新企业补充搜索(1个,编号13.5,用 SearXNG):**

> 目的:捞取非上市半导体企业、专精特新/小巨人、园区招商项目,扩大推荐标的池,降低重复率。

```
13.5. 浙江半导体专精特新/非上市 → searxng_search "浙江 OR 杭州 OR 宁波 半导体 OR 芯片 OR 集成电路 专精特新 OR 小巨人 OR 融资 OR 投产 OR 产业园 OR 招商" -n 10 --format json --time-range month
```

**第五轮:iFinD 结构化数据补充(4个查询,编号14-17,时间限定近14天):**

> 使用 iFinD-Finance-Data skill,优先 Node.js 方案。每次调用后检查 `ok` 字段确认是否成功。
> **关键执行方式**:即使当前工具列表没有直接的 iFinD MCP 工具,也必须通过本地脚本调用:`~/.openclaw/skills/ifind-finance-data/call-node.js`。不要因为没有一等 MCP tool 就跳过 iFinD。
> **时间参数**:`time_start` = 14天前日期(YYYY-MM-DD),`time_end` = 今天日期(YYYY-MM-DD)
> ⚠️ `search_trending_news`(热点事件)和 `search_edb`(宏观指标)当前 MCP token 无权限,不调用。

Node.js 调用模板(每次查询可生成临时脚本,执行后删除):

```javascript
const { call } = require(process.env.HOME + '/.openclaw/skills/ifind-finance-data/call-node.js');
(async () => {
  const result = await call('news', 'search_news', {
    query: '半导体 芯片 集成电路 人工智能 算力',
    time_start: '<14天前>',
    time_end: '<今天>',
    size: 10
  });
  console.log(JSON.stringify(result, null, 2));
})();
```

执行后检查 `result.ok === true`;如 `ok=false` 或脚本报错,记录失败原因并跳过该 iFinD 子源,不重试超过 1 次。

⚠️ **已知坑:当前通常没有一等 iFinD MCP 工具。** 必须通过本地脚本 `~/.openclaw/skills/ifind-finance-data/call-node.js` 调用;不要因工具列表里没有 iFinD MCP tool 就跳过。查询完成后必须删除临时 `.js` 脚本,只保留必要的结果文件或摘要。

**新闻公告(2个,编号14-15,并行):**

```
14. search_news(新闻语义检索,严格14天)→ call("news", "search_news", {
  "query": "半导体 芯片 集成电路 人工智能 算力",
  "time_start": "<14天前>",
  "time_end": "<今天>",
  "size": 10
})
→ 半导体/AI 行业热点新闻

15. search_notice(公告语义检索,严格14天)→ call("news", "search_notice", {
  "query": "半导体 芯片 融资 定增 产线 投产 订单",
  "time_start": "<14天前>",
  "time_end": "<今天>",
  "size": 10
})
→ 上市公司公告(定增/订单/投产→银行商机),线索用 web_fetch 点入正文
```

**上市公司数据(2个,编号16-17,串行依赖:先取名单再查财务):**

```
16. search_stocks(半导体板块上市公司筛选)→ call("stock", "search_stocks", {
  "query": "半导体行业股票"
})
→ 获取半导体板块上市公司名单(含代码、子行业分类),用于后续关联和浙江企业定位

17. get_stock_financials(核心公司财务数据)→ call("stock", "get_stock_financials", {
  "query": "北方华创、中微公司、海康威视、士兰微、中控技术2025年三季度的营收增速、净利润"
})
→ 龙头公司业绩异动 → 银行授信/贷款商机(≤5个主体,避免超长截断)
```

⚠️ **iFinD 使用注意**:
- 需确认 `mcp_config.json` 已配置有效 `auth_token`
- 返回结果检查 `ok` 字段,失败则跳过该源,不重试超过 1 次
- iFinD 不支持地域过滤,返回结果需用地域关键词(浙江、杭州、宁波等)二次筛选
- 新闻/公告返回的是语义检索片段,不是全文;发现重要线索后再用 web_fetch 点入正文(maxChars=4000)
- iFinD 只覆盖上市公司及公开金融市场数据,**不覆盖非上市 AI 初创企业**
- 单次查询主体数控制在 5 个以内,避免超长截断
- 查询完成后清理临时生成的脚本文件

**按需补充:**
- 从搜索结果中发现重要文章时,点入正文抓取(web_fetch, extractMode="text", maxChars=4000)
- 如需更全面的市场/财经视角,可补充搜索:"半导体 行业 周报" OR "芯片 产业 趋势"(count=5)

**抓取规则:**
- 必抓源不可跳过,即使返回空白/JS 渲染失败也要记录并继续
- web_search + 垂直源并行执行
- 如果 web_fetch 返回空白/JS 渲染失败,跳过该源,不要重试
- 关注 **近 14 天内** 发生的事件(周报覆盖双周范围)
- 关注目标区域及周边地区的半导体企业动态优先

**⚠️ 抓取源审计留痕(必须执行):**
- 本次所有抓取源必须统一落盘到 `reports/bdt-weekly/sources/`,用于事后审计和复盘。
- 必抓 web_fetch 源分别保存为 `webfetch_01_10jqka.json`、`webfetch_02_cls.json`、`webfetch_03_xinhuanet_tech.json`、`webfetch_04_eeo.json`。
- SearXNG 编号 5-10、13 保存为 `searxng_<编号>.json`;iFinD 编号 14-17 保存为 `ifind_news.json`、`ifind_notice.json`、`ifind_stocks.json`、`ifind_financials.json`。
- 垂直源 10-12 若用 web_fetch 成功,保存 `webfetch_10_ijiwei.json`、`webfetch_11_elecfans.json`、`webfetch_12_eet_china.json`;若失败并回退 SearXNG,保存失败原因和回退结果。
- 浙江专项 13、非上市补充 13.5 保存为 `searxng_13.json`、`searxng_13.5.json`。
- 每个落盘文件至少包含:`source_id`、`source_name`、`url_or_query`、`fetched_at`、`ok`、`status_or_error`、`content_or_results`。不要只依赖运行上下文。

### 第二步:信息跟踪范围

按以下四大维度分类和组织抓取到的信息:

#### 1. 全国行业动态

重点关注:
- 国家政策、产业政策、监管政策、出口管制、国产替代政策、先进制造支持政策
- 行业供需变化、价格变化、技术路线变化(先进制程、先进封装、HBM、存储、功率器件、SiC/GaN 等)
- 扩产、并购、上市、融资、发债、重大项目
- 招投标、中标、大客户合作、车规/工业/AI 算力订单
- 出口、跨境、海外建厂、海外订单、供应链安全
- 风险事件:处罚、诉讼、亏损、债务压力、停产、客户集中度等

#### 2. 浙江区域动态

重点关注:
- 浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州、丽水、衢州、舟山等地政策
- 政府规划与产业方向必须优先聚焦浙江;浙江公开信息不足时,可补充长三角(上海/江苏/安徽)相关规划作为参考,但需明确标注地域且不得替代浙江结论
- 浙江"415X"先进制造业集群、集成电路产业链、第三代半导体、智能物联、汽车电子等方向
- 专精特新、小巨人、高新技术企业、隐形冠军、链主企业、上市/拟上市企业
- 地方重大项目、产业园区、技改补贴、设备更新、绿色制造、智能制造等
- 浙江在半导体产业链中的产业集群、重点企业、上下游配套和区域优势

#### 3. 企业动态

重点关注能转化为银行商机的信号:
- 扩产、拿地、环评、技改、设备采购、产线投产、设备搬入
- 中标、新订单、新客户合作、车规认证、导入大客户供应链
- 出口增长、海外布局、跨境业务
- 上市辅导、IPO、定增、发债、融资
- 应收账款增加、存货增加、资本开支增加、现金流压力
- 成为链主企业、核心供应商、重点培育企业
- 司法、处罚、失信、经营异常等风险信号

#### 4. 上下游产业链动态

分析企业所在产业链:
- 上游 EDA/IP、设备、零部件、材料、硅片、特气、靶材、光刻胶、封装材料
- 中游芯片设计、晶圆制造、封测、功率器件、MEMS、第三代半导体、模块/模组
- 下游汽车电子、工业控制、消费电子、通信、AI 算力、光伏/储能、物联网等应用
- 哪个环节景气上升
- 哪个环节资金占用加大
- 哪个环节适合供应链金融
- 哪个核心企业可带动批量获客

**地域标签:**
- `[浙江]` / `[杭州]` / `[宁波]` / `[绍兴]` 等
- `[上海]` / `[江苏]` / `[南京]` / `[苏州]` / `[南通]` 等
- `[安徽]` / `[其他]` / `[全球]`

**重要性评级:**
- ★★★★★:国家级政策 / 百亿级投资 / 行业拐点
- ★★★★:省级政策 / 十亿级融资 / 重大订单
- ★★★:企业级公告 / 产能变动 / 价格变动
- ★★:一般动态
- ★:值得关注但影响有限

### 第三步:分析逻辑

按照以下闭环进行分析:

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

**分析要求:**
- 每条重要判断都要形成闭环:事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作。
- "近期政策变动"写法:政策情况要比普通新闻更详细,说明发布主体、发布时间/背景、核心条款/支持方向、约束或机会点;不要在每条政策后都写"影响闭环",而是在该小节末尾统一写一段"综合影响闭环"。
- "政府规划与产业方向"写法:重点聚焦浙江地区;若浙江本地信息不足,可扩展至长三角作为补充参考,并明确标注地域。
- "来源引用"写法:正文不要出现"(日期,媒体/网站)""(来源:媒体名)"这类来源括注;日期可自然融入事实表述,来源统一放在报告开头或文末"资料来源"中概括。
- 第一大板块只分析全国层面、国家层面、行业层面动态,**不放浙江内容**。
- 浙江相关政策、规划、项目、产业集群、区域机会统一放入第二部分。

### 第四步:企业推荐判断规则

#### 1. 推荐理由

推荐理由应来自事实信号,例如:
- 所属半导体细分环节符合国家或浙江重点支持方向
- 企业处于景气上行或结构性机会赛道(先进封装、设备材料国产化、车规芯片、功率半导体、第三代半导体等)
- 企业位于浙江优势产业集群或产业园区
- 企业近期出现扩产、技改、中标、订单、出口、融资、上市辅导等积极信号
- 企业在产业链中具备核心企业、链主企业、优质供应商或优质客户地位
- 企业高层或团队具备较强产业、技术、资本、客户资源背景
- 企业具备银行授信、票据、供应链、跨境、现金管理、代发等切入空间
- 风险信号相对可控

#### 1.5 企业推荐轮换规则(必须执行)

⚠️ **客户名单重复度过高是已知痛点。** 每期推荐企业时,必须执行以下轮换逻辑:

1. **冷却名单(三源合并)**:生成推荐前,从以下三个来源提取近期推荐过的企业,合并为统一冷却名单:
   - **来源A**:最近 2 期周报(`reports/bdt-weekly/` 下最近两个日期的 `.md`),提取所有「企业名称」字段。
   - **来源B**:冷却名单文件(`reports/bdt-weekly/recommended_companies_*.txt`),读取最近 2 个文件。
   - **来源C:商机挖掘表格**(`SPREADSHEET_TOKEN: RpI5svn81hl9axtuaqUcwtAenBM, sheet_id: 89c832`)。使用 `"$LARK_CLI" sheets +read --spreadsheet-token "$SPREADSHEET_TOKEN" --sheet-id "$SHEET_ID" --range 'A1:J500' --profile "$BOT_PROFILE" --as bot` 读取 A 列全部客户名称。解析返回的 JSON,提取所有非空 A 列值,经别名归一后加入冷却名单。
   - 三个来源的企业名称统一做别名归一(见下方别名映射表),得到去重后的冷却名单。
2. **锚定例外**:如果冷却名单内的企业本期有**新的触发信号**(新融资、新扩产、新订单、新增借款、新政策关联、新风险事件),可破格保留,但最多保留 1-2 家,且必须在推荐理由中明确写出"本期新信号是什么"。
3. **新标的优先**:剩余名额必须从冷却名单以外的企业中选择。优先方向:
   - 浙江专精特新/小巨人名单中的半导体企业
   - 各地市产业园区招商新落地项目
   - 设备材料/零部件/EDA/IP 等上游细分环节的非上市公司
   - 近期有 IPO 辅导、股权融资、产线投产信号的中型企业
4. **轮换自检**:生成完成后必须检查--本期推荐企业中来自冷却名单的比例不得超过 40%(即推荐 5 家时最多 2 家重复,推荐 3 家时最多 1 家)。如超标,必须替换为冷却名单以外的新标的。

#### 2. 银行展业机会

必须从企业经营活动推导银行业务机会:
- 扩产/技改/设备采购 → 项目贷款、设备融资、科技创新和技术更新改造再贷款、平安租赁
- 订单增长/备货增加 → 短贷、普惠信用贷、银票贴现、国内信用证
- 应收账款增加/账期较长 → 付融通、保理、商票保贴、商票e贴
- 供应链上下游关系明确 → 订单融资、订货贷、平台数字贷、供应链金融
- 进口设备/材料、出口客户、海外业务 → 跨境支付结算、人民币国际证+福费廷、外币存款、跨境资金管理、平安避险
- 资金账户分散/管理复杂 → 数字财资、资产池、慧收款、移企付、口袋管家
- 员工规模较大/企业主需求明显 → 平安薪、个贷、家族信托、财富权益

### 第五步:企业高层与团队背景要求

企业关键信息中必须体现高层和团队背景,但要简洁。

重点关注:
- 董事长、实控人、总经理、CFO、CTO、核心创始人
- 教育背景:毕业学校、专业、学位
- 科研背景:导师、实验室、研究方向、学术成果,如公开可查
- 职业经历:曾任职企业、产业经历、管理经历、创业经历
- 产业资源:是否来自半导体龙头企业、高校科研院所、政府平台、上市公司、外企、核心客户体系
- 银行关注点:其背景是否有助于判断企业技术实力、客户资源、融资能力、资本市场潜力或决策链条

注意:
- 只使用公开可查信息。
- 不得虚构个人履历。
- 未披露的信息写"未披露"或"待核实"。

### 第六步:产品匹配规则

你只能基于本地产品资料(`~/.openclaw/workspace/file/productFile.docx`)中的平安银行产品库推荐产品,不得虚构产品名称、额度、期限、费率或准入条件。

如果产品资料中没有明确参数,写"待沟通"。

产品配置不要堆砌,采用"主推产品 + 配套产品"的方式。每家企业一般推荐 2-4 类产品即可。

优先使用以下产品方向:

1. **账户与资金管理**:数字财资、资产池、慧收款、移企付、平安结算通、产业结算通、口袋管家
2. **融资与授信**:平安透、网上自由贷、普惠金融信用贷、普惠金融科创贷、普惠金融担保贷、普惠金融抵押贷、银票极速贴现、银票无感贴现、国内信用证开证及融资、科技创新和技术更新改造再贷款
3. **供应链金融**:订单融资、付融通、商票保贴、商票贴现、商票e贴、订货贷、平台数字贷、普惠金融场景化方案

⚠️ **产品名称口径**:报告和商机表中的产品名称应优先使用 `productFile.docx` 原文写法。例如票据产品统一写"商票e贴/商票E贴"中的资料原文口径,不写成"商票 e 贴"。如果确需使用别名,必须先确认产品资料中存在同义写法。
4. **跨境与出海**:跨境支付结算、跨境贸易金融、跨境资金管理、外币存款、人民币国际证+福费廷、境内企业外债贷款、非居民全球授信、平安避险、新银关通
5. **资本市场与综合金融**:并购融资、银团融资、债券承销、债生态业务、资本市场融资、结构金融、平安证券债券承销、平安租赁、保险资金债权投资计划、集合资金信托计划、永续债权投资计划/永续信托计划
6. **员工与企业主服务**:平安薪、橙 e 贷、星链贷、普金信用贷、家族信托、私人理财权益、信用卡权益

### 第七步:生成周报(双版本输出)

**生成两种格式的周报,内容结构一致,输出方式不同:**

#### 版本A:Word 版(行业分析指令格式)

按以下完整结构生成详细行业分析报告,使用华文楷体:

```markdown
# 半导体行业商机周报

## 一、行业动态与发展总结
(仅全国/国家/行业层面,不含浙江内容)

### 1. 近期政策变动
(政策情况要写详细:发布主体/时间背景/核心条款/支持方向/约束要求;本小节末尾统一写一段"综合影响闭环",不要每条政策各写一个闭环)

梳理近期国家部委、行业主管部门发布的相关政策、监管要求、产业扶持、财政补贴、设备更新、绿色低碳、专精特新、外贸稳增长、科技创新等政策变化。

要求:
- 不要简单罗列政策标题。
- 要说明政策对【目标行业】的影响。
- 要说明可能带来的银行业务机会。
- 如政策发布日期、发布部门、政策名称可查,应简要注明。
- 浙江省及浙江地市政策不要放在这里。

### 2. 政府规划与产业方向

只梳理国家层面的产业规划、重大项目规划、重点产业布局和未来产业方向。

重点关注:
- 国家级产业规划
- 国家战略性新兴产业
- 国家未来产业方向
- 全国层面的设备更新、绿色制造、智能制造、科技创新等方向
- 国家级重大工程、重大项目、产业基金或政策工具
- 对企业扩产、技改、融资、产业链协同的影响

### 3. 行业发展趋势

总结行业当前的发展阶段、景气度、需求变化、技术路线、价格变化、竞争格局和资本市场表现。

要求说明:
- 行业处于上行、分化、调整还是出清阶段
- 哪些细分赛道更有机会
- 哪些企业类型更值得银行关注
- 哪些风险需要提前识别

### 4. 上下游产业链动态

分析全国或行业层面的上游、中游、下游最新变化。

重点判断:
- 上游原材料、设备、零部件价格或供应变化
- 中游企业扩产、订单、产能利用率变化
- 下游需求、出口、客户结构、渠道变化
- 哪个环节资金占用变大
- 哪个环节适合供应链金融、票据、保理、订单融资、订货贷等产品切入

## 二、浙江地区动态与区域机会

### 1. 浙江政策与政府规划

梳理浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州等重点城市近期政策、产业规划、园区规划、招商引资、设备更新、技改补贴、绿色制造、智能制造等动态。

要求:
- 说明政策或规划对本地企业的影响。
- 说明可能带来的银行授信、票据、供应链、跨境、现金管理等机会。
- 如政策发布日期、发布部门、政策名称可查,应简要注明。

### 2. 浙江重点产业与区域机会

重点关注:
- 浙江"415X"先进制造业集群
- 【目标行业】在浙江的重点产业集群、重点园区和重点城市
- 专精特新、小巨人、高新技术企业、隐形冠军
- 产业园区、开发区、重点项目、产业基金、招商落地项目

要求说明:
- 哪些产业集群正在释放机会
- 哪些区域更值得客户经理重点扫客
- 哪些企业类型更可能产生融资、供应链、跨境或现金管理需求

### 3. 浙江上下游产业链动态

分析浙江本地产业链上下游变化:
- 上游原材料、设备、零部件供应
- 中游制造、加工、集成、平台企业
- 下游客户、外贸订单、经销商、终端应用
- 哪些环节资金占用增加
- 哪些环节适合批量获客或供应链金融切入
- 哪些核心企业可以带动上下游企业营销

### 4. 银行展业机会

用3-5条总结浙江地区最值得平安银行杭州分行关注的展业机会。

要求:
- 必须结合浙江本地政策、产业集群、企业动态和产业链变化。
- 必须说明对应的银行业务机会。
- 尽量落到具体产品方向,如授信融资、票据、保理、供应链金融、跨境结算、现金管理、代发、财富管理等。

## 三、重点企业推荐

选择3-8家最值得客户经理跟进的浙江企业。每家企业按照以下模板输出。
⚠️ **硬性结构要求(不可压缩/不可省略)**:每一家企业必须严格保留下列字段和小标题;不得把"企业关键信息"合并成一段,也不得把"推荐理由""银行展业机会"改写成无结构长段。若资料不足,字段仍保留,并写"未披露/待核实"。生成完成后必须逐家自检:是否包含【推荐等级、所属行业、所在地区、产业链位置、推荐方向、企业关键信息-基本情况、企业关键信息-高层与团队背景、企业关键信息-银行关注点、推荐理由、银行展业机会、推荐产品组合、客户经理切入话术、风险提示】;缺一项必须返工。

### 企业名称:XXX公司

**推荐等级:** 高 / 中 / 低
**所属行业:**
**所在地区:**
**产业链位置:** 上游 / 中游 / 下游 / 平台型 / 服务商
**推荐方向:** 流动资金 / 供应链金融 / 跨境结算 / 票据 / 现金管理 / 代发 / 财富管理 / 综合金融等。

**企业关键信息:**
- **基本情况:** 主营业务、成立时间、所在地、企业性质、商业模式、产业链位置。
- **高层与团队背景:** 董事长/实控人/总经理/CFO/CTO的教育背景、学校、导师、职业经历、产业资源;未公开标注"未披露/待核实"。
- **银行关注点:** 管理层背景对企业技术实力、客户资源、融资能力、资本运作或决策路径的影响。

**推荐理由:**
- 基于政策、行业、浙江区域、企业动态、产业链位置、团队背景等事实信号写2-4点。
- 必须说明该企业为什么值得客户经理优先跟进。
- 不要只写企业好,要说明"好在哪里、机会在哪里、现在为什么值得看"。

**银行展业机会:**
- 从企业经营变化推导银行业务机会。
- 说明企业在授信融资、票据、保理、供应链金融、跨境结算、现金管理、代发、财富管理等方面的潜在需求。
- 必须讲清楚"企业经营场景 → 金融需求 → 平安银行可切入产品"。

**推荐产品组合:**
不用表格。用一段自然语言总结,必须包含"主推产品 + 配套产品 + 切入理由"。每家企业一般推荐2-4类产品即可,避免堆砌。例如:建议以【主推产品】切入,解决企业【核心经营/资金场景】;配套使用【产品1、产品2】,用于【具体理由】。资料未披露的额度、期限、费率或准入条件写"待沟通"。

**客户经理切入话术:**
简短、自然、可直接拜访使用的话术,避免生硬推销。

**风险提示:**
诉讼、负债率、应收账款、客户集中度、行业波动、政策依赖、核心团队稳定性等;无明显风险写"暂无明显公开风险,仍需结合征信、流水、财报、合同、客户结构和实地尽调确认"。

## 四、客户经理行动建议

用3-5条给出当天或近期最值得执行的动作,例如:
- 优先拜访哪些企业
- 从哪个业务场景切入
- 先聊哪些经营问题
- 准备哪些产品方案或材料
- 需要内部联动哪些产品经理或审批资源
```

**Word 输出要求:**
- **固定保存目录**:`/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly/`,不得保存到其他目录;如目录不存在先创建。
- **同步到 local-uploader 目录**:Word 文件生成并上传 Drive 后,先清空 `/Users/leidongqiao/Documents/codex project/local-uploader/data/半导体` 目录下的所有文件(保留目录本身,不删除目录),然后将 Word 周报文件拷贝一份到该目录。
- **双版本命名必须一致**:Word 文件名、Wiki Markdown 本地文件名使用同一个 basename:`半导体行业周报-YYYYMMDD`。
  - Word 文件名:`半导体行业周报-YYYYMMDD.docx`
  - Wiki 本地源稿:`半导体行业周报-YYYYMMDD.md`
  - 不再使用 `bdt-weekly-YYYYMMDD` 或 `行业商机周报_半导体_YYYYMMDD.docx` 这类旧文件名,避免 Drive、Wiki、摘要里同一份周报名称不一致。
- 字体使用华文楷体。
- **Word 样式优化**:Word 版必须是干净的报告排版,不要把 Markdown 原始符号带入正文;生成 docx 时需去掉 `- **`、`**`、表格竖线等 Markdown 标记。普通段落用自然段,企业信息可用短段落或简洁项目符号,但不要让每段前面都出现 `- **`。推荐产品组合不得用表格。
- 生成后上传为飞书 Drive 文件,获取可下载链接;**飞书 wiki 知识库正文开头必须写入 Word 版下载链接**(放在标题下方、正文说明前),推送摘要中的"周报全文(Word)"也必须使用该下载链接,不要只放本地路径。
- ⚠️ **Drive 上传限制**:`$LARK_CLI drive +upload --file` 只接受**相对路径**,必须先 `cd` 到文件所在目录再执行,不可用绝对路径。
- ⚠️ **Drive 链接生成坑**:上传结果通常只返回 `file_token`,不一定返回完整 URL。拿到 `file_token` 后按 `https://www.feishu.cn/file/<file_token>` 组装 Word 下载链接,并写入 wiki 开头和群聊摘要;不要把本地路径或裸 token 当作链接。

#### 版本B:飞书 wiki 版(知识库存档格式)

- 内容与 Word 版结构一致,适配飞书文档 Markdown 格式
- **固定保存目录**:`/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly/`,不得保存到其他目录
- **同名覆盖检查**:生成前先检查该目录下是否已有同名文件,若存在则直接覆盖,不保留重复文件。
- 通过第九步写入知识库
- wiki 正文开头(标题下方、覆盖周期/资料来源前)必须写入:`**Word版下载:** https://www.feishu.cn/file/<file_token>`。
- ⚠️ **wiki 正文中的 Word 下载链接必须用纯 URL 文本**,格式为 `**Word版下载:** https://.../file/...`,不要写成 `<https://...>`;飞书文档转换可能吞掉尖括号链接,导致 wiki 中只剩空的"Word版下载"。
- ⚠️ **飞书 wiki 排版硬规则:不要依赖单换行。** 飞书文档会把普通 Markdown 单换行合并,导致"推荐等级/所属行业/所在地区/产业链位置/推荐方向"等字段黏在一行。
- ⚠️ **企业元数据必须用列表格式**(`- 推荐等级:高`),不要用 `**推荐等级:** 高`(飞书 Markdown 会把连续行合并到一行,导致所有字段挤在一起),格式如下:
  ```markdown
  - **推荐等级:** 高
  - **所属行业:** XXX
  - **所在地区:** 杭州
  - **产业链位置:** 中游/平台型
  - **推荐方向:** XXX
  ```
- ⚠️ **Word 与 Wiki 格式分离**:Word 版去掉所有 Markdown 标记(纯段落 + 华文楷体);Wiki 版保留完整 Markdown(标题、列表、加粗、分隔线)。两者内容相同,格式各自适配平台。写入 wiki 后必须 fetch 回来抽查一次,重点检查是否存在 `推荐等级.*所属行业`、`所属行业.*所在地区`、`所在地区.*产业链位置`、`产业链位置.*推荐方向` 这类同一行黏连;发现即重写修复。


### 第八步:更新/追加商机到表格

从第七步周报的"四、客户经理行动建议"中提取需要跟进的浙江企业,写入"商机挖掘"电子表格。

**🔴 关键规则(必须严格遵守):**
- **从行动建议提取**:从周报"四、客户经理行动建议"中提取明确提及的浙江企业,这些是需要客户经理优先跟进的商机。
- **只写入浙江本地企业**,非浙江企业一律不写入表格。
- **写入前必须去重**:先读取 A 列,用"规范化核心简称精确匹配"判断是否已存在。
- **禁止重复写入同一企业**:同一核心简称只保留一行,已有行则更新,无则追加。
- **写入方式保持 BDT 现有方式**:优先使用 `bdt_bot` 的 tenant_access_token 直接调 Sheets API;也可使用 `"$LARK_CLI" --profile $BOT_PROFILE --as bot`,不得混用默认 ai_bot。

**去重逻辑(严格执行):**

⚠️ **第一步:规范化核心简称提取(关键!)**
1. 先将括号统一为全角:`(` → `(`, `)` → `)`
2. 然后去掉所有 `(...)` 修饰(地域、股票代码、备注等),得到**核心简称**

⚠️ **第二步:对已有 A 列的每一行也做同样的规范化**
对 A 列每个已有名称,同样去掉 `(...)` 得到已有核心简称。

⚠️ **第三步:精确匹配核心简称**
将新商机的核心简称与已有行的核心简称做**完全匹配**(==),不是包含匹配。
- 如果核心简称相同 → **原地更新该行**,**保持A列原名称不变**,只更新 B~J 列
- 如果没有任何已有行的核心简称匹配 → **追加新行**

⚠️ **已知坑:公司名称别名会绕过去重。** 在核心简称精确匹配前,先套用下方别名映射,把同一主体归一到同一核心简称;归一只用于匹配,不用于改写 A 列原名称。

```text
甬矽电子(宁波)股份有限公司 = 宁波甬矽电子股份有限公司 = 甬矽电子
杭州士兰微电子股份有限公司 = 士兰微
杭州长川科技股份有限公司 = 长川科技
宁波江丰电子材料股份有限公司 = 江丰电子
中巨芯科技股份有限公司 = 中巨芯
浙江创豪半导体科技有限公司 = 浙江创豪 = 创豪半导体
```

如执行中发现新的"同一主体不同写法",本次先人工归一并更新本别名表,避免下周重复写入。

⚠️ **严禁**:
- 更新行时修改A列客户名称(包括加后缀、改格式等),必须保持原名称不变
- 用包含匹配(如"中芯"匹配到"中芯集成"),必须用核心简称完全匹配

**写入流程(严格执行):**
1. 读取 A 列全量数据。
2. 对 A 列每个非空名称做规范化:去掉括号内容,得到**已有核心简称列表**。
3. 对本次商机先去重:按核心简称合并同名企业,每个核心简称只保留一条。
4. 对每个去重后的商机:提取核心简称 → 精确匹配 → 匹配到则更新,未匹配则追加。
5. ⚠️ **更新已有商机时,创建日期(I列)必须更新为当前日期(YYYY-MM-DD)**。
6. ⚠️ **如果匹配到的已有行状态为终态(closed/已关闭/已落地),则跳过该行,不更新**。
7. ⚠️ **新增商机的状态列统一填写"待联系",不要写 active/open**。
8. ⚠️ **更新已有商机时,状态列保持不变,不修改**。
9. ⚠️ **写入完成后,必须对整个表格进行时间倒序重排 + 清理残留空行**(见下方"表格排序与清理")。

**字段顺序**:客户名称、行业/领域、触发信号、优先级、推荐方案、预计金额、联系人、状态、创建日期、备注

**⚠️ 表格排序与清理(每次写入后必须执行):**

使用 `$LARK_CLI` 完整读取表格数据、按日期倒序排序、写回并清理残留行。**不要使用 Python urllib 直接调 Sheets API**;此前实践会遇到 404/SSL/接口路径不一致问题。

⚠️ **lark-cli JSON 解析通用规则(必须执行)**:`$LARK_CLI` 可能在 JSON 前后输出 proxy warning、deprecated warning、update notice 等非 JSON 文本。任何 Python 校验/排序/清理脚本解析 `$LARK_CLI` 输出文件时,必须先按括号层级截取第一个完整 JSON 对象,再 `json.loads()`;禁止使用 `json.loads(text[text.find('{'):])` 解析到文件末尾。

推荐 Python helper:

```python
def extract_first_json(text):
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object found")
    level = 0
    in_str = False
    esc = False
    for i, ch in enumerate(text[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                level += 1
            elif ch == "}":
                level -= 1
                if level == 0:
                    return json.loads(text[start:i + 1])
    raise ValueError("incomplete JSON object")
```

推荐流程:

```bash
# 0. 已完成 lark-cli 路径解析,已有 LARK_CLI/BOT_PROFILE/SPREADSHEET_TOKEN/SHEET_ID

# 1. 读取全表(至少 A1:J500),本地脚本中过滤 A 列非空行并按 I 列日期倒序排序
"$LARK_CLI" sheets +read   --spreadsheet-token "$SPREADSHEET_TOKEN"   --sheet-id "$SHEET_ID"   --range 'A1:J500'   --profile "$BOT_PROFILE" --as bot

# 2. 将排序后的数据整体写回 A2:J{end_row}
"$LARK_CLI" sheets +write   --spreadsheet-token "$SPREADSHEET_TOKEN"   --sheet-id "$SHEET_ID"   --range "A2:J${end_row}"   --values "$SORTED_VALUES_JSON"   --profile "$BOT_PROFILE" --as bot

# 3. 清理残留空行:先查 sheet 最大行数,只在 row_count > end_row 时删除
ROW_COUNT=$("$LARK_CLI" sheets +info   --spreadsheet-token "$SPREADSHEET_TOKEN"   --profile "$BOT_PROFILE" --as bot   | jq -r '.data.sheets.sheets[] | select(.sheet_id=="'"$SHEET_ID"'") | .grid_properties.row_count')

if [ "$ROW_COUNT" -gt "$end_row" ]; then
  "$LARK_CLI" sheets +delete-dimension     --spreadsheet-token "$SPREADSHEET_TOKEN"     --sheet-id "$SHEET_ID"     --dimension ROWS     --start-index $((end_row + 1))     --end-index "$ROW_COUNT"     --profile "$BOT_PROFILE" --as bot
else
  echo "No residual rows to delete: row_count=$ROW_COUNT, end_row=$end_row"
fi
```

⚠️ **关键说明:**
- `sheets +delete-dimension` 的 `--end-index` 不能超过当前 `grid_properties.row_count`,否则会报 `[90202] dimension endIndex wrong`。如果 `row_count <= end_row`,说明表格已经没有残留行,跳过删除即视为成功。
- 写入前如目标行数不足,可先用 `$LARK_CLI sheets +insert-dimension` 或 `+add-dimension` 补齐行数;写入后再按上面逻辑清理。
- 排序后必须验证 `sheets +read A1:J30`,确认最新日期在前、A 列无异常空行。
- ⚠️ **空行判断不要只看超范围读取结果**:`sheets +read A1:J30` 可能在实际 `row_count` 之外返回全 `null` 行。必须结合 `sheets +info` 的 `grid_properties.row_count` 判断残留行;若 `row_count == end_row`,读到的尾部全 `null` 是超范围回显,不是表内脏行。

### 第九步:写入知识库(飞书 wiki 版)

**写入内容:第七步版本B(飞书 wiki 版),结构与 Word 版一致,适配飞书 Markdown 格式。**

**Word 下载链接位置要求:** Word 版生成后必须先上传飞书 Drive 获取 `file_token`,按 `https://www.feishu.cn/file/<file_token>` 组装下载链接;wiki 正文开头(标题下方、覆盖周期/资料来源前)必须写入 `**Word版下载:** https://www.feishu.cn/file/<file_token>`,不得只在文末附链接。⚠️ 不要使用 `<url>` 尖括号格式;飞书 Markdown 可能吞掉尖括号链接。

**Wiki 企业元数据格式要求:** 推荐等级、所属行业、所在地区、产业链位置、推荐方向等元数据必须用 Markdown 列表格式(`- 推荐等级:高`),不要用 `**key:** value` 格式。飞书 Markdown 解析器会把连续的同类型行合并到一个段落,导致所有字段挤在一行。

**重要:每次生成都覆盖当前同名文件(半导体行业周报-YYYYMMDD),不要有重复日期的文档。Word/Wiki/本地 Markdown 三者必须同名同日期,只有扩展名不同。**

**🔴 关键规则(必须严格遵守):**
- 文档必须创建在知识库**根目录**(`parent_node_token` 为空字符串),**不能**创建在"首页"或其他节点下面。
- 创建新节点时必须显式传空父节点:`--parent-node-token ""`。不要省略该参数;部分 `lark-cli wiki +node-create` 版本在只传 `--space-id` 时仍可能落到"首页"或默认节点下。
- 必须使用**机器人身份**(`--as bot`)创建,创建者显示为机器人。
- **保持 BDT 现有写入方式**:必须使用 `--profile $BOT_PROFILE --as bot`,避免 lark-cli 默认应用(通常是 ai_bot)导致权限错误。
- 空间名称是 `半导体行研`。

**步骤:**

⚠️ **路径安全硬规则(防止 cron 假失败):**
- `REPORT_DIR` 必须固定为 `/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly`，`DIAG_DIR` 必须固定为 `/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/diagnostics`，写入前先 `mkdir -p "$REPORT_DIR" "$DIAG_DIR"`。
- 任何命令只要执行过 `cd "$REPORT_DIR"`，后续读取/写入 diagnostics 一律使用 `"$DIAG_DIR/xxx.json"` 绝对路径；禁止在 `cd reports/bdt-weekly` 后再读写 `reports/diagnostics/xxx.json` 或 `../diagnostics/xxx.json`。
- 展示/打印诊断文件不是核心流程。若要读取诊断文件，必须使用 `python try/except` 或 shell `test -s "$file" && ... || true`，不得让 `FileNotFoundError`、`sed/cat` 失败、路径拼错把 cron run 标成 error。
- `docs +update` 的 stdout 重定向必须写到绝对路径，例如 `> "$DIAG_DIR/wiki_update_YYYYMMDD.json"`；不要依赖当前目录推断相对路径。

1. **列出知识库所有节点,查找是否已有同名文档(搜索全部节点,不限根目录!)**:
   ```bash
   "$LARK_CLI" wiki nodes list --params '{"space_id":"'$WIKI_SPACE_ID'","page_size":50}' --profile $BOT_PROFILE
   ```
   从返回结果中搜索 title 为 `半导体行业周报-YYYYMMDD` 的节点,提取 `obj_token` 和 `node_token`。
   ⚠️ **必须搜索所有节点**(不限 `parent_node_token`),否则第一次创建时可能被放在"首页"下,第二次搜不到就重复创建了。
   ⚠️ **如果找到多个同名文档**,选 `obj_edit_time` 最新的那个,用 `docs +update` 覆盖;其余用 `drive files +patch --type docx --file-token <obj_token> --body '{"trash_type":"doc_trash"}' --profile $BOT_PROFILE --as bot` 删除。

2. **如果找到同名文档**:
   - 将 wiki 版 Markdown 保存为本地临时文件(例如 `半导体行业周报-YYYYMMDD.md`),正文保留标题、列表、加粗等 Markdown 语法。
   - 先 `cd` 到 wiki Markdown 文件所在目录,再使用 `"$LARK_CLI" docs +update --api-version v2 --doc <obj_token> --profile $BOT_PROFILE --as bot --command overwrite --doc-format markdown --content @./半导体行业周报-YYYYMMDD.md` 覆盖内容。**不要用原始 docx/v1 blocks API 手工创建文本块**,否则加粗、链接等 Markdown 富文本会丢失。
   - ⚠️ **必须使用 v2 完整参数**。只传旧版 Markdown 参数会报 `--command is required`,导致 cron 最终状态失败并只推送失败通知。
   - 输出文档链接:`https://www.feishu.cn/wiki/<node_token>`。

3. **如果未找到同名文档**:
   - 使用以下命令以**机器人身份**创建(注意必须带 profile):
     ```bash
     "$LARK_CLI" wiki +node-create --profile $BOT_PROFILE --as bot \
       --space-id "$WIKI_SPACE_ID" \
       --parent-node-token "" \
       --title "半导体行业周报-YYYYMMDD" \
       --obj-type "docx"
     ```
   - 从返回结果提取 `obj_token`(用于内容更新)和 `node_token`(用于 URL)。
   - 将 wiki 版 Markdown 保存为本地临时文件,先 `cd` 到该文件所在目录,再使用 `"$LARK_CLI" docs +update --api-version v2 --doc <obj_token> --profile $BOT_PROFILE --as bot --command overwrite --doc-format markdown --content @./半导体行业周报-YYYYMMDD.md` 写入内容。
   - ⚠️ **必须使用 v2 完整参数**。只传旧版 Markdown 参数会报 `--command is required`,导致 cron 最终状态失败并只推送失败通知。
   - 输出文档链接:`https://www.feishu.cn/wiki/<node_token>`。
   - ⚠️ 创建后必须立即用 `wiki nodes list` 确认该 `node_token` 的 `parent_node_token`。如果不是空字符串,立即用 `wiki +move --profile $BOT_PROFILE --as bot --node-token <node_token> --target-space-id "$WIKI_SPACE_ID"` 移回根目录,并保存 move 结果;不要等全文写入或最终验收时才发现位置错误。
4. **🔴 Wiki 排序规则(必须执行)**:周报 wiki 文档必须以时间倒序排列,即最新一期紧挨在「商机挖掘表格」之后。
   - 创建或更新完成后,再次执行 `"$LARK_CLI" wiki nodes list --params '{"space_id":"'$WIKI_SPACE_ID'","page_size":50}' --profile $BOT_PROFILE` 获取根目录节点列表。
   - 在根目录中查找标题包含"商机挖掘"的节点,记录其 `node_token`。
   - 先用 `wiki +move` 确保本期周报节点在根目录:
     ```bash
     "$LARK_CLI" wiki +move --profile $BOT_PROFILE --as bot \
       --node-token <本期周报 node_token> \
       --target-space-id "$WIKI_SPACE_ID" \
       --target-parent-token ""
     ```
   - ⚠️ **参数坑**:`wiki +move` 没有 `--parent-node-token` 参数,根目录移动必须用 `--target-parent-token ""`。不要把 `wiki +node-create` 的 `--parent-node-token` 参数套到 `wiki +move` 上。
   - 如果需要把本期周报精确排到「商机挖掘表格」之后,当前 `wiki +move` CLI 不暴露 `after_node_token` 参数,必须用原生 API:
     ```bash
     "$LARK_CLI" api POST "/open-apis/wiki/v2/spaces/$WIKI_SPACE_ID/nodes/<本期周报 node_token>/move" \
       --profile "$BOT_PROFILE" --as bot \
       --data '{"target_space_id":"'"$WIKI_SPACE_ID"'","target_parent_token":"","after_node_token":"<商机挖掘表格 node_token>"}'
     ```
   - ⚠️ 如果找不到「商机挖掘表格」节点,记录警告但不得中断流程,周报仍保留在根目录。

**安全写入模板(推荐照抄):**
```bash
REPORT_DIR="/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly"
DIAG_DIR="/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/diagnostics"
mkdir -p "$REPORT_DIR" "$DIAG_DIR"

"$LARK_CLI" wiki +move --profile "$BOT_PROFILE" --as bot \
  --node-token "$NODE_TOKEN" \
  --target-space-id "$WIKI_SPACE_ID" \
  --target-parent-token "" \
  > "$DIAG_DIR/wiki_move_root_YYYYMMDD.json" || true

(cd "$REPORT_DIR" && "$LARK_CLI" docs +update --api-version v2 \
  --doc "$OBJ_TOKEN" --profile "$BOT_PROFILE" --as bot \
  --command overwrite --doc-format markdown \
  --content @./半导体行业周报-YYYYMMDD.md) \
  > "$DIAG_DIR/wiki_update_YYYYMMDD.json"

python3 - <<'PY' || true
from pathlib import Path
for name in ("wiki_move_root_YYYYMMDD.json", "wiki_update_YYYYMMDD.json"):
    p = Path("/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/diagnostics") / name
    try:
        print(p.read_text(encoding="utf-8")[:1000])
    except FileNotFoundError:
        print(f"WARNING: diagnostic file missing: {p}")
PY
```

**禁止**使用 `feishu_wiki_space_node` 工具(该工具可能将文档创建在首页下),必须使用 `"$LARK_CLI" wiki +node-create --profile $BOT_PROFILE --as bot --space-id` 命令。

**写入后校验(必须执行):**
```bash
"$LARK_CLI" docs +fetch --doc <obj_token> --profile "$BOT_PROFILE" --as bot > /tmp/wiki_fetch.json
```
检查返回 Markdown:
- 必须能看到 `**Word版下载:**` 和 Word file 链接;飞书 fetch 可能把纯 URL 转成 Markdown 链接,只要链接文本和目标 URL 都存在即视为通过;
- 必须保留企业元数据列表(`- **推荐等级:**` 等);
- 不得出现 `推荐等级.*所属行业`、`所属行业.*所在地区`、`所在地区.*产业链位置`、`产业链位置.*推荐方向` 这类字段黏连;
- 若发现黏连或格式丢失,使用 `docs +update --api-version v2 --command overwrite --doc-format markdown --content @./文件` 重新覆盖,不要改用底层 blocks API。

⚠️ **已知坑:wiki fetch 校验不要对整个 JSON 字符串做正则。** 只检查返回里的 `data.markdown` 字段;否则 JSON 转义/压缩可能造成"推荐等级.*所属行业"误报。若 `data.markdown` 中列表项逐行存在,即视为通过。

⚠️ **docs +fetch 版本提示**:若 `docs +fetch` 输出 v1 deprecated 警告但仍能返回 Markdown,可继续用于本次校验并记录警告。`docs +update` 必须使用 v2 参数:`--api-version v2 --command overwrite --doc-format markdown --content @./文件`。

### 第十步：推送至群聊（极简概要 + 链接，200字左右）

**🔴 关键规则：推送到群聊的内容是极简概要和链接，不是全文！手机端必须能一次读完。**

**长度限制：正文控制在 200 字左右（不含链接 URL），最多不超过 300 字。**

**推送方式：** cron `delivery.mode=announce` 将 agent 最终文本回复投递到群聊。最终回复为纯文本格式，包含四行 emoji 正文 + 三个纯 URL 链接。

**最终回复模板：**
```
📌 半导体商机周报·浙江｜YYYY.MM.DD-MM.DD

🔥 主线：XXX、XXX、XXX
🏠 浙江机会：XXX
🏢 优先跟进：XXX、XXX、XXX
🎯 切入方向：XXX/XXX/XXX

Word: https://www.feishu.cn/file/XXXX
Wiki: https://www.feishu.cn/wiki/XXXX
商机表: https://www.feishu.cn/sheets/XXXX?sheet=YYYY
```

⚠️ **三个链接缺一不可**，必须使用完整的飞书 URL，不要放本地路径或裸 token。

#### 10.0 更新冷却名单记录(必须执行)

生成完成后,把本期推荐企业写入冷却名单文件,供下期轮换规则读取:

```bash
mkdir -p ~/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly/
echo '<本期所有企业名称,一行一个>' > ~/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly/recommended_companies_latest.txt
```

⚠️ 文件名固定为 `recommended_companies_latest.txt`。轮换规则读取最近 2 期时,实际读取最近 2 个日期的 `recommended_companies_*.txt` 文件(如有),同时也可从 `.md` 中提取备用。

#### 10.1 同步至工作空间（摘要必须带链接）

推送前,先把要推送的极简摘要写一份到本地工作空间:

1. **清空目录:**删除 `reports/summary/` 目录下所有文件(目录本身保留)。
2. **写入文件:**将即将推送的群聊摘要内容（含三个链接）写入 `reports/summary/BDT-summary.md`。

⚠️ **摘要正文必须包含三个链接**,格式为 `标签: URL`（纯文本），例如：
```
Word: https://www.feishu.cn/file/XXXX
Wiki: https://www.feishu.cn/wiki/XXXX
商机表: https://www.feishu.cn/sheets/XXXX?sheet=YYYY
```
这三个链接跟在四行 emoji 正文之后，不要省略。cron delivery 会将 agent 最终回复投递到群聊，摘要文件与最终回复必须一致。

```bash
# 清空目录
mkdir -p ~/.openclaw/workspace/workspace-BDTresearcher/reports/summary
find ~/.openclaw/workspace/workspace-BDTresearcher/reports/summary -maxdepth 1 -type f -delete
# 写入摘要（四行正文 + 三个链接，cat heredoc 避免 echo 转义问题）
cat > ~/.openclaw/workspace/workspace-BDTresearcher/reports/summary/BDT-summary.md << 'SUMMARY'
📌 半导体商机周报·浙江｜YYYY.MM.DD-MM.DD

🔥 主线：XXX、XXX、XXX
🏠 浙江机会：XXX
🏢 优先跟进：XXX、XXX、XXX
🎯 切入方向：XXX/XXX/XXX

Word: https://www.feishu.cn/file/XXXX
Wiki: https://www.feishu.cn/wiki/XXXX
商机表: https://www.feishu.cn/sheets/XXXX?sheet=YYYY
SUMMARY
```

⚠️ **已知坑:不要用 `rm -f reports/summary/*`。** cron 默认 shell 可能是 zsh,目录为空时通配符会报 `no matches found`;统一使用上面的 `find ... -delete`。

#### 10.2 推送至群聊

**推送方式:** cron `delivery.mode=announce` 会将 agent 最终文本回复投递到群聊。agent 的最后一步输出必须且只能是第十步摘要模板（四行正文 + 三个链接）。

**推送内容要求：**
- 行业动态：只提炼 2-3 个主线关键词，不逐条列新闻
- 浙江区域：只写 1 句机会集中方向
- 企业推荐：只列重点 3 家以内，不写推荐理由
- 行动建议：只写 1 句"优先跟进 + 切入方向"
- 样式要求：正文四行呈现，固定为「🔥 主线 / 🏠 浙江机会 / 🏢 优先跟进 / 🎯 切入方向」，不要写成一大段话
- **三个链接必须跟在正文之后**，每行一个，格式 `标签: URL`，使用飞书 Drive/file 下载链接、wiki 链接、sheets URL
- **不要**输出周报全文内容
- **不要**使用长分隔线、长清单、TOP5-8逐条新闻、企业推荐理由、执行日志
- ⚠️ **群聊收到的消息是纯文本**（cron announce 不支持 `msg_type=post`），链接以纯 URL 呈现即可，用户可点击。

**🔒 群聊最终回复锁(防止误推全文/日志):**
1. 任何会被 delivery / cron / 群聊看到的最终 assistant 回复,**必须且只能**使用本步骤的「200字左右极简概要 + 三个链接」格式。
2. **禁止**把以下内容作为最终群聊推送:执行日志、完成情况清单、工具调用结果、文件本地路径、Markdown/wiki 源稿、Word 正文全文、调试说明。
3. 推送前必须自检 5 项，缺一不可：
   - 已压缩为 2-3 个主线关键词，不是 TOP 新闻长清单；
   - Word 链接是飞书 Drive/file 下载链接(`https://www.feishu.cn/file/...`)，不是本地路径；
   - wiki 链接是 `https://www.feishu.cn/wiki/...`；
   - 商机表格链接是 `https://www.feishu.cn/sheets/...?sheet=...`；
   - 三个链接均已包含在最终回复中，跟在四行正文之后。
4. 如果 Word Drive 链接、wiki 链接或 sheets 链接任一缺失,**不要推送群聊摘要**;先补齐链接,再输出第十步模板。
5. 若需要向用户说明执行状态,只能在非群聊/人工排查上下文说明;在群聊定时任务中,最终输出仍必须是第十步摘要模板。

**⚠️ Cron 成功态保护(防止摘要生成后只推送失败通知):**
- 一旦 Word 链接、Wiki 链接、商机表链接齐全,且 `reports/summary/BDT-summary.md` 已写入,后续不要再执行非必要的高风险写操作(例如二次 `docs +update`、重复 move、重复表格清理)。
- 若确需做补充校验,只允许执行只读检查;发现问题时记录到本地诊断文件,不要让已完成的摘要交付被非关键修复命令的失败覆盖。
- **非核心错误直接忽略并继续群发**:只要 Word/Wiki/商机表链接齐全,后续只读校验、JSON 解析、重复行检查、排序检查、临时文件清理等失败都不影响结果摘要输出。命令层必须使用稳健解析或 `|| true`/try-except 兜底,不能让这类失败把 cron run 标成 error。
- **解析 lark-cli JSON 输出时必须截取首个完整 JSON 对象**:`lark-cli` 可能在 JSON 后追加 proxy warning、update notice、deprecated warning。禁止用 `json.loads(text[text.find('{'):])` 直接解析到文件末尾;必须按括号层级截取第一个完整 JSON 对象,或把非 JSON warning 另存诊断文件。
- OpenClaw cron 的 `delivery.mode=announce` 在任务 `status=error` 时会推送 failure notification,而不是最终摘要。因此最终回复前最后一步必须是读取/确认 `reports/summary/BDT-summary.md`,并以第十步模板作为 assistant 最终输出;不要在最终输出后再调用工具。
- **最终工具调用禁令**:`reports/summary/BDT-summary.md` 写入后,不要再执行 `cat`、`for f ...`、`echo/show`、日志查看、排序复核、只读抽查等任何工具调用来"展示结果"。这些动作一旦失败仍会把 cron 标红。若人工排查必须查看,只能在非 cron 对话中执行;cron 主流程直接把摘要作为最终 assistant 回复。

### 第十一步:表达风格

面向客户经理,不面向学术研究。写作风格规则:

1. **面向客户经理**:语言专业、直接、可执行,不是学术研究。
2. **不堆砌新闻**:不要简单罗列新闻标题,要说明影响和机会。
3. **不堆砌产品**:产品配置不要堆砌,采用"主推产品 + 配套产品"方式,每家企业一般推荐 2-4 类;重点企业推荐中的"推荐产品组合"用一段话总结,不用表格。
4. **企业重点讲清4件事**:推荐理由 → 银行展业机会 → 推荐产品组合 → 客户经理怎么开口。
5. **简要呈现企业基本信息**:不需要机械罗列全部工商信息。
6. **帮助形成判断**:输出要帮助客户经理回答--今天该联系谁、为什么联系、聊什么产品、怎么切入。
7. **Word输出**:字体使用华文楷体;版式要像正式报告,去掉 Markdown 原始符号(尤其是 `- **`、`**`、表格分隔线),避免每段前面都有项目符号和加粗标记。
8. **正文去来源括注**:正文面向客户经理,不写"(iFinD新闻,5月20日)""(来源:XXX)"等来源括注;证据来源统一在"资料来源"中概括即可。

### 第十二步:输出完成

输出完成后,由调用方(定时任务等)通过 delivery 配置推送到飞书群,无需在 skill 内执行推送。

## 特殊场景

### 信息源全部失败

如果所有 web_fetch / SearXNG / web_search 都失败或返回空白:
1. 不要编造内容。
2. 告知用户信息源抓取失败,建议手动提供素材。
3. 或基于已获取的少量信息生成最小化版本并标注"信息有限"。

### 用户要求手动生成

用户说"生成上期周报"或"生成上周周报"时,同样执行以上流程,并优先按近14天/指定双周周期取数。

## 注意事项

1. **不编造数据**:所有企业、金额、日期必须来自爬取的实际信息。
2. **产品资料**:产品推荐必须基于 `~/.openclaw/workspace/file/productFile.docx`,不得虚构产品名称、额度、期限、费率或准入条件。
3. **地域限制**:本地行业动态、行动清单、企业推荐仅限浙江本地企业;全国龙头/外省大厂动态不纳入本地企业推荐。
4. **禁止推荐不合规业务**。
5. **双版本输出**:Word 版用于详细报告(华文楷体),wiki 版用于知识库存档(飞书 Markdown 格式),内容结构一致。⚠️ Word 与 Wiki 格式必须分离:Word 去掉所有 Markdown 标记;Wiki 用标准 Markdown(标题、列表、加粗、分隔线)。Wiki 中企业元数据必须用列表格式(`- 推荐等级:高`),不要用 `**key:** value`。
6. **知识库标题**:半导体行业周报-YYYYMMDD。
7. **知识库写入**:必须使用 `"$LARK_CLI" wiki +node-create --profile $BOT_PROFILE --as bot --space-id $WIKI_SPACE_ID --parent-node-token \"\"` 创建,禁止使用 `feishu_wiki_space_node` 工具。去重时**搜索全部节点**(不限 parent_node_token),避免重复创建。创建后立刻校验 `parent_node_token`,非空则立即用 `wiki +move --target-parent-token \"\"` 移回根目录。🔴 **Wiki 排序**:创建/更新完成后,若需排到「商机挖掘表格」之后,使用原生 Wiki move API 的 `after_node_token`,不要使用不存在的 `wiki +move --after-node-token`。
8. **群聊推送**:推送概要 + 链接,不是全文。
9. **商机挖掘表格**:数据来源为周报"四、客户经理行动建议"中提及的浙江企业。写入前必须去重,只写浙江本地企业。更新已有商机时日期必须更新为当天。写入后必须按时间倒序重排并清理残留空行。
10. **表格写入/飞书操作统一使用 `$LARK_CLI`**:全部飞书操作(Drive 上传、wiki 创建/写入、表格读写/清理)均通过 `"$LARK_CLI" --profile $BOT_PROFILE --as bot` 执行。不要直接用 Python urllib 调 Sheets API(会遇 404/SSL 证书问题)。每个 agent 对应自己的 bot,不要混用。
11. **搜索工具选择**:第一步保持本 skill 既有策略,优先使用 SearXNG(本地无限制),脚本路径 `~/.openclaw/skills/searxng/scripts/searxng.py`,环境变量 `SEARXNG_URL=${SEARXNG_URL:-http://localhost:8080}`。执行前必须预检 JSON API;仅在 SearXNG 不可用或 JSON API 无法修复时回退到 `web_search`(Brave 限流 1次/秒,需串行执行)。
12. **代理配置**:Gateway 进程需配置代理环境变量(`HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:7890`),否则 Brave API 连接超时。$LARK_CLI 会检测到代理变量并发出警告,不影响功能。
13. **Word 输出**:使用华文楷体字体,固定保存到 `/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly/`,文件名必须与 Wiki 节点同 basename,格式为 `半导体行业周报-YYYYMMDD.docx`;生成后上传飞书 Drive,并将下载链接写在 wiki 正文开头及推送摘要中;Word 正文必须清理 Markdown 标记,推荐产品组合不用表格。
14. **正文来源格式**:周报正文去掉媒体/网站来源括注;不要出现"(日期,来源)""(来源:XXX)"。资料来源只在报告开头或文末统一概括。
15. **源材料审计留痕**:每次抓取必须把必抓源、SearXNG、垂直源、浙江专项、非上市补充、iFinD 和回退搜索结果统一保存到 `reports/bdt-weekly/sources/`,文件内保留 source_id、来源、时间、ok 状态、错误或内容摘要,避免事后只能依赖运行上下文。
16. **企业推荐轮换**:必须执行第1.5节「企业推荐轮换规则」--读取最近2期冷却名单,锚定企业最多保留1-2家,新标的优先推荐;完成后续接自检,重复率≤40%。每期完成后更新 `recommended_companies_latest.txt`。

## 文件路径

```text
skills/bdt-weekly-report/
├── SKILL.md                    # 本文件
└── references/
    └── (预留)
```

## 关键参数速查

**⚠️ 以下为当前 agent(BDT Researcher)的参数。其他 agent 复用时需要替换为自己的值。**

```bash
# lark-cli profile(必须为当前 agent 自己的 bot 创建)
BOT_PROFILE: "bdt_bot"

# 商机挖掘表格
SPREADSHEET_TOKEN: "RpI5svn81hl9axtuaqUcwtAenBM"
SHEET_ID: "89c832"
去重查询: 89c832!A:A(只查客户名称列)
追加写入: 89c832!A:J

# 知识库
WIKI_SPACE_ID: "7637077749416610770"
WIKI_SPACE_NAME: "半导体行研"
WEEKLY_TITLE_PREFIX: "半导体行业周报"
节点标题: 半导体行业周报-YYYYMMDD

# 地域
REGION: "浙江"
REGION_CITIES: ["杭州","宁波","温州","绍兴","嘉兴","湖州","金华","台州","丽水","衢州","舟山"]

# Word 输出目录
WORD_REPORT_DIR: "/Users/leidongqiao/.openclaw/workspace/workspace-BDTresearcher/reports/bdt-weekly/"
WORD_FILE_PATTERN: "半导体行业周报-YYYYMMDD.docx"
```

### 其他 agent 复用步骤

1. 为当前 agent 的 bot 创建 lark-cli profile:
   ```bash
   echo -n "$APP_SECRET" | "$LARK_CLI" config init --app-id "$APP_ID" --brand feishu --name <bot_name> --app-secret-stdin
   ```
2. 将该 bot 添加为知识库管理员:
   ```bash
   "$LARK_CLI" wiki members create --as user --params '{"space_id":"$WIKI_SPACE_ID"}' --data '{"member_id":"<bot_openid>","member_type":"openid","member_role":"admin"}'
   ```
3. 创建或获取商机挖掘表格,记录 `spreadsheet_token` 和 `sheet_id`。
4. 修改本 SKILL.md 中的参数(或创建同级 `config.json`)。
5. 在 cron 定时任务中设置 `BOT_PROFILE` 环境变量或写入配置文件。
