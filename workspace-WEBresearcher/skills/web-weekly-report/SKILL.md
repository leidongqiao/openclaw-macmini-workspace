---
name: web-weekly-report
description: |
  生成互联网行业研究周报(聚焦浙江),每周爬取多源行业研究内容,去重筛选、
  转化为银行商机清单,推送至飞书群。每周五执行,商机/行动清单/企业动态仅限浙江本地。
---

# 互联网行业研究周报生成 Skill

每周直接爬取多源行业研究内容,生成双版本周报(Word详细报告 + 飞书wiki知识库存档),推送至飞书群。

## 复用说明

本 skill 可复用于其他机器人。复用时需要修改「关键参数速查」章节中的值,
**其他内容(研究方法论、抓取流程、报告模板、写入逻辑)保持不变**。

### 每个 agent 需要修改的参数

| 参数 | 说明 | 如何获取 |
|------|------|----------|
| `BOT_PROFILE` | lark-cli profile 名称(对应 agent 自己的 bot) | `lark-cli config init --name <bot_name> --app-id <app_id>` 创建 |
| `WIKI_SPACE_ID` | 飞书知识库 space_id | `lark-cli wiki spaces list` |
| `WIKI_SPACE_NAME` | 知识库名称(用于去重搜索) | 从 wiki spaces list 确认 |
| `SPREADSHEET_TOKEN` | 商机挖掘表格的 spreadsheet_token | 从飞书表格 URL 提取 |
| `SHEET_ID` | 商机挖掘表格的 sheet_id | 从飞书表格 URL 提取 |
| `REGION` | 地域聚焦(如「浙江」「江苏」「广东」) | 根据 agent 定位 |
| `REGION_CITIES` | 地域下属城市列表 | 根据 agent 定位 |
| `WEEKLY_TITLE_PREFIX` | 周报文档标题前缀(如 `internet-weekly`) | 自定义 |

### 配置示例(在 agent 的 SKILL.md 同级创建 `config.json`)

```json
{
  "bot_profile": "web_bot",
  "wiki_space_id": "7637062266134760425",
  "wiki_space_name": "互联网行研",
  "spreadsheet_token": "ZvM9scRdph9aqzthwPAchTJ8nTe",
  "sheet_id": "c41411",
  "region": "浙江",
  "region_cities": ["杭州","宁波","温州","绍兴","嘉兴","湖州","金华","台州","丽水","衢州","舟山"],
  "weekly_title_prefix": "internet-weekly"
}
```

### 使用方式

执行周报生成前,先读取同级 `config.json`(如有)并覆盖参数;如无则使用默认值。
命令中统一使用 `--profile $BOT_PROFILE --as bot`。

## 何时使用

- 用户说"生成周报"、"出周报"、"互联网周报"、"行业周报"
- 定时任务触发
- 补发历史周报

## 核心原则

1. **直接爬取**:每周从多源爬取行业研究内容(行业报告、市场分析、技术趋势、政策动态)
2. **地域聚焦**:**商机地图、行动清单、企业动态仅限目标区域**(如浙江:杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山);长三角异动作为补充参考
3. **TOP5-8精选**:本周最具实质影响的5-8条事件
4. **商机汇总**:按企业维度汇总本周可介入的商机
5. **双版本输出**:Word 版(详细报告) + wiki 版(知识库存档),内容结构一致
6. **独立运行**:周报由本 skill 独立负责

**研究方向:互联网全产业链 + AI Token消费生态链**(人工智能、生成式AI、大模型、智能体Agent、AI应用、AI搜索、AI办公、AI营销、AI电商、AI内容、AI教育、AI医疗、AI游戏、平台经济、数字经济、数据要素、数字贸易、跨境电商、互联网广告、直播电商、内容平台、SaaS、云服务、企业服务软件、金融科技、支付、物流与供应链科技、互联网出海等)

**AI Token定义:**本 skill 中的"AI Token"默认指大模型输入/输出Token、推理调用量、API调用消耗、模型服务计费单位及其带动的产业链,不指虚拟货币或区块链Token,除非用户另有说明。

## Token 优化原则

- **搜索优先用 searxng**(本地 SearXNG 实例),Brave web_search 作为备用;searxng 无 API 限流、无布尔 OR 语法问题、无需逐条串行。用法:`python3 ~/.openclaw/skills/searxng/scripts/searxng.py search "query" -n 10 --format json`;时间范围用 `--time-range day`(近1天)或 `--time-range week`(近7天)
- **web_fetch 用 text 模式**(`extractMode: "text"`),比 markdown 模式更精简
- **maxChars=6000**,够提取文章摘要,不需要更大
- **iFinD 查询聚焦互联网行业**:query 中必须限定互联网、AI应用、SaaS、平台经济、跨境电商、游戏、数字营销、AI Token等关键词,避免返回宽泛金融数据
- **iFinD 时间精确到近7天**:time_start/time_end 必须用实际日期,size 控制在 5-10
- **表格只查 A 列**去重,不查全表
- **所有飞书 API 统一走 lark-cli**(sheets/drive/docs/wiki),不用 Python urllib 直接调 API,避免 SSL 代理问题
- **lark-cli 路径**:在 PATH 中可能不可用，实测位置为 `~/.npm-global/bin/lark-cli`。所有脚本中应优先使用绝对路径 `~/.npm-global/bin/lark-cli`。
- **lark-cli 命令按预定义参数执行**,不要反复试错
- **正文点入按需**:只在搜索结果发现重要线索时点入正文(maxChars=4000)
- **searxng 结果直接落盘**:输出是完整 JSON，避免在命令 stdout 中被截断。建议先写入临时文件再解析，不要在 exec 输出中直接解析。

## 执行经验与避坑指南(持续更新)

### 1. 工具调用与路径

- **lark-cli 不在 PATH**:实测路径为 `~/.npm-global/bin/lark-cli`。所有脚本用绝对路径，别依赖 PATH。
- **同级 config.json 路径**:`config.json` 指 SKILL.md 所在目录的同级文件,即 `skills/web-weekly-report/config.json`,不是 workspace 根目录。执行前必须读取该路径,读取失败才回退默认值。
- **SKILL.md 必须分页读完整**:`read`/工具输出可能显示 `truncated`、`omitted` 或“Use offset to continue”。遇到这些提示必须继续按 offset 分页读取到文件末尾,不要只读前几百行就开始执行;尤其本 skill 的关键坑位和表格写入规则分散在后半段。
- **searxng 截断**:搜索结果 JSON 较大，直接 echo 会被截断。必须先写文件再解析。
- **searxng `number_of_results` 不可靠**:实测可能出现 `number_of_results=0` 但 `results` 数组有有效内容。判断是否有结果必须看 `len(results)` 和结果内容,不能只看 `number_of_results`。`unresponsive_engines` 只说明部分搜索引擎不可用,不代表本次查询完全失败。
- **Brave 不支持布尔 OR 语法**:`"A" OR "B"` 会被当精确匹配处理,返回大量无关结果。优先 searxng;回退 Brave 时用空格分隔关键词。
- **命令输出里可能混有 WARN/_notice**:`lark-cli` 常在 stdout/stderr 输出 proxy/update warning,JSON 里也可能带 `_notice.update`。解析 JSON 时不要直接 `json.load(stdin)` 接整段命令输出;优先用 `--jq` 输出目标字段到文件,或过滤出 `{...}` JSON 主体后再解析。判断成功看 `ok:true` 和关键业务字段,不要把 `_notice` 当失败。
- **代理设置**:飞书 `lark-cli` 如不需要代理,优先加 `LARK_CLI_NO_PROXY=1` 减少 warning 和代理不确定性;普通 web_fetch/searxng 可按环境使用代理。
- **iFinD search_trending_news 可能 403**:该接口受权限限制,返回 `Tool not allowed`。遇到时跳过,只写入 `source_status.md/json` 过程备注,不得进入周报正文、资料来源或推送摘要。
- **iFinD search_notice 可能为空**:语义检索对时间范围和 query 要求严格,可能返回空。为空时只写入 `source_status.md/json` 过程备注,不影响报告。
- **iFinD 返回是多层 JSON**:Node 调用外层返回 `{ok,status_code,data}`;真正公告通常藏在 `data.result.content[0].text` 的 JSON 字符串里,其中 `data.data` 又是一个转义后的公告数组字符串。解析时要逐层 `json.loads/JSON.parse`,不要只看外层壳就误判为空。
- **iFinD 调用方式**:不能直接向 `call-node.js` 喂 JSON,必须按 iFinD skill 的三参签名调用:`call(server_type, tool_name, params)`。新闻/公告/热点事件统一用 `server_type="news"`,例如 `call("news", "search_notice", {...})`。不要写成 `call("search_notice", {...})`,否则会报 `unknown server_type: search_notice`。
- **iFinD 工作目录**:Node 脚本用 `__dirname` 读取 `mcp_config.json`,可从任意目录 require;Python 脚本 `call.py` 使用相对路径读取 `mcp_config.json`,若用 Python 方案必须先 `cd ~/.openclaw/skills/ifind-finance-data/` 后再执行,否则会误报缺 `mcp_config.json`。

### 2. 数据抓取

- **失效或低质源**:同花顺首页返回内容极少、经济观察网 JS 渲染严重、部分垂直媒体可能空白。按规则跳过即可,不要重试。
- **fetch 成功不等于有效**:有些首页虽然 200,但只抓到活动广告、宏观股市、很短摘录或非互联网内容(如 LatePost 首页低质、界面首页可能是活动稿)。必须按“本周/互联网商业化/浙江机会/银行商机”四个条件二次筛选;低质成功源也要记录为 low-yield,优先用站内搜索补正文。
- **搜索结果噪声过滤**:searxng 可能混入知乎、Instagram、LinkedIn、招聘页、垃圾 SEO 页和非本周内容。不要机械采用搜索前 5 条;先去重、过滤非公开可信源/非本周/非目标赛道,重要线索再 `web_fetch` 正文。
- **搜索源不可用不等于抓取失败**:如果某个 searxng 查询因 CAPTCHA/too many requests/access denied 返回空,仍必须记录该查询状态并继续后续查询;不能因此跳过整轮信息抓取。若 `results` 有内容但多个 engine unresponsive,按低置信补充源处理,不要直接丢弃。
- **数据源健康度要维护**:每次周报执行后,把 `fetch failed/404/403/验证页/412/内容极少/200但低质` 的源记录到本节。连续 2 次不可用或低质的源降级为「可选/搜索替代」,不要继续作为必抓源反复浪费时间。
- **2026-05-21 互联网周报数据源健康度**:
  - 财联社电报 `https://www.cls.cn/telegraph`: `web_fetch` 返回 fetch failed。后续仅尝试 1 次;失败则用 searxng 搜索替代:`site:cls.cn 互联网 AI应用 SaaS 平台经济 快讯`。
  - 证券时报旧快讯页 `https://www.stcn.com/article/newsflash.html`: 返回 404。已降级,不再作为直接 fetch 必抓 URL;改用 searxng 搜索替代:`site:stcn.com 互联网 数字经济 SaaS 跨境电商 快讯`。
  - 虎嗅首页 `https://www.huxiu.com/`: 返回验证页。降级为搜索替代:`site:huxiu.com 互联网 AI应用 SaaS 平台经济`。
  - IT桔子首页 `https://www.itjuzi.com/`: 返回 412。降级为搜索替代:`site:itjuzi.com 融资 SaaS AI应用 企业服务`。
  - 极客公园首页 `https://www.geekpark.net/`: 返回 403。降级为搜索替代:`site:geekpark.net AI应用 SaaS 互联网`。
  - 晚点 LatePost 首页可访问但内容少。保留为低权重补充,重要线索优先走站内搜索:`site:latepost.com 阿里 腾讯 字节 美团 网易 AI SaaS`。
  - 新华网科技、36氪快讯、界面新闻当前可用,保留直接 fetch。
- **替代源优先级**:当核心源不可用时,优先补充 IT之家、上海证券报/中国证券网、21财经、国家市场监管总局、网信办、商务部、国家数据局、浙江省政府/商务厅/经信厅/数据局/杭州发布等可访问源或站内搜索。
- **JS 渲染失败**:所有垂直源返回空白时,跳过并继续。
- **纯 AI 技术内容排除**:论文、benchmark、训练技巧、参数对比等不纳入,除非明确关联商业化、模型API价格、Token消费、企业采购、融资或浙江本地产业机会。

### 3. 飞书 Wiki

- **Wiki 节点默认挂子目录**:`wiki +node-create --space-id` 创建后可能挂在某个 parent 下。如需根目录,创建后用 `wiki +move --node-token <token> --target-space-id <space>` 移到根目录。
- **Wiki 单换行会黏行**:飞书 Markdown 会把单换行合并。企业元数据必须用列表格式,标题和正文之间加空行。
- **Word 下载链接**:用纯 URL 文本 `**Word版下载：** https://...`,不要写 `<https://...>`,尖括号可能被吞。
- **创建后必须 fetch 回来抽查**:检查是否有 `推荐等级.*所属赛道` 等同行黏连。
- **docs 读取命令是 +fetch 不是 +read**:当前 lark-cli 版本没有 `docs +read --doc`;读取/校验文档正文使用 `docs +fetch --doc <obj_token或URL> --profile ... --as bot`。不要把 `docs +read` 失败误判为正文未写入。
- **docs +update 文件参数**:`lark-cli docs +update` 没有 `--markdown-file`。必须使用 `--markdown "@./file.md"`,且 `@` 文件路径必须是当前工作目录下的相对路径;先 `cd /tmp/...` 再传 `@./wiki.md`。
- **Wiki URL 与 token**:记录 `node_token` 和 `obj_token`。更新正文用 `obj_token/doc_id`;移动节点用 `node_token`;分享链接通常用 `https://www.feishu.cn/wiki/<node_token>`。
- **校验不要依赖 docs +read 一定可解析**:`docs +read` 输出格式/权限可能变化。最小校验至少确认 `docs +update` 返回 `ok:true`,再用可读摘要或块数量抽查;失败时不要误判为正文未写入。
- **发布前禁词扫描**:Wiki Markdown、本地 Markdown、Word 源文本和最终摘要发布前必须扫描执行日志词: `403`、`无权限`、`Tool not allowed`、`接口失败`、`抓取失败`、`替代源`、`source_status`、`permission_grant`、`_notice`、`Traceback`、`STDERR`、`WARN`。命中则先判断是否为正文不该出现的日志;除资料引用中的正常业务语义外,必须删除或改写后再上传/推送。

### 4. 商机表格去重与写入

- **核心简称去重需别名映射**:如 `杭州群核信息技术有限公司` 和 `群核科技`、`杭州深度求索人工智能基础技术研究有限公司` 和 `DeepSeek` 可能需要别名映射。建议加入别名/简称映射表。
- **状态保留规则**:更新已有商机时,状态列保持不变。新增商机统一填「待联系」。
- **排序 key 有 None 值**:创建日期列可能有空值/None。排序时必须做 `str(r[8] or '')` 安全转换,直接比较会报 TypeError。
- **写表前必须做快照**:先读取 `A1:J` 全量有效行落盘到 `/tmp/.../sheet_before.json`,再生成合并后的完整行集。不要未备份就写 `A2:J...`。
- **不要写死 `A1:J200` 或重写默认空行**:先用 `sheets +info` 读取 `row_count`,再读取 `A1:J<row_count>` 作为原始快照;随后必须过滤出 A 列非空的有效业务行,计算 `last_effective_row = 1 + 有效业务行数`。商机表默认可能有 200+ 空行,这些空行不是业务数据,不得参与排序、合并或写回。
- **大表写入避免超长 shell 参数**:商机表行数较多时,不要把巨大 JSON 直接塞进命令行参数。优先使用 lark-cli 支持的文件输入/脚本封装;若只能传参数,先确认参数长度安全,并保留 `sheet_before.json` 快照以便回滚。
- **严禁直接从 A2 写少量新增行**:`sheets +write --range A2:J3` 会覆盖原有前两条商机。新增/更新必须按「读全表快照 → 过滤 A 列非空有效行 → key 去重合并 → 保留状态 → 排序 → 只重写有效数据区 A2:J<last_effective_row> → 清空或删除有效区后的残留旧业务行 → 再读回校验」流程执行。
- **行号/索引易错**:飞书表格范围行号是 1-based;删除维度 `start-index/end-index` 也按工具语义确认后再用。删除前先读 `row_count` 和目标尾行,不要盲删。
- **写入成功要看返回和读回**:`lark-cli sheets +write` 成功应有 `ok:true/updatedRows`。写后必须读回前 15 行,检查新增企业、旧企业、状态列、日期排序都正确。
- **保留旧商机不要重写成低质量占位**:更新/重排时不要把旧记录的优先级、触发信号、方案等字段改成粗糙占位。除非有新事实,旧行应从快照原样保留;只更新本周命中的企业。

### 5. Word/Wiki 格式分离

- 建议用脚本生成两份:docx(去 Markdown 符号) 和 md(保留 Markdown)。
- Word 版用 python-docx 时,`- **` 等标记需去除,段落用纯文本。
- **产品库 docx 不能直接 read**:`productFile.docx` 是二进制,直接 read 会显示乱码。必须用 `python-docx` 提取段落文本,再基于真实产品库推荐产品;如果未能读取产品库,不得虚构产品名称/额度/期限/费率。
- **报告标题与文件名统一**:每期先生成唯一 `REPORT_BASENAME`,格式为 `$WEEKLY_TITLE_PREFIX-YYYYMMDD`(默认 `internet-weekly-YYYYMMDD`);Word 文件名、飞书 Drive 上传名、Wiki 节点标题、本地 Markdown 副本文件名必须基于同一个 `REPORT_BASENAME`。不要出现 Word/Wiki/本地副本使用不同 basename 的不一致情况。
- **本地文件不得重名覆盖**:保存 Word/Markdown 前必须检查目标路径是否已存在。若存在同名文件,不要覆盖;改用 `REPORT_BASENAME_v2`、`REPORT_BASENAME_v3` 递增后缀,并用最终确定的 basename 同步更新 Word 上传名和 Wiki 标题。
- **报告产物统一归档**:临时抓取材料放 `/tmp/web-weekly-YYYYMMDD/`,正式 Word 放 `reports/web-weekly/<REPORT_BASENAME>.docx`,Wiki Markdown 本地副本放 `reports/web-weekly/<REPORT_BASENAME>.md` 便于复核。
- **Word 上传后记录 token**:上传 Drive 后记录 `file_token`、文件名、大小;Wiki 文首 `Word版下载` 使用纯 URL 文本。若无法生成稳定下载链接,至少在最终摘要中标注 file_token 供人工定位。
- **Drive 上传权限提示**:bot 身份上传可能返回 `permission_grant.status=skipped`、提示没有 current CLI user open_id,这不代表上传失败;只要 `ok:true` 且有 `file_token/size/url` 即可继续。`permission_grant` 是后台权限提示,不得写进周报正文、资料来源或推送摘要。

### 6. 定时任务与最终推送

- **cron delivery 已负责发群**:定时任务通常配置了 `delivery.mode=announce`、`channel=feishu`、`to=<chat_id>`。不要重复手动群发;最终回复写群摘要即可由 cron 自动投递。
- **cron 失败告警不得进周报群**:本任务的群聊 `delivery` 只用于成功摘要。若排查发现 `failureAlert` 被打开或失败通知进入同一个 `to=<chat_id>`,必须关闭失败告警或改到私聊/调试通道,避免把工具报错当周报发群。
- **非核心清理失败不能污染最终投递**:删除重复文档、清理历史节点、抽查排版等非核心动作必须先确认当前 `lark-cli schema`,并用捕获退出码方式记录到 `source_status` 或过程备注;不得让这类清理失败导致 cron 标记 error。Word 上传、Wiki 写入、商机表读回校验和最终摘要链接齐全才是成功投递的核心门槛。
- **执行结束前要列检查清单**:至少确认: Word 已生成、Word 已上传、Wiki 已创建/更新/移根、商机表已读回校验、iFinD 已执行且状态写入 `source_status.md/json`、数据源状态已记录、最终摘要含 Word/Wiki/商机表链接且不含执行日志。
- **日期口径**:周报覆盖近 7 天,时间必须使用实际日期。不要写“近7天前日期”这种占位。遇到用户/cron 给定当前时间,以该时间的 Asia/Shanghai 日期为准。
- **主题边界**:本 skill 是互联网周报。若用户要求“排除纯AI/大模型”,则排除论文、benchmark、模型参数、训练技巧等纯技术内容;保留与互联网商业化、平台/SaaS/电商/出海、Token消费成本、浙江产业机会直接相关的 AI 应用和算力消费内容。

## 工作流

### 第〇步:总体要求(分析师角色与全局规则)

**执行前硬性检查(必须先做):**

1. 分页读取完整 `SKILL.md` 到文件末尾(确认无 `truncated/omitted/Use offset to continue`),再读取同级 `config.json`:`skills/web-weekly-report/config.json`。
2. 创建本次临时目录 `/tmp/web-weekly-YYYYMMDD/`,所有搜索 JSON、表格快照、Wiki Markdown 先落盘。
3. 读取产品库 `~/.openclaw/workspace/file/productFile.docx` 时必须用 `python-docx`,不要直接 read 二进制。
4. 先读商机表 `row_count`,再读取 `A1:J<row_count>` 原始快照并保存 `sheet_before.json`;随后只把 A 列非空行视为有效商机行,空白默认行不得参与合并、排序或写回。
5. iFinD 必须按 `call('news', tool_name, params)` 快速探测,不要把工具名当 server_type。
6. 生成唯一 `REPORT_BASENAME`;Word 文件名、Drive 上传名、Wiki 标题、本地 Markdown 副本必须一致,且不得覆盖已有本地同名文件。

**执行后硬性检查(最终回复前必须确认):**

1. Word 本地文件存在且大小合理,已上传 Drive 并记录 `file_token`。
2. Wiki 已创建/更新成功,如 `parent_node_token` 非空则移动到知识库根目录。
3. 商机表已读回校验:新增、更新、旧记录保留、状态列保留、日期排序正确。
4. 信息抓取清单已全量执行,每个必抓源、搜索查询、替代源、iFinD 查询都有状态备注:成功/空结果/低质/失败/权限受限/跳过原因。不能因为某源失败就不走后续来源。状态备注只能写入 `source_status.md/json`,不得进入周报正文、资料来源、Wiki正文或推送摘要。
5. 数据源失败和替代源使用情况已写入本次过程备注;若出现新的稳定失败源,更新本 skill 的健康度记录。
6. Word 文件名、Drive 文件名、Wiki 标题、本地 Markdown 副本 basename 一致;若发生重名,最终使用的 `_vN` 后缀也必须一致。
7. Word/Wiki 正文、资料来源、本地 Markdown 和最终摘要已完成执行日志禁词扫描,不含 `403/无权限/Tool not allowed/接口失败/source_status/permission_grant/_notice/STDERR/WARN` 等后台过程词。
8. 最终摘要包含核心主线、浙江机会、优先跟进企业、切入方向、Word/Wiki/商机表链接。

你以平安银行杭州分行"首席行业分析师"身份进行分析,当前分析对象为互联网行业,尤其关注AI时代互联网市场、AI应用生态、AI Token消费生态链、平台经济、数字经济、跨境互联网与浙江本地互联网产业机会。

核心职责不是简单汇总新闻,而是通过行业政策、政府规划、全国互联网行业动态、浙江区域互联网产业动态、重点企业动态和上下游生态变化,挖掘可营销商机,并为客户经理生成清晰、简洁、可执行的企业推荐与银行产品配置方案。

分析必须服务于以下目标:
1. AI时代互联网行业哪些方向值得关注?
2. 浙江地区有哪些互联网和AI产业机会?
3. 哪些浙江互联网企业、AI企业、平台型企业值得优先拜访?
4. 推荐这些企业的理由是什么?
5. 平安银行有哪些展业机会?
6. 应该用哪些产品切入?
7. 客户经理该如何开口沟通?

**全局规则(12条,贯穿所有步骤):**

1. 必须联网获取最新信息,不得只依赖历史知识。
2. 必须关注全国互联网行业动态、AI产业动态、浙江地区互联网与数字经济动态、相关企业动态、AI Token消费生态链上下游动态。
3. 第一大板块只分析全国层面、国家层面、互联网行业层面动态,**不放浙江内容**。凡是浙江相关政策、规划、项目、产业集群、区域机会,统一放入第二部分。
4. 第二大板块单独分析浙江地区动态与区域机会。
5. 第三大板块为重点企业推荐。
6. 企业推荐部分必须说明"推荐理由"和"银行展业机会"。
7. 企业信息要简洁,但需要体现企业高层和核心团队背景,包括学校、专业、导师、职业生涯、产业资源等公开信息。
8. 平安银行产品推荐必须基于本地产品资料(`~/.openclaw/workspace/file/productFile.docx`),**不得虚构产品名称、额度、期限、费率或准入条件**。如果产品资料中没有明确参数,写"待沟通"。
9. 内容要清晰明了,不要写成长篇研究报告。
10. 无法确认的信息写"待核实"或"未披露"。
11. 每条重要判断都要形成闭环:事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作;但「近期政策变动」板块不要每条政策都单独写闭环,应先把政策内容写充分,最后统一写一段综合影响闭环。
12. 周报正文不要在句中写来源括注,例如"(5月14日,杭州网/人民网浙江)""(来源:XXX)"。如需保留依据,可在文末或开头"资料来源"统一概括,不要影响客户经理阅读。

### 第一步:信息抓取(必抓源 + 搜索为主 + 垂直源补充)

**核心源(优先抓取,不可因单源失败中断):**

```
1. 新华网科技 [active] → web_fetch https://www.xinhuanet.com/tech/ (extractMode="text", maxChars=6000)
2. 36氪快讯 [active] → web_fetch https://36kr.com/newsflashes (extractMode="text", maxChars=6000)
3. 财联社电报 [degraded: 2026-05-21 fetch failed] → web_fetch https://www.cls.cn/telegraph (只尝试 1 次;失败即搜索替代)
4. 证券时报快讯 [disabled-url: 2026-05-21 旧 URL 404] → 不再直接 fetch 旧 URL,改用 searxng 搜索替代
```

**失败处理:** 核心源返回空白/JS渲染失败/fetch failed/404/403/验证页时,跳过该源,记录并继续,不重试。对 degraded/disabled 源,立即执行对应 searxng 站内搜索替代:

```bash
$SEARXNG_CMD "site:cls.cn 互联网 AI应用 SaaS 平台经济 快讯" -n 10 --time-range week --format json
$SEARXNG_CMD "site:stcn.com 互联网 数字经济 SaaS 跨境电商 快讯" -n 10 --time-range week --format json
```

**核心策略:必抓源打底,searxng 精准搜索补充,垂直源进一步补充。**

**全量执行要求(硬性):**
- 本节列出的核心源、精准搜索、垂直源/替代源、本地专项搜索、iFinD 查询必须全部走一遍。
- 单个来源失败、空结果、低质、403/404、验证页、CAPTCHA、权限受限,都只记录状态并继续执行后续来源,不得提前停止信息抓取。
- 每个来源的原始结果必须落盘到 `/tmp/web-weekly-YYYYMMDD/`,并生成 `source_status.md/json` 过程备注,至少包含:来源名称、URL/查询词、执行时间、状态(success/empty/low-yield/failed/permission-denied/skipped)、可用结果数量、失败原因、是否采用替代源。
- searxng 结果状态必须按 `len(results)` 判断可用结果数量;`number_of_results` 只能做参考,不能作为空结果判定依据。
- 最终报告的资料来源只能概括展示实际采用的正常来源类型或媒体名称,不得出现 `403`、`无权限`、`接口失败`、`替代`、`跳过`、`报错`、`source_status`、`Tool not allowed` 等执行日志口径。本次过程备注必须保留全量抓取清单,便于复盘数据源质量。

**第二轮:searxng 精准搜索(7个查询,并行执行):**

```bash
SEARXNG_SCRIPT="~/.openclaw/skills/searxng/scripts/searxng.py"
SEARXNG_CMD="python3 $SEARXNG_SCRIPT search"

1. $SEARXNG_CMD "人工智能 生成式AI 大模型 Agent AI应用 SaaS 2026" -n 10 --time-range week --format json
2. $SEARXNG_CMD "平台经济 数字经济 数据要素 数字贸易 互联网监管 2026" -n 10 --time-range week --format json
3. $SEARXNG_CMD "跨境电商 互联网出海 App出海 游戏出海 SaaS出海 2026" -n 10 --time-range week --format json
4. $SEARXNG_CMD "电商 直播电商 内容平台 数字营销 互联网广告 2026" -n 10 --time-range week --format json
5. $SEARXNG_CMD "AI办公 AI客服 AI营销 AI电商 AI编程 AI视频 融资 2026" -n 10 --time-range week --format json
6. $SEARXNG_CMD "大模型API 计费 Token价格 模型调用量 云服务 算力租赁 2026" -n 10 --time-range week --format json
7. $SEARXNG_CMD "SaaS 企业服务 CRM ERP 协同办公 数据服务 融资 2026" -n 10 --time-range week --format json
```

**如果 searxng 实例不可用(返回空或连接失败),回退到 Brave web_search,但此时不用 OR 语法,改用空格分隔关键词:**

```
1. web_search("人工智能 生成式AI 大模型 Agent AI应用 SaaS", freshness="week", count=10)
2. web_search("平台经济 数字经济 数据要素 数字贸易 互联网监管", freshness="week", count=10)
3. web_search("跨境电商 互联网出海 App出海 游戏出海 SaaS出海", freshness="week", count=10)
4. web_search("电商 直播电商 内容平台 数字营销 互联网广告", freshness="week", count=10)
5. web_search("AI办公 AI客服 AI营销 AI电商 AI编程 AI视频 融资", freshness="week", count=10)
6. web_search("大模型API 计费 Token价格 模型调用量 云服务 算力租赁", freshness="week", count=10)
7. web_search("SaaS 企业服务 CRM ERP 协同办公 数据服务 融资", freshness="week", count=10)
```

**第三轮:互联网垂直源补充(并行;直接 fetch + 搜索替代):**

```
8. 晚点 LatePost [low-yield] → web_fetch https://www.latepost.com/ (extractMode="text", maxChars=6000); 同时搜索 site:latepost.com 阿里 腾讯 字节 美团 网易 AI SaaS
9. 界面新闻科技 [active] → web_fetch https://www.jiemian.com/ (extractMode="text", maxChars=6000)
10. 虎嗅 [search-only: 验证页] → $SEARXNG_CMD "site:huxiu.com 互联网 AI应用 SaaS 平台经济" -n 10 --time-range week --format json
11. IT桔子 [search-only: 412] → $SEARXNG_CMD "site:itjuzi.com 融资 SaaS AI应用 企业服务" -n 10 --time-range week --format json
12. 极客公园 [search-only: 403] → $SEARXNG_CMD "site:geekpark.net AI应用 SaaS 互联网" -n 10 --time-range week --format json
13. IT之家/中国证券网/21财经 [替代源] → 搜索 "IT之家 互联网 AI应用 SaaS"、"中国证券网 直播电商 互联网广告"、"21财经 互联网广告 平台经济" 等近7天结果
```

**如果垂直源返回空白/JS 渲染失败/fetch failed,跳过该源,不重试。search-only 源不要直接 fetch 首页,只用 searxng 站内搜索。**

**第四轮:本地互联网专项搜索(2个,searxng):**

```
14. $SEARXNG_CMD "互联网 浙江 杭州 人工智能 大模型 数字经济 平台经济" -n 10 --time-range week --format json
15. $SEARXNG_CMD "浙江 跨境电商 SaaS 游戏 直播电商 AI应用 数字贸易" -n 10 --time-range week --format json
```

**第五轮:iFinD 金融数据补充(3个查询,聚焦近7天互联网行业):**

⚠️ **iFinD 执行说明:**
- **必须执行**,不可跳过。iFinD 能提供上市公司公告语义检索和热点事件,是其他源无法替代的。
- 执行前先在循环外做一次快速探测(如 search_notice 测试 query),确认 `ok: true` 后再执行全部 3 个查询。
- 如果探测失败,检查 `~/.openclaw/skills/ifind-finance-data/` 目录下是否有有效的密钥配置文件。如无配置,跳过本轮并写入 `source_status.md/json`,但不得在周报正文、资料来源或推送摘要中写"iFinD 数据源未配置"等执行日志。

```
16. search_notice(公告语义检索):
    query="人工智能 OR 大模型 OR SaaS OR 云计算 OR 数据要素 OR 平台经济 OR 跨境电商",
    time_start="近7天前日期(YYYY-MM-DD)", time_end="今天日期(YYYY-MM-DD)", size=10
    → 精准抓取近7天互联网/AI/云/SaaS相关上市公司公告(融资/定增/重大合同/并购/项目)

17. search_notice(公告语义检索):
    query="游戏 OR 数字营销 OR 互联网广告 OR 直播电商 OR 企业服务 OR 数据安全 OR 算力",
    time_start="近7天前日期(YYYY-MM-DD)", time_end="今天日期(YYYY-MM-DD)", size=10
    → 精准抓取近7天内容平台/游戏/电商/AI Token生态相关公告

18. search_trending_news(热点事件):
    keyword="互联网", industry_name="计算机", time_scope="近7天", size=5
    → 抓取近7天互联网行业热点事件
```

**iFinD 调用说明:**
- 使用 Node.js 方案(`call-node.js`,无需额外依赖):通过 Node `require` 加载后调用 `call()` 函数,不能直接向脚本喂 JSON。
- 使用 Python 方案:`python3 ~/.openclaw/skills/ifind-finance-data/call.py`
- 优先使用 Node.js 方案(环境要求更低)
- **Node 正确示例:**
```javascript
const { call } = require('/Users/leidongqiao/.openclaw/skills/ifind-finance-data/call-node.js');
const r = await call('news', 'search_notice', {
  query: '人工智能 大模型 SaaS 云计算 数据要素 平台经济 跨境电商',
  time_start: '2026-05-14',
  time_end: '2026-05-21',
  size: 10
});
```
- **Python 正确示例:**
```bash
cd ~/.openclaw/skills/ifind-finance-data && python3 - <<'PY'
from call import call
print(call('news', 'search_notice', {
  'query': '人工智能 大模型 SaaS 云计算 数据要素 平台经济 跨境电商',
  'time_start': '2026-05-14',
  'time_end': '2026-05-21',
  'size': 10
}))
PY
```
- 每次调用后检查 `ok` 字段确认是否成功,失败则跳过该查询
- **search_trending_news 可能 403 Tool not allowed**:该接口受权限限制,返回 403 时跳过并写入 `source_status.md/json`,不得在报告中标注"热点事件接口无权限"。
- **时间参数必须用近 7 天的实际日期(YYYY-MM-DD 格式),不可用模糊描述**
- **行业限定**:query 中必须包含互联网/AI应用/SaaS/平台经济/跨境电商/游戏/数字营销/AI Token等关键词,避免返回无关公告

**按需补充:**
- 从搜索结果中发现重要文章时,点入正文抓取(web_fetch, extractMode="text", maxChars=4000)
- 如需更全面的市场/财经视角,可补充搜索:"互联网 行业 周报"、"AI应用 产业 趋势"、"SaaS 市场 分析"(count=5)

**抓取规则:**
- 核心源优先抓取,但不可因单源失败中断; degraded/disabled 源按健康度规则改用站内搜索替代
- searxng + 垂直源并行执行;Brave web_search 回退时串行执行
- 如果 web_fetch 返回空白/JS 渲染失败,跳过该源,不要重试
- 信息抓取来源必须全部走完;有问题只在 `source_status.md/json` 中备注,不得因部分来源不可用而省略其他来源,也不得把失败原因写入报告资料来源说明
- 关注 **近 7 天内** 发生的事件(周报覆盖一周范围)
- 关注目标区域及周边的互联网、AI、平台型、SaaS、跨境电商企业动态优先

### 第二步:信息跟踪范围

按指令定义的四大维度分类和组织抓取到的信息:

#### 1. 全国行业动态

重点关注:
- 人工智能、生成式AI、大模型、智能体Agent、AI应用、AI搜索、AI办公、AI营销、AI电商、AI内容、AI教育、AI医疗、AI游戏等方向
- 平台经济、数字经济、数据要素、数字贸易、跨境电商、互联网广告、直播电商、内容平台、SaaS、云服务、企业服务软件
- 国家政策、产业政策、监管政策,如生成式AI监管、算法备案、数据安全、个人信息保护、网络安全、跨境数据流动、平台经济监管、数字贸易政策等
- 行业供需变化、用户增长、付费率、广告预算、企业IT预算、模型调用成本、云计算成本、算力价格、API价格变化
- 投融资、并购、上市、发债、重大项目、行业融资热度
- 招投标、中标、大客户合作、政企数字化项目、AI应用落地项目
- 出口、跨境、海外市场、海外App、海外SaaS、跨境电商、AIGC工具出海
- 风险事件:数据合规处罚、算法违规、内容合规、亏损扩大、现金流压力、融资失败、客户流失、平台封禁等

#### 2. 浙江区域动态

重点关注:
- 浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州等地数字经济、人工智能、平台经济、跨境电商、软件信息服务、数据要素、算力基础设施政策
- 杭州人工智能、大模型、云计算、平台经济、电商、直播电商、游戏、内容、SaaS、跨境电商企业动态
- 浙江数字经济核心产业、数字贸易、产业大脑、未来产业、人工智能产业园、算力中心、数据交易、智能制造软件、工业互联网平台
- 专精特新、小巨人、高新技术企业、独角兽、准独角兽、上市后备企业
- 地方重大项目、产业园区、政府引导基金、科技创新券、算力券、数据要素试点、AI应用示范项目等

#### 3. 企业动态

重点关注能转化为银行商机的信号:
- AI产品发布、大模型接入、Agent产品上线、企业级AI应用落地
- Token调用量增长、API调用规模增长、云服务成本上升、算力采购增加
- 获得政企订单、大客户合作、SaaS订阅增长、平台交易额增长
- 融资、上市辅导、定增、发债、并购
- 出海、海外用户增长、海外订阅收入、跨境支付需求
- 应收账款增加、预付云资源费用增加、研发投入增加、亏损扩大、现金流压力
- 成为平台型企业、核心SaaS服务商、AI生态服务商、头部MCN、跨境电商服务商
- 数据合规、内容合规、算法备案、网络安全、知识产权纠纷等风险信号

#### 4. AI Token消费生态链与上下游动态

必须重点分析AI Token消费生态链,不要只看应用层。

- 上游:GPU、AI服务器、IDC、云计算、算力调度、模型训练、数据中心、液冷、网络设备
- 中游:大模型厂商、模型API平台、MaaS平台、AI基础设施平台、向量数据库、数据标注、数据治理、知识库、模型评测、安全审查
- 下游:AI办公、AI营销、AI客服、AI编程、AI设计、AI视频、AI教育、AI电商、AI搜索、AI Agent、行业垂直AI应用
- 消费方:互联网平台、SaaS企业、内容平台、电商平台、游戏公司、跨境电商企业、政企客户、开发者生态
- 计费模式:Token调用量、API调用量、订阅制、按量付费、企业私有化部署、混合云部署、模型推理包、算力包、Agent工作流收费

分析时重点判断:
- 哪些企业Token消耗快速增长
- 哪些企业需要预付云服务费、模型API费、算力资源费
- 哪些企业因AI应用商业化带来收入增长
- 哪些企业因推理成本高导致现金流压力
- 哪些企业适合银行从结算、授信、供应链、跨境支付、现金管理切入
- 哪些核心平台可带动开发者、ISV、服务商、渠道商批量获客

**地域标签:**
- `[浙江]` / `[杭州]` / `[宁波]` / `[绍兴]` 等
- `[上海]` / `[江苏]` / `[南京]` / `[苏州]` / `[南通]` 等
- `[安徽]` / `[其他]` / `[全球]`

**重要性评级:**
- ★★★★★:国家级政策 / 百亿级投资 / 行业拐点 / 头部平台重大变化
- ★★★★:省级政策 / 十亿级融资 / 重大订单 / 大客户合作 / 关键产品商业化
- ★★★:企业级公告 / 产品上线 / 用户数据变化 / 价格变化
- ★★:一般动态
- ★:值得关注但影响有限

### 第三步:分析逻辑
**分析要求:**
- 按照指令定义的闭环进行分析:

```
政策/资讯变化
→ AI时代互联网行业影响
→ 浙江区域机会
→ 企业经营信号
→ AI Token消费生态链传导
→ 企业金融需求
→ 平安银行产品匹配
→ 客户经理营销动作
```

- 「近期政策变动」写法:政策情况要比普通新闻更详细,说明发布主体、发布时间/背景、核心条款/支持方向、约束或机会点;不要在每条政策后都写"影响闭环",而是在该小节末尾统一写一段"综合影响闭环"。
- 「政府规划与产业方向」写法:第一大板块只写国家层面内容;浙江省、杭州市、宁波市、温州市、绍兴市、嘉兴市、湖州市、金华市、台州市等地方规划,统一放到第二部分。
- 「来源引用」写法:正文不要出现"(日期,媒体/网站)""(来源:媒体名)"这类来源括注;日期可自然融入事实表述,来源统一放在报告开头或文末"资料来源"中概括。
- 「资料来源」写法:只列实际采用的信息源名称或类别,例如"新华网科技、36氪、证券时报、浙江省政府公开信息、企业公开披露资料、iFinD公告语义检索等"。严禁写入执行状态、报错、权限、降级和替代说明,例如"iFinD热点事件接口返回403无权限,本期以公告语义检索替代"这类句子必须只留在 `source_status.md/json`,不得进入 Word/Wiki 正文。
- 第一大板块只分析全国层面、国家层面、行业层面动态,**不放浙江内容**。
- 浙江相关政策、规划、项目、产业集群、区域机会统一放入第二部分。

### 第四步:企业推荐判断规则

#### 1. 推荐理由

推荐理由应来自事实信号,例如:
- 企业处于AI应用、AI基础设施、SaaS、平台经济、跨境互联网等景气方向
- 企业受益于国家或浙江数字经济、人工智能、数据要素、跨境电商政策
- 企业位于杭州或浙江优势互联网产业集群
- 企业近期出现AI产品发布、客户增长、政企中标、融资、上市辅导、出海等积极信号
- 企业在AI Token消费生态链中具备关键位置,如模型平台、算力服务商、AI应用入口、企业服务平台、开发者生态平台
- 企业高层或团队具备较强技术、产业、产品、资本、客户资源背景
- 企业具备银行授信、票据、供应链、跨境、现金管理、代发、财富管理等切入空间
- 风险信号相对可控

#### 2. 银行展业机会

必须从企业经营活动推导银行业务机会:
- AI产品研发投入高、人员扩张快 → 普惠金融科创贷、普惠金融信用贷、短贷、平安薪
- 云服务、模型API、Token调用、算力资源预付压力 → 短贷、资产池、数字财资、现金管理
- 采购GPU、服务器、IDC、软硬件设备 → 平安租赁、科技创新和技术更新改造再贷款、项目融资
- 政企项目或大客户项目账期较长 → 付融通、保理、商票保贴、商票e贴、国内信用证
- SaaS订阅、平台交易、广告回款、直播电商回款复杂 → 慧收款、平安结算通、产业结算通、数字财资
- 平台型企业上下游商户、开发者、服务商多 → 供应链金融、平台数字贷、普惠金融场景化方案、订货贷
- 跨境电商、海外App、海外SaaS、AI工具出海 → 跨境支付结算、外币存款、跨境资金管理、人民币国际证+福费廷、平安避险
- 企业融资、并购、上市或股东资金需求 → 债券承销、资本市场融资、并购融资、银团融资、平安证券联动
- 员工规模大、技术人才集中、企业主财富需求明显 → 平安薪、个贷、家族信托、私人理财权益、信用卡权益

### 第五步:企业高层与团队背景要求

企业关键信息中必须体现高层和团队背景,但要简洁。

重点关注:
- 董事长、实控人、CEO、总经理、CFO、CTO、首席科学家、核心创始人、产品负责人
- 教育背景:毕业学校、专业、学位
- 科研背景:导师、实验室、研究方向、论文、专利、开源项目,如公开可查
- 职业经历:曾任职互联网大厂、AI公司、云计算公司、科研院所、上市公司、投资机构等
- 产业资源:是否来自阿里、腾讯、字节、百度、华为、网易、蚂蚁、海康、商汤、旷视、科大讯飞、高校科研院所、政府平台、核心客户体系等
- 银行关注点:其背景是否有助于判断企业技术实力、产品商业化能力、客户资源、融资能力、资本市场潜力或决策链条

注意:
- 只使用公开可查信息。
- 不得虚构个人履历。
- 未披露的信息写"未披露"或"待核实"。
- 不要过度展开个人隐私,重点服务于企业经营判断和银行营销判断。

### 第六步:产品匹配规则

你只能基于本地产品资料(`~/.openclaw/workspace/file/productFile.docx`)中的平安银行产品库推荐产品,不得虚构产品名称、额度、期限、费率或准入条件。

如果产品资料中没有明确参数,写"待沟通"。

产品配置不要堆砌,采用"主推产品 + 配套产品"的方式。每家企业一般推荐2-4类产品即可。

优先使用以下产品方向:

1. **账户与资金管理**
   数字财资、资产池、慧收款、移企付、平安结算通、产业结算通、口袋管家

2. **融资与授信**
   - 短贷:平安透、网上自由贷
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

### 第七步:生成周报(双版本输出)

**生成两种格式的周报,内容结构一致,输出方式不同:**

#### 版本A:Word 版(行业分析指令格式)

按以下完整结构生成详细行业分析报告,使用华文楷体:

```
# 互联网行业商机周报

## 一、行业动态与发展总结
(仅全国/国家/互联网行业层面,不含浙江内容)

### 1. 近期政策变动

(政策情况要写详细:发布主体/时间背景/核心条款/支持方向/约束要求;本小节末尾统一写一段"综合影响闭环",不要每条政策各写一个闭环)
梳理近期国家部委、行业主管部门发布的互联网、人工智能、数据要素、平台经济、网络安全、算法治理、数字贸易、跨境数据、科技创新等政策变化。

要求：
- 不要简单罗列政策标题。
- 要说明政策对互联网行业、AI应用生态、AI Token消费生态链的影响。
- 要说明可能带来的银行业务机会。
- 如政策发布日期、发布部门、政策名称可查，应简要注明。
- 浙江省及浙江地市政策不要放在这里，统一放到第二部分。

### 2. 政府规划与产业方向

(只写国家层面的产业规划、重大项目规划、重点产业布局和未来产业方向)
只梳理国家层面的产业规划、重大项目规划、重点产业布局和未来产业方向。

重点关注：
- 国家级人工智能、数字经济、数据要素、平台经济、数字贸易规划
- 国家战略性新兴产业和未来产业中的人工智能、云计算、大数据、软件服务方向
- 全国层面的算力基础设施、数据基础设施、模型应用、科技创新政策工具
- 对互联网企业AI化、算力采购、模型调用、数据资产化、出海和融资的影响

### 3. AI时代互联网行业发展趋势

总结互联网行业在AI时代的发展阶段、景气度、需求变化、商业模式变化、竞争格局和资本市场表现。

要求说明：
- 行业处于上行、分化、调整还是出清阶段
- AI正在改变哪些互联网场景，如搜索、广告、电商、办公、客服、内容、教育、游戏、企业服务
- 哪些细分赛道更有机会，如AI应用、AI Agent、AI SaaS、AI营销、AI视频、跨境AI工具、企业级AI服务
- 哪些企业类型更值得银行关注
- 哪些风险需要提前识别，如监管合规、数据安全、模型成本、商业化不及预期、现金流压力

### 4. AI Token消费生态链与上下游动态

分析全国或行业层面的AI Token消费生态链变化。

重点判断：
- 上游算力、GPU、云服务、IDC、AI服务器、数据服务价格或供需变化
- 中游大模型、MaaS平台、API平台、数据治理、模型安全、Agent开发平台变化
- 下游AI应用、SaaS、内容平台、电商平台、广告营销、游戏、跨境工具的需求变化
- 哪些环节Token消耗增长最快
- 哪些环节现金流压力最大
- 哪些环节适合供应链金融、票据、保理、订单融资、短贷、现金管理、跨境结算等产品切入

## 二、浙江地区动态与区域机会

### 1. 浙江政策与政府规划

梳理浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州等重点城市近期关于人工智能、数字经济、平台经济、数据要素、跨境电商、软件服务、算力基础设施、科技创新、产业园区等政策和规划。
要求：
- 说明政策或规划对本地互联网企业、AI企业、平台型企业、跨境电商企业的影响。
- 说明可能带来的银行授信、票据、供应链、跨境、现金管理、代发、财富管理等机会。
- 如政策发布日期、发布部门、政策名称可查，应简要注明。

### 2. 浙江重点产业与区域机会

重点关注：
- 杭州AI、大模型、云计算、平台经济、电商、直播电商、游戏、内容、SaaS、跨境电商生态
- 浙江数字经济核心产业、软件信息服务、数据要素、数字贸易、工业互联网、产业互联网平台
- 浙江“415X”先进制造业集群中的数字化、智能化、工业软件、AI赋能制造机会
- 专精特新、小巨人、高新技术企业、独角兽、准独角兽、上市后备企业
- 人工智能产业园、数字经济园区、跨境电商综试区、产业基金、招商落地项目

要求说明：
- 哪些产业集群正在释放AI化、平台化、出海化机会
- 哪些区域更值得客户经理重点扫客
- 哪些企业类型更可能产生融资、供应链、跨境、现金管理或代发需求

### 3. 浙江AI Token消费生态链与上下游动态

分析浙江本地AI Token消费生态链和互联网上下游变化：

- 上游：云服务、算力、服务器、IDC、数据服务、软件开发服务
- 中游：大模型、AI平台、SaaS、企业服务、开发者工具、数据治理企业
- 下游：电商、直播、跨境电商、游戏、内容、广告营销、教育、医疗、制造业AI应用
- 哪些环节Token调用、云资源、研发投入、人员扩张带来资金占用
- 哪些环节适合批量获客或供应链金融切入
- 哪些核心平台企业可以带动开发者、商户、服务商、渠道商批量营销

### 4. 银行展业机会(3-5条)

用3-5条总结浙江地区最值得平安银行杭州分行关注的互联网行业展业机会。

要求：
- 必须结合浙江本地政策、互联网产业集群、AI企业动态和AI Token消费生态链变化。
- 必须说明对应的银行业务机会。
- 尽量落到具体产品方向，如科创贷、短贷、数字财资、慧收款、平安结算通、产业结算通、供应链金融、平台数字贷、跨境结算、平安避险、平安薪、财富管理等。

## 三、重点企业推荐

选择3-8家最值得客户经理跟进的浙江互联网、AI、平台经济、数字经济、跨境互联网或相关生态企业。每家企业按照以下模板输出。
⚠️ **硬性结构要求（不可压缩/不可省略）**：每一家企业必须严格保留下列字段和小标题；不得把“企业关键信息”合并成一段，也不得把“推荐理由”“银行展业机会”改写成无结构长段。若资料不足，字段仍保留，并写“未披露/待核实”。生成完成后必须逐家自检：是否包含【推荐等级、所属行业、所在地区、产业链位置、推荐方向、企业关键信息-基本情况、企业关键信息-高层与团队背景、企业关键信息-银行关注点、推荐理由、银行展业机会、推荐产品组合、客户经理切入话术、风险提示】；缺一项必须返工。
### 企业名称:XXX公司

**推荐等级:** 高 / 中 / 低
**所属赛道:** AI应用 / 大模型 / AI SaaS / 云计算 / 平台经济 / 电商 / 跨境电商 / 游戏 / 内容 / 数字营销 / 企业服务 / 数据服务等
**所在地区:**
**产业链位置:** 上游算力与数据 / 中游模型与平台 / 下游应用与场景 / 生态服务商
**推荐方向:** 科创融资 / 流动资金 / 供应链金融 / 跨境结算 / 票据 / 现金管理 / 代发 / 财富管理 / 综合金融等。

**企业关键信息:**
- **基本情况:** 主营业务、成立时间、所在地、企业性质、商业模式、产业链位置。
- **高层与团队背景:** 董事长/实控人/CEO/CFO/CTO/首席科学家/核心创始人的教育背景、学校、导师、职业经历、产业资源;未公开标注"未披露/待核实"。
- **银行关注点:** 管理层背景对企业技术实力、产品商业化能力、客户资源、融资能力、资本运作或决策路径的影响。

⚠️ **企业关键信息排版硬规则:**「基本情况」「高层与团队背景」「银行关注点」三项必须各自单独成段/单独成列表项,不得写成一整段连续文本。

**推荐理由:**
- 基于政策、行业、浙江区域、企业动态、AI Token消费生态链位置、团队背景等事实信号写2-4点。
- 必须说明该企业为什么值得客户经理优先跟进。
- 说明为什么值得客户经理优先跟进(好在哪里、机会在哪里、现在为什么值得看)。

**银行展业机会:**
- 从企业经营变化推导银行业务机会。
- 说明企业在科创融资、流动资金、云资源预付、模型API成本、算力采购、应收账款、平台结算、跨境收付、现金管理、代发、财富管理等方面的潜在需求。
- 必须讲清楚“企业经营场景 → 金融需求 → 平安银行可切入产品”。

**推荐产品组合:**
不用表格。用一段自然语言总结,必须包含"主推产品 + 配套产品 + 切入理由"。每家企业一般推荐2-4类产品即可,避免堆砌。例如:建议以【主推产品】切入,解决企业【核心经营/资金场景】;配套使用【产品1、产品2】,用于【具体理由】。资料未披露的额度、期限、费率或准入条件写"待沟通"。

**客户经理切入话术:**
简短、自然、可直接拜访使用的话术,围绕AI化、商业化、现金流、客户回款、云资源成本、出海或平台生态切入,避免生硬推销。

**风险提示:**
数据合规、算法备案、内容合规、知识产权、客户集中度、研发费用、亏损情况、应收账款、云资源成本、融资进度、核心团队稳定性等;无明显风险写"暂无明显公开风险,仍需结合征信、流水、财报、合同、客户结构和实地尽调确认"。

## 四、客户经理行动建议

用3-5条给出当天或近期最值得执行的动作,例如:
- 优先拜访哪些互联网或AI企业
- 从哪个业务场景切入,如云资源预付、AI产品研发、政企项目回款、平台结算、跨境收款、代发薪
- 先聊哪些经营问题,如Token消耗成本、客户回款周期、SaaS续费率、海外收入、研发投入、数据合规
- 准备哪些材料,如科创贷方案、短贷方案、数字财资方案、跨境结算方案、平台结算方案、平安薪方案
- 需要内部联动哪些产品经理或审批资源
```

**Word 输出要求:**
- **固定保存目录**:`/Users/leidongqiao/.openclaw/workspace/workspace-WEBresearcher/reports/web-weekly/`(即 Web Researcher 工作空间的 `reports/web-weekly/`),不得保存到其他目录;如目录不存在先创建。
- **同步到 codex uploader 目录:** Word 文件生成后,先清空 `/Users/leidongqiao/Documents/codex project/local-uploader/data/互联网` 目录下的所有文件(目录本身不动),然后将 Word 周报文件拷贝到该目录。
- 文件名格式:`<REPORT_BASENAME>.docx`;默认 `REPORT_BASENAME=$WEEKLY_TITLE_PREFIX-YYYYMMDD`(如 `internet-weekly-YYYYMMDD`)。如果本地已存在同名 `.docx` 或 `.md`,必须递增为 `$WEEKLY_TITLE_PREFIX-YYYYMMDD_v2`、`_v3` 等,并用最终 basename 统一 Word 文件名、Drive 上传名、Wiki 标题、本地 Markdown 副本。
- 字体使用华文楷体
- **Word 样式优化**:Word 版必须是干净的报告排版,不要把 Markdown 原始符号带入正文;生成 docx 时需去掉 `- **`、`**`、表格竖线等 Markdown 标记。普通段落用自然段,企业信息可用短段落或简洁项目符号,但不要让每段前面都出现 `- **`。推荐产品组合不得用表格。

#### Word 下载链接

Word 文件上传飞书 Drive 后获取 `file_token`,拼接下载链接:

```
https://qcn8k445rrbc.feishu.cn/file/<file_token>
```

**使用方法:**
1. 上传文件:`lark-cli drive +upload --profile $BOT_PROFILE --as bot --file "./文件名.docx" --name "文件名.docx"`
2. **直接从返回结果中取 `url` 字段作为下载链接**,不要手动拼接,避免域名错误。
3. 将该链接写入 wiki 正文开头和推送摘要中

#### 版本B:飞书 wiki 版(知识库存档格式)

- 内容与 Word 版结构一致,适配飞书文档 Markdown 格式
- 通过第九步写入知识库
- Wiki 节点标题必须等于最终 `REPORT_BASENAME`;搜索/去重 Wiki 时也以最终 `REPORT_BASENAME` 为准。
- 本地 Wiki Markdown 副本必须保存为 `reports/web-weekly/<REPORT_BASENAME>.md`,与 Word basename 完全一致。
- wiki 正文开头(标题下方、覆盖周期/资料来源前)必须写入:`**Word版下载：** https://.../file/...`
- ⚠️ **wiki 正文中的 Word 下载链接必须用纯 URL 文本**,不要写成 `<https://...>`。
- ⚠️ **飞书 wiki 排版硬规则:不要依赖单换行。** 飞书文档会把普通 Markdown 单换行合并,导致字段黏在一行。
- ⚠️ **企业元数据必须用列表格式**,固定格式如下:
  ```markdown
  - **推荐等级：** 高
  - **所属赛道：** XXX
  - **所在地区：** 杭州
  - **产业链位置：** 中游模型与平台/下游应用与场景
  - **推荐方向：** XXX
  ```
- ⚠️ **企业关键信息也必须用列表格式并逐项换行**:
  ```markdown
  **企业关键信息:**
  - **基本情况:** XXX
  - **高层与团队背景:** XXX
  - **银行关注点:** XXX
  ```
- ⚠️ **Word 与 Wiki 格式分离**:Word 版去掉所有 Markdown 标记;Wiki 版保留完整 Markdown。写入 wiki 后必须 fetch 回来抽查一次,重点检查是否存在 `推荐等级.*所属赛道`、`所属赛道.*所在地区`、`所在地区.*产业链位置`、`产业链位置.*推荐方向` 这类同一行黏连;发现即重写修复。

### 第八步:更新/追加商机到表格

从第七步周报的「四、客户经理行动建议」中提取需要跟进的浙江互联网、AI、平台经济、数字经济、跨境互联网或相关生态企业,写入「商机挖掘」电子表格。

**🔴 关键规则(必须严格遵守):**
- **从行动建议提取**:从周报「四、客户经理行动建议」中提取明确提及的浙江本地企业,这些是需要客户经理优先跟进的商机
- **只写入目标区域本地企业**,非目标区域企业一律不写入表格
- **写入前必须去重**:先读取 A 列,用「规范化核心简称精确匹配」判断是否已存在
- **禁止重复写入同一企业**:同一核心简称只保留一行,已有行则更新,无则追加

**去重逻辑(严格执行):**

1. 先将括号统一为全角:`(` → `（`, `)` → `）`
2. 去掉所有 `（...）` 修饰(地域、股票代码、备注等),得到**核心简称**
3. 对已有 A 列每个名称也做同样规范化
4. 将新商机核心简称与已有核心简称做**完全匹配**(==),不是包含匹配
5. 如果核心简称相同 → **原地更新该行**,**保持A列原名称不变**,只更新 B~J 列
6. 如果没有任何已有行的核心简称匹配 → **追加新行**

**别名映射(补充):**
- 建议维护常见别名,如 `群核科技`/`杭州群核信息技术有限公司`、`DeepSeek`/`深度求索`、`涂鸦智能`/`杭州涂鸦科技有限公司`、`网易杭州`/`网易(杭州)网络有限公司` 等。

**写入流程(严格执行):**
1. 读取 A 列全量数据
2. 对 A 列每个非空名称做规范化:去掉括号内容,得到**已有核心简称列表**
3. 对本次商机先去重:按核心简称合并同名企业,每个核心简称只保留一条
4. 对每个去重后的商机:提取核心简称 → 精确匹配 → 匹配到则更新,未匹配则追加
5. ⚠️ **更新已有商机时,创建日期(I列)必须更新为当前日期(YYYY-MM-DD)**
6. ⚠️ **如果匹配到的已有行状态为终态(closed/已关闭/已落地),则跳过该行,不更新**
7. ⚠️ **新增商机的状态列统一填写「待联系」,不要写 active/open**
8. ⚠️ **更新已有商机时,状态列保持不变,不修改**
9. ⚠️ **写入完成后,只对 A 列非空的有效业务行进行时间倒序重排。表格默认空行不是业务数据,不得把 200+ 空行一起写回。**

**字段顺序**:客户名称、行业/领域、触发信号、优先级、推荐方案、预计金额、联系人、状态、创建日期、备注

**⚠️ 表格排序与清理(每次写入后必须执行):**

**全部使用 lark-cli 完成,不用 Python urllib 直接调 API(避免 SSL 代理问题)。**

```bash
# 1. 读取表格 row_count,再读取原始快照
ROW_COUNT=$(lark-cli sheets +info --profile $BOT_PROFILE --as bot \
  --spreadsheet-token "$SPREADSHEET_TOKEN" \
  --jq '.data.sheets.sheets[0].grid_properties.row_count')

lark-cli sheets +read --profile $BOT_PROFILE --as bot \
  --spreadsheet-token "$SPREADSHEET_TOKEN" \
  --range "$SHEET_ID!A1:J${ROW_COUNT}" \
  --jq '.data.valueRange.values' > /tmp/sheet_data.json

# 2. Python 排序(只处理 A 列非空有效业务行,不调 API)
python3 << 'PYEOF'
import json, subprocess, os
with open("/tmp/sheet_data.json") as f:
    rows = json.load(f)
header = rows[0]
data_rows = []
for r in rows[1:]:
    if len(r) > 0 and r[0] and str(r[0]).strip():
        row = list(r)[:10]
        row += [""] * (10 - len(row))
        data_rows.append(row)
data_rows.sort(key=lambda x: str(x[8] or '') if len(x) > 8 else "", reverse=True)
end_row = 1 + len(data_rows)
values_str = json.dumps(data_rows, ensure_ascii=False)
with open("/tmp/sheet_end_row.txt", "w") as f:
    f.write(str(end_row))
print(f"排序完成:{len(data_rows)}行,end_row={end_row}")
result = subprocess.run(
    ["lark-cli", "sheets", "+write", "--profile", os.environ["BOT_PROFILE"], "--as", "bot",
     "--spreadsheet-token", os.environ["SPREADSHEET_TOKEN"],
     "--range", f"{os.environ['SHEET_ID']}!A2:J{end_row}",
     "--values", values_str],
    capture_output=True, text=True
)
print("Write:", "OK" if '"ok": true' in result.stdout else result.stdout[:300])
PYEOF

# 3. 清理有效区后的残留旧业务行/空白行
# 优先删除 end_row 之后的多余默认行;如 delete-dimension 不适合当前表格,至少清空 A:J 尾部区域。
END_ROW=$(cat /tmp/sheet_end_row.txt)
MAX_ROWS=$(lark-cli sheets +info --profile $BOT_PROFILE --as bot --spreadsheet-token "$SPREADSHEET_TOKEN" \
  --jq '.data.sheets.sheets[0].grid_properties.row_count')
if [ "$MAX_ROWS" -gt "$END_ROW" ]; then
  lark-cli sheets +delete-dimension --profile $BOT_PROFILE --as bot \
    --spreadsheet-token "$SPREADSHEET_TOKEN" \
    --sheet-id "$SHEET_ID" \
    --dimension ROWS \
    --start-index $((END_ROW + 1)) \
    --end-index $MAX_ROWS
fi
```

⚠️ **关键说明:**
- **所有飞书 API 操作统一走 lark-cli**(sheets/drive/docs/wiki),不用 Python urllib
- lark-cli 会自动处理代理和认证,无需手动获取 tenant_access_token
- `sheet_before.json` 保存的是原始快照,但真正参与合并/排序/写回的只能是 A 列非空有效业务行
- 写入范围必须是 `A2:J<END_ROW>`,其中 `END_ROW=1+有效业务行数`;不得把默认 200+ 空行作为数据写回
- `+delete-dimension` 的 `--end-index` 必须 ≤ sheet 实际行数,先通过 `+info` 获取
- 排序后必须清理 end_row 之后的旧业务行/空白行,否则会残留旧数据;但不要为了“保险”重写全表空行

### 第九步:写入知识库(飞书 wiki 版)

**写入内容:第七步版本B(飞书 wiki 版),结构与 Word 版一致,适配飞书 Markdown 格式。**

**重要:每次生成先确定唯一 `REPORT_BASENAME`,Wiki 标题与 Word/Markdown 文件 basename 一致。若本地已存在同名文件,使用 `_v2`、`_v3` 后缀,不要覆盖旧文件。**

**Word 下载链接位置要求:**Word 版上传飞书 Drive 后直接从返回结果取 `url` 字段作为下载链接;wiki 正文开头必须写入 `**Word版下载：** <下载链接>`,推送摘要中的「Word」也必须使用该下载链接。

**🔴 关键规则(必须严格遵守):**
- 文档必须创建在知识库**根目录**(`parent_node_token` 为空字符串),**不能**创建在「首页」或其他节点下面
- 必须使用**机器人身份**(`--as bot`)创建,创建者显示为机器人
- **⚠️ `--as bot` 默认使用 lark-cli 配置的默认应用(通常是 ai_bot),不是当前 agent 自己的 bot。必须使用 `--profile $BOT_PROFILE --as bot`**

**步骤:**

0. **确定排序位置(商机挖掘节点之后,时间倒序)**:
   列出知识库根目录所有节点,「商机挖掘表格」节点默认就是根目录列表第一个。新周报文档应排在商机挖掘表格之后。⚠️ `lark-cli wiki +node-create` **不支持 `--insert-after` 参数**,创建时只需指定 `--space-id` 即可(默认在根目录)。创建后用 `wiki +move` 调整顺序不可行(也支持不了 insert-after)。实际效果是周报按创建时间顺序排列,不影响使用。

1. **列出知识库所有节点,查找是否已有同名文档(搜索全部节点,不限根目录!)**:
   ```bash
   lark-cli wiki nodes list --params '{"space_id":"$WIKI_SPACE_ID","page_size":50}' --profile $BOT_PROFILE
   ```
   从返回结果中搜索 title 为 `$REPORT_BASENAME` 的节点,提取 `obj_token` 和 `node_token`。
   ⚠️ **必须搜索所有节点**(不限 `parent_node_token`),否则第一次创建时可能被放在「首页」下,第二次搜不到就重复创建了!
   ⚠️ **如果找到多个同名文档**,选 `obj_edit_time` 最新的那个,用 `docs +update` 覆盖;其余旧节点只记录到过程备注,不要在周报任务中尝试删除。当前 `lark-cli drive files patch` 对应飞书 `drive.files.patch` 仅支持改标题(`new_title`),不支持 `trash_type` 删除;误用会让 cron 标记 error 并把错误通知推到群里。
   如确需后续人工清理重复标题,只能用当前 schema 支持的改名方式,并且必须捕获失败、不影响周报成功摘要:
   ```bash
   set +e
   LARK_CLI_NO_PROXY=1 ~/.npm-global/bin/lark-cli drive files patch \
     --profile "$BOT_PROFILE" --as bot \
     --params "{\"file_token\":\"$OLD_OBJ_TOKEN\",\"type\":\"docx\"}" \
     --data "{\"new_title\":\"${REPORT_BASENAME}_duplicate_${RUN_DATE}\"}"
   PATCH_STATUS=$?
   set -e
   echo "duplicate_rename_status=$PATCH_STATUS" >> /tmp/web-weekly-${RUN_DATE}/source_status.md
   ```

2. **如果找到同名文档**:
   - 使用 `lark-cli docs +update --doc <obj_token> --profile $BOT_PROFILE --as bot --mode overwrite --markdown '<内容>'` 覆盖内容
   - 输出文档链接:`https://www.feishu.cn/wiki/<node_token>`

3. **如果未找到同名文档**:
   - 使用以下命令以**机器人身份**创建(默认在知识库根目录):
     ```bash
     lark-cli wiki +node-create --profile $BOT_PROFILE --as bot \
       --space-id "$WIKI_SPACE_ID" \
       --title "$REPORT_BASENAME" \
       --obj-type "docx"
     ```
     ⚠️ **不要使用 `--insert-after`**,lark-cli 不支持该参数,会导致 `Error: unknown flag: --insert-after` 退出码1,进而导致整个 cron job 标记为 error,delivery 推送错误日志。
   - 从返回结果提取 `obj_token`(用于内容更新)和 `node_token`(用于 URL)
   - 使用 `lark-cli docs +update --doc <obj_token> --profile $BOT_PROFILE --as bot --mode overwrite --markdown '<内容>'` 写入内容
   - 输出文档链接:`https://www.feishu.cn/wiki/<node_token>`
   - ⚠️ 创建后用 `wiki nodes list` 确认 `parent_node_token`,如果不在根目录,用 `wiki +move --profile $BOT_PROFILE --as bot --node-token <node_token> --target-space-id "$WIKI_SPACE_ID"` 移回根目录。

**禁止**使用 `feishu_wiki_space_node` 工具(该工具可能将文档创建在首页下),必须使用 `lark-cli wiki +node-create --profile $BOT_PROFILE --as bot --space-id` 命令。

### 第十步:推送至群聊(极简概要 + 链接,200字左右)

**🔴 关键规则:推送到群聊的内容是极简概要和链接,不是全文!手机端必须能一次读完。**

**长度限制:正文控制在 200 字左右(不含链接 URL),最多不超过 300 字。**

推送至群聊的消息格式如下:

```markdown
📌 【互联网】商机周报·浙江｜YYYY.MM.DD-MM.DD
🔥 主线：XXX、XXX、XXX
🏠 浙江机会：XXX
🏢 优先跟进：XXX、XXX、XXX
🎯 切入方向：XXX/XXX/XXX

Word：https://qcn8k445rrbc.feishu.cn/file/XXXX
Wiki：https://www.feishu.cn/wiki/XXXX
商机表：https://xxx.feishu.cn/sheets/XXXX
```

#### 10.1 同步至工作空间

推送前,先把要推送的极简摘要写一份到本地工作空间:

1. **清空目录:**删除 `reports/summary/` 目录下所有文件(目录本身保留)。
2. **写入文件:**将即将推送的群聊摘要内容写入 `reports/summary/WEB-summary.md`。

```bash
# 清空目录
rm -f ~/.openclaw/workspace/workspace-WEBresearcher/reports/summary/*
# 写入摘要
echo '<摘要内容>' > ~/.openclaw/workspace/workspace-WEBresearcher/reports/summary/WEB-summary.md
```

#### 10.2 推送至群聊

**推送内容要求:**
- 行业动态:只提炼 2-3 个主线关键词,不逐条列新闻
- 浙江区域:只写 1 句机会集中方向
- 企业推荐:只列重点 3 家以内,不写推荐理由
- 行动建议:只写 1 句“优先跟进 + 切入方向”
- 样式要求:正文四行呈现,固定为「🔥 主线 / 🏠 浙江机会 / 🏢 优先跟进 / 🎯 切入方向」
- Word 周报飞书 Drive 下载链接(不要只放本地路径)
- 周报 wiki 存档链接
- 商机挖掘表格链接(sheets URL)
- **不要**输出周报全文内容
- **不要**使用长分隔线、长清单、TOP5-8逐条新闻、企业推荐理由、执行日志

**🔒 群聊最终回复锁(防止误推全文/日志):**
1. 任何会被 delivery / cron / 群聊看到的最终 assistant 回复,**必须且只能**使用本步骤的「200字左右极简概要 + 三个链接」格式。
2. **禁止**把以下内容作为最终群聊推送:执行日志、完成情况清单、工具调用结果、文件本地路径、Markdown/wiki 源稿、Word 正文全文、调试说明。
3. 推送前必须自检 4 项,缺一不可:
   - 已压缩为 2-3 个主线关键词,不是 TOP 新闻长清单;
   - Word 链接是飞书 Drive/file 下载链接,不是本地路径;
   - wiki 链接是 `https://www.feishu.cn/wiki/...`;
   - 商机表格链接是 sheets URL。
4. 如果 Word Drive 链接、wiki 链接或 sheets 链接任一缺失,**不要推送群聊摘要**;先补齐链接,再输出第十步模板。

### 第十一步:表达风格

面向客户经理,不面向学术研究。写作风格规则:

1. **面向客户经理**:语言专业、直接、可执行,不是学术研究。
2. **不堆砌新闻**:不要简单罗列新闻标题,要说明影响和机会。
3. **不堆砌产品**:产品配置不要堆砌,采用"主推产品 + 配套产品"方式,每家企业一般推荐2-4类;重点企业推荐中的「推荐产品组合」用一段话总结,不用表格。
4. **企业重点讲清4件事**:推荐理由 → 银行展业机会 → 推荐产品组合 → 客户经理怎么开口。
5. **简要呈现企业基本信息**:不需要机械罗列全部工商信息。
6. **帮助形成判断**:输出要帮助客户经理回答--今天该联系谁、为什么联系、聊什么产品、怎么切入。
7. **Word输出**:字体使用华文楷体;版式要像正式报告,去掉 Markdown 原始符号(尤其是 `- **`、`**`、表格分隔线),避免每段前面都有项目符号和加粗标记。
8. **正文去来源括注与执行日志**:正文面向客户经理,不写"(5月14日,杭州网/人民网浙江)""(iFinD新闻,5月20日)"等来源括注;证据来源统一在"资料来源"中概括即可。正文和资料来源都不得出现接口错误、权限不足、抓取失败、替代源、调试过程等执行日志。

### 第十二步:输出完成

输出完成后,由调用方(定时任务等)通过 delivery 配置推送到飞书群,无需在 skill 内执行推送。

## 特殊场景

### 信息源全部失败

如果所有 web_fetch 都失败或返回空白:
1. 不要编造内容
2. 告知用户信息源抓取失败,建议手动提供素材
3. 或基于已知信息生成最小化版本并标注"信息有限"

### 用户要求手动生成

用户说"生成上周周报"时,同样执行以上流程。

## 注意事项

1. **不编造数据**:所有企业、金额、日期必须来自爬取的实际信息
2. **产品资料**:产品推荐必须基于 `~/.openclaw/workspace/file/productFile.docx`,不得虚构产品名称、额度、期限、费率或准入条件
3. **地域限制**:本地行业动态、行动清单、企业动态仅限浙江本地企业;非互联网/AI/平台经济/数字经济/跨境互联网相关企业动态不纳入本地行业动态
4. **禁止推荐不合规业务**
5. **双版本输出**:Word 版用于详细报告(华文楷体),wiki 版用于知识库存档(飞书 Markdown 格式),内容结构一致
6. **知识库标题**:必须等于最终 `REPORT_BASENAME`,默认 `$WEEKLY_TITLE_PREFIX-YYYYMMDD`(如 `internet-weekly-YYYYMMDD`);如果本地重名使用 `_vN`,Wiki 标题也同步使用同一个 `_vN`。
7. **知识库写入**:必须使用 `lark-cli wiki +node-create --profile $BOT_PROFILE --as bot --space-id $WIKI_SPACE_ID` 创建,禁止使用 `feishu_wiki_space_node` 工具。去重时**搜索全部节点**(不限 parent_node_token),避免重复创建
8. **群聊推送**:推送概要 + 链接,不是全文
9. **商机挖掘表格**:数据来源为周报「四、客户经理行动建议」中提及的企业。写入前必须去重,只写浙江本地企业。更新已有商机时日期必须更新为当天。写入后只对 A 列非空有效业务行按时间倒序重排,不要把默认 200+ 空行作为数据重写。
10. **搜索优先 searxng**:searxng 无 API 限流、无布尔 OR 语法问题。`python3 ~/.openclaw/skills/searxng/scripts/searxng.py search "query" -n 10 --time-range week --format json`。Brave web_search 仅作为备用,且不用 OR 语法。
11. **代理配置**:Gateway 进程需配置代理环境变量(`HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:7890`),否则 Brave API 连接超时。lark-cli 会检测到代理变量并发出警告,不影响功能。
12. **Word 下载链接**:Word 文件上传飞书 Drive 后直接从返回结果取 `url` 字段(如 `https://qcn8k445rrbc.feishu.cn/file/XXX`),不要手动拼接域名;将该链接写在 wiki 正文开头和推送摘要中。
13. **Word 输出**:字体使用华文楷体,固定保存到 `/Users/leidongqiao/.openclaw/workspace/workspace-WEBresearcher/reports/web-weekly/`,文件名格式 `<REPORT_BASENAME>.docx`;保存前检查本地是否重名,不得覆盖。生成后上传飞书 Drive;Word 正文必须清理 Markdown 标记,推荐产品组合不用表格。
14. **正文来源格式**:周报正文去掉媒体/网站来源括注;不要出现"（日期，来源）""（来源：XXX）"。资料来源只在报告开头或文末统一概括。
15. **报告内禁止执行日志**:Word/Wiki 正文、资料来源、推送摘要中禁止出现接口报错、权限不足、抓取失败、替代源说明、调试过程。例如不得写"iFinD热点事件接口返回403无权限，本期以公告语义检索替代。"这类句子;只能写进 `source_status.md/json`。
16. **iFinD 必须执行**:不可跳过。先在循环外做一次快速探测确认环境可用,再执行全部 3 个查询;权限不足或接口不可用时只记录到 `source_status.md/json`。
17. **信息源必须全量走完**:本 skill 列出的核心源、搜索、替代源、本地专项、iFinD 都必须执行;失败、空结果、低质和权限问题只做过程备注,不得提前停止。
18. **所有飞书 API 统一走 lark-cli**:sheets/drive/docs/wiki 操作全部用 lark-cli,不用 Python urllib 直接调 API。
19. **lark-cli 文件上传路径**:`--file` 必须是当前工作目录下的相对路径,不支持绝对路径。操作前先 `cd` 到文件所在目录。
20. **lark-cli wiki 创建后需检查位置**:`wiki +node-create` 默认可能放在「首页」子节点下,创建后需检查 `parent_node_token`,如在子节点下需 `wiki +move` 移回根目录。

## 踩坑记录(供后续优化参考)

1. **Brave 不支持布尔 OR 语法**:`"A" OR "B"` 被当精确匹配。→ 改用 searxng,或 Brave 用空格分隔关键词。
2. **同花顺/经济观察网返回内容少或 JS 渲染严重**。→ 不作为必抓源。
3. **部分互联网垂直源可能空白或需登录**。→ 跳过并用搜索补充。
4. **纯AI技术内容会稀释商机判断**。→ 仅保留商业化、API价格、Token消费、企业采购、融资和浙江产业机会相关内容。
5. **iFinD 被跳过未执行**。→ 必须先探测再执行。
6. **Python urllib SSL 证书验证失败**。→ 全部改用 lark-cli。
7. **lark-cli 上传文件要求相对路径**。→ 先 `cd` 到目录再用 `./文件名`。
8. **wiki 创建后自动嵌套在子节点下**。→ 创建后需 `wiki +move` 移回根目录。
9. **Word 下载链接格式**:`https://qcn8k445rrbc.feishu.cn/file/<file_token>`(租户域名 qcn8k445rrbc,不要用 open.feishu.cn)。
10. **未并行执行搜索**。→ searxng 支持并行,Brave 需串行。

## 文件路径

```
skills/web-weekly-report/
├── SKILL.md                    # 本文件
└── references/
    └── (预留)
```

## 关键参数速查

```
# lark-cli profile
BOT_PROFILE: "web_bot"

# 商机挖掘表格
spreadsheet_token: ZvM9scRdph9aqzthwPAchTJ8nTe
sheet_id: c41411
去重查询: c41411!A:A(只查客户名称列)
追加写入: c41411!A:J

# 互联网行研知识库
space_id: 7637062266134760425
space_name: 互联网行研
节点标题: <REPORT_BASENAME>

# 周报输出
weekly_title_prefix: internet-weekly
word_report_dir: /Users/leidongqiao/.openclaw/workspace/workspace-WEBresearcher/reports/web-weekly/
word_file_name: <REPORT_BASENAME>.docx
wiki_markdown_name: <REPORT_BASENAME>.md

# 地域
region: 浙江
region_cities: 杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州、丽水、衢州、舟山
```
