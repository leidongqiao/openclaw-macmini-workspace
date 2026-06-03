---
name: ai-weekly-report
description: |
 生成行业研究周报(双版本:Word详细报告 + 飞书wiki),每周爬取多源行业研究内容,
 去重筛选、转化为银行商机清单,推送至飞书群。每周五执行,商机/行动清单/企业动态仅限浙江本地。
---

# AI 行业研究周报生成 Skill

每周直接爬取多源行业研究内容,生成双版本周报(Word详细报告 + 飞书wiki知识库存档),推送至飞书群。

## 何时使用

- 用户说"生成周报"、"出周报"、"AI 周报"、"行业周报"
- 定时任务触发
- 补发历史周报

## 核心原则

1. **直接爬取**:每周从多源爬取行业研究内容(行业报告、市场分析、技术趋势、政策动态)
2. **地域聚焦**:**本地行业动态、行动清单仅限浙江本地**(杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山);长三角异动作为补充参考
3. **TOP5-8精选**:本周最具实质影响的5-8条要闻
4. **商机汇总**:按企业维度汇总本周可介入的商机
5. **双版本输出**:Word 版(详细报告) + wiki 版(知识库存档),内容结构一致
6. **独立运行**:周报由本 skill 独立负责

## Token 优化原则

- **搜索优先级**:优先使用本地 SearXNG 搜索(无 Brave 1次/秒限流),Brave `web_search` 作为备用;用关键词精准搜索行业信息,比爬取大站再筛选高效得多
- **web_fetch 用 text 模式**(`extractMode: "text"`),比 markdown 模式更精简
- **maxChars=6000**,够提取文章摘要,不需要更大
- **表格只查 A 列**(`28609d!A:A`)去重,不查全表
- **lark-cli 命令按预定义参数执行**,不要反复试错
- **正文点入按需**:只在搜索结果发现重要线索时点入正文(maxChars=4000)

## 已踩坑与强制避坑清单

这些问题在周报任务中反复出现,执行前必须先对照检查:

1. **必须读完整个 skill**:如果 `read` 返回提示 `truncated`、`more lines` 或内容未到文件末尾,必须继续按 offset 读取到完整结束后再执行;不要只读前半段就开跑。
2. **Brave 限流**:只有 SearXNG 不可用或结果明显不足时才回退 `web_search`;回退 Brave 时必须串行,两个 Brave 请求之间至少间隔 1.2 秒,禁止并行触发 429。
3. **SearXNG 结果质量检查**:SearXNG 可用不等于结果可用。若前 10 条主要是官网、百科、旧文、无日期内容,视为"结果明显不足",必须改写更具体查询(加年份/月/浙江/政策/融资/中试基地等)或串行回退 Brave;不要把泛化结果当作近 7 天证据。
4. **垂直源失败处理**:机器之心、量子位、36氪等垂直源经常 403、JS 渲染失败或只返回页脚/广告/数据服务页。遇到这种情况按"该源无有效正文"在内部来源备注中记录并跳过,不要反复重试;用新华网、财联社、人民网/杭州网、iFinD、精准搜索补足。抓取源失败属于过程备注,不写入最终群聊推送,除非全部信息源失败。
5. **iFinD 调用方式**:`call-node.js` 是模块,不是直接命令行工具。不要直接 `node call-node.js ...`;应创建临时 JS 脚本 `const {call}=require('.../call-node.js')` 后调用 `call(server_type, tool_name, params)`,检查 `ok` 字段,完成后删除临时脚本。
6. **iFinD 工具权限失败**:`search_trending_news` 可能返回 `Tool not allowed`。这不是致命错误:在内部来源备注中记录失败,不超过 1 次重试;继续执行 `search_news`、`search_notice` 和 web 搜索补足,不要中断周报,也不要把该过程问题写入最终群聊推送。
7. **飞书 Drive/Doc 文件路径必须用相对路径**:`lark-cli drive +upload --file`、`lark-cli docs +update --content @file.md` 不接受工作区外的绝对路径。上传或写入前先 `cd` 到文件所在目录,再用 `--file ./文件名.docx`、`--content @./AI-weekly-YYYYMMDD-wiki.md` 这类相对路径。
8. **飞书 Drive 下载链接**:上传结果若只返回 `file_token`,需拼出完整 Drive 链接:`https://qcn8k445rrbc.feishu.cn/file/<file_token>`;该链接只用于 wiki 正文和最终摘要,不写入 Word 正文,不要只写 token 或本地路径。
9. **wiki 创建位置**:目标是一次落到知识库根目录。当前 `lark-cli wiki +node-create --parent-node-token "" --dry-run` 会省略 `parent_node_token`,不能把空字符串 parent 当成可靠直达根目录方案。优先使用能明确落根的路径;若仍使用 `wiki +node-create --space-id`,创建后必须用 `wiki nodes list --as bot` 或返回值检查 `parent_node_token`;若不为空,立即 `wiki +move --as bot --node-token ... --target-space-id ... --target-parent-token ''` 移回根目录,并把这次异常写入内部备注。
10. **wiki 抽查必须解析 JSON 后检查**:`docs +fetch --as bot` 输出是 JSON;检查字段黏连时必须先解析 `data.markdown`,不要在原始 stdout 字符串上做正则,否则 `\n` 转义会导致误判。
11. **wiki 单换行黏连**:飞书会合并普通单换行。正文中"覆盖周期/资料来源"、企业元数据、连续短字段之间必须用空行或列表项;写入后检查 `覆盖周期.*资料来源` 以及 `推荐等级.*所属行业` 等黏连,发现即重写。
12. **商机表空行/None 处理**:读取全表后过滤数据行必须用 `r[0] is not None and str(r[0]).strip()`,不要把 `None` 转成字符串参与排序或写回;写回前统一补齐/截断为 10 列。
13. **商机表排序日期键**:排序 key 必须容错:`str(x[8] if len(x)>8 and x[8] is not None else '')`,避免 `NoneType` 与 `str` 混排报错。
14. **商机表清理残留行**:删除空行前必须读取 `sheetMaxRowCount`(`sheets +info` 返回的 `grid_properties.row_count`)。只有当 `end_row < sheetMaxRowCount` 时才执行删除,且 `--end-index` 必须等于 `sheetMaxRowCount`;禁止硬编码 `200`、`1000` 等上限,否则会触发 `90202 dimension endIndex wrong`。
15. **zsh 清空目录**:不要用可能触发 `no matches found` 的裸 glob(如 `rm reports/summary/*`);用 `find reports/summary -type f -delete` 或 `rm -f reports/summary/*(N)`。
16. **飞书 Drive patch 新版参数**:`lark-cli drive files patch` 只接受 `--params` 和 `--data`,用于 `new_title` 等字段;禁止再使用旧参数 `--type`、`--file-token`、`--body`。示例:`lark-cli drive files patch --as bot --params '{"file_token":"<token>","type":"docx"}' --data '{"new_title":"新标题"}'`。
17. **重复 wiki 文档删除**:同名 wiki 节点去重时,删除对象是 wiki node,不要用 `drive files patch` 伪删除。使用:`lark-cli wiki +node-delete --as bot --space-id "7630717889183534041" --node-token "<node_token>" --obj-type wiki --yes`。普通 Drive 文件才使用 `lark-cli drive +delete --as bot --type docx --file-token "<file_token>" --yes`。
18. **BOT_PROFILE 检测失败必须排查,禁止盲 fallback**:skill 里的自动检测逻辑(`grep "^${AGENT_PREFIX}_"`)可能匹配不到 openclaw.json 中实际的 account key(如 workspace-AIResearcher → airesearcher → 但 openclaw.json 里只有 ai_bot)。当 grep 返回空时,**必须**执行以下排查流程:
    - 列出 openclaw.json 里所有 feishu.accounts keys,找到与 workspace 对应的 bot(如 `ai_bot`)
    - 用该 key 对应的 appId 检查 lark-cli profile 列表:`lark-cli profile list`
    - 如果该 appId 不在 profile 列表中,需要检查 ~/.lark-cli/config.json 是否有对应 app,或 ~/.lark-cli/openclaw/config.json 的 profile 配置
    - **绝对不要**在 grep 返回空后直接 fallback 到 lark-cli 默认 profile,因为默认 profile 可能是其他 bot(如 im_bot),会导致后续所有 wiki/sheet/drive 操作在错误的空间/表格上执行
    - **验证方法**:创建 wiki 节点前,先 `lark-cli wiki spaces list --as bot` 确认能看到目标空间(AI行研 space_id=7630717889183534041);如果看不到,说明 profile 错了,立即停止并修复
19. **wiki 企业元数据用表格格式防黏连**:飞书文档对连续短字段(推荐等级/所属行业/所在地区/产业链位置/推荐方向)即使用双换行或列表格式仍可能黏连。最可靠方案是使用 Markdown 表格格式,写入后 fetch 回来检查 `<lark-table` 标签确认渲染正确。
20. **Word 正文禁止写自身地址**:Word 版报告正文不写"Word版下载""本文链接""飞书 Drive 地址""本地路径"等自身引用。Word 上传后的 Drive 链接只写入 wiki 正文开头和最终推送摘要。
21. **Wiki 节点标题固定英文日期名**:飞书 wiki 节点/知识库文档标题必须固定为 `AI-weekly-YYYYMMDD`,用于去重和覆盖。中文标题(如"行业商机周报_人工智能_YYYYMMDD"或"人工智能行业商机周报")只允许用于 Word 文件名和正文 H1 展示,不得作为 wiki 节点 title。
22. **docs +update 后必须修正 wiki 标题**:`docs +update` 写入带中文 H1 的正文后,飞书可能把 wiki 节点 title 同步成中文标题。每次更新正文后必须立刻执行 `drive files patch --as bot --params '{"file_token":"<obj_token>","type":"docx"}' --data '{"new_title":"AI-weekly-YYYYMMDD"}'`,然后用 `wiki nodes list --as bot` 回查 title 是否恢复为固定英文日期名。
23. **信息抓取禁止跳过任何源**:第一步定义的 18 个数据源(4个必抓源 + 5个搜索 + 3个垂直源 + 1个浙江搜索 + 5个 iFinD)全部必须尝试,一个都不能跳过。Token 优化原则是「搜索优先于爬取」「用 text 模式」「maxChars=6000」,但**不是跳过抓取的理由**。每个源必须有「尝试记录 + 结果备注」,哪怕预判该源会返回空白或 403,也要先发请求,失败后再在内部备注中记录「该源无有效正文」,然后继续下一个源。禁止在发出请求前就决定跳过。
24. **SearXNG 回退 Brave 前必须先改写查询**:当 SearXNG 前 10 条结果主要是官网、百科、旧文、无日期内容时,按坑 #3 视为"结果明显不足"。此时**必须先改写查询词**(加年份/月份/浙江/政策/融资/中试基地等更具体关键词)再试一次 SearXNG;改写后仍然不足,才串行回退 Brave。禁止在 SearXNG 首次结果不佳后直接跳到 Brave。
25. **iFinD 查询禁止跳过**:第五轮的 5 个 iFinD 查询(search_trending_news、search_news、search_notice、search_stocks、get_stock_events)必须全部发出请求,即使 search_trending_news 可能返回 `Tool not allowed`(坑 #6)。每个查询的返回结果(或失败信息)必须在内部备注中记录。禁止因为某一次查询失败就跳过剩余查询。
26. **进入报告生成前必须完成全部 18 个数据源尝试**:只有当第一步的 18 个数据源全部尝试过(不管成功或失败),才能进入第二步信息分类和第七步报告生成。如果为了省 token 或赶时间而跳过部分信息源直接生成报告,属于违反 skill 流程,必须返工重新抓取。
27. **wiki 根目录顺序必须固定为商机表后按日期倒序**:AI 行研知识库根目录第一项是「商机挖掘」表格,周报节点必须排在其后,并按 `AI-weekly-YYYYMMDD` 日期倒序。飞书公开 API 只能移动到父节点,不能指定 sibling 位置;当前已验证 `wiki +move --target-space-id <space_id>` 会把节点追加到根目录末尾。因此每次新建或更新周报后,必须执行根目录重排:列出根目录节点,识别 `AI-weekly-*` 节点,保留最新周报不动,把其余旧周报按日期倒序依次 `wiki +move --as bot --node-token <old_node> --target-space-id "7630717889183534041"` 追加到末尾,最终校验顺序为 `商机挖掘`、最新周报、次新周报......。若移动行为变化或校验不通过,停止并提示人工处理,不要声称已排序。
28. **docs +update 使用当前新版参数**:当前 lark-cli 1.0.38 的 `docs +update` 必须使用 `--command overwrite --doc-format markdown --content @./file.md`;旧写法 `--mode overwrite --markdown @file.md` 会报 `--command is required`。写入前先 `cd` 到 Markdown 文件目录,避免绝对路径报错。
29. **docs +fetch 校验不要用 `--format markdown` 或 `str(data)`**:当前 lark-cli 1.0.38 会提示 `unknown format "markdown", falling back to json`。校验 wiki 黏连时必须解析 JSON 后读取 `data.document.content` 或明确存在的正文内容字段;不要对 `str(data)` 做正则,否则 HTML/XML 标签在同一行会造成 `推荐等级.*所属行业` 这类误报。
30. **cron 运行中禁止"先失败再重试"**:OpenClaw cron 会把任意中途 tool failure 记入 diagnostics;即使后续修复成功并产出最终摘要,整次 run 仍可能被标记为 `error`,并把失败通知推送到群聊。执行 `lark-cli` 前必须先确认参数和路径,探索性命令要用不会产生非零退出码的方式隔离;已知可恢复问题不要先触发失败再补救。

## 产品资料

产品推荐必须基于本地产品资料文件,不得虚构产品名称、额度、期限、费率或准入条件:
- **产品资料路径**:`~/.openclaw/workspace/file/productFile.docx`
- 生成周报前**必须先读取该文件**,了解平安银行产品库内容
- 产品资料中没有的参数写"待沟通"
- 产品配置不要堆砌,采用"主推产品 + 配套产品"方式,每家企业一般推荐2-4类

## 工作流

### 第〇步:总体要求(分析师角色与全局规则)

你以平安银行杭州分行"首席行业分析师"身份进行分析,当前分析对象为【目标行业】。

核心职责不是简单汇总新闻,而是通过行业政策、政府规划、全国行业动态、浙江区域动态、重点企业动态和上下游产业链变化,挖掘可营销商机,并为客户经理生成清晰、简洁、可执行的企业推荐与银行产品配置方案。

分析必须服务于以下目标:
1. 【目标行业】近期为什么值得关注?
2. 浙江地区有哪些区域机会?
3. 哪些浙江企业值得优先拜访?
4. 推荐这些企业的理由是什么?
5. 平安银行有哪些展业机会?
6. 应该用哪些产品切入?
7. 客户经理该如何开口沟通?

**全局规则(11条,贯穿所有步骤):**

1. 必须联网获取最新信息,不得只依赖历史知识。
2. 必须关注全国行业动态、浙江地区行业动态、相关企业动态、上下游产业链动态。
3. 第一大板块只分析全国层面、国家层面、行业层面动态,**不放浙江内容**。凡是浙江相关政策、规划、项目、产业集群、区域机会,统一放入第二部分。
4. 第二大板块单独分析浙江地区动态与区域机会。
5. 第三大板块为重点企业推荐。
6. 企业推荐部分必须说明"推荐理由"和"银行展业机会"。
7. 企业信息要简洁,但需要体现企业高层和核心团队背景,包括学校、专业、导师、职业生涯、产业资源等公开信息。
8. 平安银行产品推荐必须基于本地产品资料(`~/.openclaw/workspace/file/productFile.docx`),**不得虚构产品名称、额度、期限、费率或准入条件**。如果产品资料中没有明确参数,写"待沟通"。
9. 内容要清晰明了,不要写成长篇研究报告。
10. 无法确认的信息写"待核实"或"未披露"。
11. 每条重要判断都要形成闭环:事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作;但「近期政策变动」板块不要每条政策都单独写闭环,应先把政策内容写充分,最后统一写一段综合影响闭环。
12. 周报正文不要在句中写来源括注,例如"(5月14日吹风会,杭州网/人民网浙江)""(来源:XXX)"。如需保留依据,可在文末或开头"资料来源"统一概括,不要影响客户经理阅读。

### 第一步:信息抓取(必抓源 + 搜索为主 + 垂直源补充)

**必抓源(4个,不可跳过):**

```
1. 同花顺首页 → web_fetch https://www.10jqka.com.cn/  (extractMode="text", maxChars=6000)
2. 财联社电报 → web_fetch https://www.cls.cn/telegraph  (extractMode="text", maxChars=6000)
3. 新华网科技 → web_fetch https://www.xinhuanet.com/tech/  (extractMode="text", maxChars=6000)
4. 经济观察网 → web_fetch https://www.eeo.com.cn/  (extractMode="text", maxChars=6000)
```

**核心策略:必抓源打底,搜索补充,垂直源进一步补充。所有源必须逐个尝试,禁止跳过。**

⚠️ **信息源抓取执行纪律(强制):**
- 第一步定义的所有数据源(4 个必抓源 + 5 个搜索 + 3 个垂直源 + 1 个浙江搜索 + 5 个 iFinD = **18 个源**)全部必须发出请求,**一个都不能跳过**。
- 每个源请求后必须在内部备注中记录该源的抓取状态(成功/空白/403/Tool not allowed 等)。
- 禁止在发出请求前就凭预判跳过任何源;即使认为某源大概率返回空白,也要先尝试。
- 只有全部 18 个源都尝试过,才能进入第二步和第七步。
- Token 优化≠跳过抓取。优化手段是选择更高效的工具(搜索 > 爬取)和参数(text 模式、maxChars=6000),不是省略数据源。

**第二轮:精准搜索(5个查询;优先 SearXNG,Brave 备用):**

优先使用本地 SearXNG,避免 Brave 免费套餐 1 次/秒限流导致 429。执行方式:

```bash
SEARXNG_URL=http://localhost:8080 python3 ~/.openclaw/skills/searxng/scripts/searxng.py search "查询词" -n 10 --format json
```

如 SearXNG 不可用、返回异常或结果明显不足,再回退到 `web_search`(Brave)。使用 Brave 时必须串行执行,不要并行调用。

```
1. "AI 行业" OR "人工智能" → SearXNG(近7天,count=10;Brave备用)
2. "大模型" OR "LLM" OR "GPT" OR "Claude" → SearXNG(近7天,count=10;Brave备用)
3. "AI 芯片" OR "GPU" OR "算力" → SearXNG(近7天,count=10;Brave备用)
4. "机器人" OR "具身智能" OR "自动驾驶" → SearXNG(近7天,count=10;Brave备用)
5. "AI 融资" OR "AI 上市" OR "AI 政策" OR "AI 投资" → SearXNG(近7天,count=10;Brave备用)
```

**第三轮:AI 垂直源补充(并行,3个):**

```
6. 机器之心 → web_fetch https://www.jiqizhixin.com/  (extractMode="text", maxChars=6000)
7. 量子位 → web_fetch https://www.qbitai.com/  (extractMode="text", maxChars=6000)
8. 36氪 AI 频道 → web_fetch https://www.36kr.com/information/AI/  (extractMode="text", maxChars=6000)
```

**第四轮:浙江本地 AI 专项搜索(1个):**

```
9. "AI 浙江" OR "人工智能 杭州" OR "AI 宁波" OR "大模型 浙江" → SearXNG(近7天,count=10;Brave备用)
```

**第五轮:iFinD 金融新闻公告专项(3个并行):**

> 使用 iFinD-Finance-Data skill,需 Node.js 环境(`call-node.js` 脚本)。
> 配置文件 `mcp_config.json` 需包含有效 `auth_token`。
> 每次请求后检查 `ok` 字段确认是否成功。

```
10. search_trending_news(热点事件,注重时效性,size 不超过 10)
    server_type="news", tool_name="search_trending_news"
    params: {"keyword": "人工智能", "industry_name": "计算机", "time_scope": "近7天", "size": 10}
    → 抓取 AI 行业热点事件(如 time_scope 不支持"近7天"则回退到"近3天"或去掉 time_scope)
    ⚠️ 此查询必须发出请求,不能跳过;失败时在内部备注记录。

11. search_news(新闻语义检索,严格 7 天)
    server_type="news", tool_name="search_news"
    params: {"query": "AI 大模型 算力 机器人", "time_start": "YYYY-MM-DD(= 今天往前推7天)", "time_end": "YYYY-MM-DD(= 今天)", "size": 10}
    → AI 行业新闻深度检索,不得超过7天范围
    ⚠️ 此查询必须发出请求,不能跳过;失败时在内部备注记录。

12. search_notice(公告语义检索,严格 7 天)
    server_type="news", tool_name="search_notice"
    params: {"query": "人工智能 融资 定增 投产 订单", "time_start": "YYYY-MM-DD(= 今天往前推7天)", "time_end": "YYYY-MM-DD(= 今天)", "size": 10}
    → AI 相关上市公司公告(定增/订单/投产→直接对应银行商机),不得超过7天范围
    ⚠️ 此查询必须发出请求,不能跳过;失败时在内部备注记录。
```

⚠️ **iFinD 时间范围严格控制为 7 天**:time_start/time_end 必须用实际日期(YYYY-MM-DD),计算为周报覆盖周的起始日到结束日,不得扩大范围。

**iFinD 补充查询(按需,前12轮完成后,同样限制7天范围):**
```
13. search_stocks(AI 板块上市公司筛选)
    server_type="stock", tool_name="search_stocks"
    params: {"query": "人工智能行业股票"}
    → 发现 AI 板块上市公司名单,用于后续事件关联
    ⚠️ 此查询必须发出请求,不能跳过;失败时在内部备注记录。

14. get_stock_events(上市公司重大事件,近7天)
    server_type="stock", tool_name="get_stock_events"
    params: {"query": "浙江AI相关股票重大事件"}
    → 抓取浙江 AI 上市公司的 IPO/定增/订单等事件(时间范围不超过7天)
    ⚠️ 此查询必须发出请求,不能跳过;失败时在内部备注记录。
```

**iFinD 使用注意:**
- iFinD 只覆盖上市公司及公开金融市场数据,**不覆盖非上市 AI 初创企业**,不能替代 web_search
- 新闻/公告返回的是语义检索片段,不是全文;发现重要线索后再用 web_fetch 点入正文
- 每次请求后必须检查 `ok` 字段,失败时不重试超过 1 次
- **所有查询严格限制 7 天时间范围**,time_start/time_end 用 YYYY-MM-DD 格式的实际日期
- 查询完成后清理临时生成的脚本文件

**按需补充:**
- 从搜索结果中发现重要文章时,点入正文抓取(web_fetch, extractMode="text", maxChars=4000)
- 如需更全面的市场/财经视角,可补充搜索:"AI 行业 周报" OR "AI 产业 趋势"(count=5)

**抓取规则:**
- 4个必抓源优先并行执行
- 必抓源完成后,web_search 搜索 + 垂直源并行执行
- 如果 web_fetch 返回空白/JS 渲染失败,跳过该源,不要重试
- 关注 **近 7 天内** 发生的事件(周报覆盖一周范围)
- 关注浙江/长三角地区的 AI 企业动态优先

### 第二步:信息跟踪范围

按指令定义的四大维度分类和组织抓取到的信息:

#### 1. 全国行业动态

重点关注:
- 国家政策、产业政策、监管政策
- 行业供需变化、价格变化、技术路线变化
- 扩产、并购、上市、融资、发债、重大项目
- 招投标、中标、大客户合作
- 出口、跨境、海外建厂、海外订单
- 风险事件:处罚、诉讼、亏损、债务压力、停产等

#### 2. 浙江区域动态

重点关注:
- 浙江省及杭州、宁波、温州、绍兴、嘉兴、湖州、金华、台州等地政策
- 政府规划与产业方向必须优先聚焦浙江;浙江公开信息不足时,可补充长三角(上海/江苏/安徽)相关规划作为参考,但需明确标注地域且不得替代浙江结论
- 浙江"415X"先进制造业集群
- 专精特新、小巨人、高新技术企业、隐形冠军
- 地方重大项目、产业园区、技改补贴、绿色制造、智能制造、设备更新等
- 浙江在【目标行业】中的产业集群、重点企业、上下游配套和区域优势

#### 3. 企业动态

重点关注能转化为银行商机的信号:
- 扩产、拿地、环评、技改、设备采购
- 中标、新订单、新客户合作
- 出口增长、海外布局、跨境业务
- 上市辅导、定增、发债、融资
- 应收账款增加、存货增加、现金流压力
- 成为链主企业、核心供应商、重点培育企业
- 司法、处罚、失信、经营异常等风险信号

#### 4. 上下游产业链动态

分析企业所在产业链:
- 上游原材料、设备、零部件、技术服务供应商
- 中游制造、加工、集成、平台或服务企业
- 下游客户、经销商、渠道、终端应用
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

按照指令定义的闭环进行分析:

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
- 每条重要判断都要形成闭环:事实信号 → 经营含义 → 金融需求 → 产品匹配 → 营销动作
- 「近期政策变动」写法:政策情况要比普通新闻更详细,说明发布主体、发布时间/背景、核心条款/支持方向、约束或机会点;不要在每条政策后都写"影响闭环",而是在该小节末尾统一写一段"综合影响闭环"。
- 「政府规划与产业方向」写法:重点聚焦浙江地区(浙江省、杭州/宁波/温州/绍兴/嘉兴/湖州/金华/台州/丽水/衢州/舟山等);若浙江本地信息不足,可扩展至长三角(上海、江苏、安徽)作为补充参考,并明确标注地域。
- 「来源引用」写法:正文不要出现"(日期,媒体/网站)""(来源:媒体名)"这类来源括注;日期可自然融入事实表述,来源统一放在报告开头或文末"资料来源"中概括。
- 第一大板块只分析全国层面、国家层面、行业层面动态,**不放浙江内容**
- 浙江相关政策、规划、项目、产业集群、区域机会统一放入第二部分
- 第一大板块不写浙江省或浙江各地市内容

### 第四步:企业推荐判断规则

#### 1. 推荐理由

推荐理由应来自事实信号,例如:
- 所属行业符合国家或浙江重点支持方向
- 企业处于景气上行或结构性机会赛道
- 企业位于浙江优势产业集群
- 企业近期出现扩产、技改、中标、出口、融资等积极信号
- 企业在产业链中具备核心企业、链主企业、优质供应商或优质经销商地位
- 企业高层或团队具备较强产业、技术、资本、客户资源背景
- 企业具备银行授信、票据、供应链、跨境、现金管理、代发等切入空间
- 风险信号相对可控

#### 2. 银行展业机会

必须从企业经营活动推导银行业务机会:
- 扩产/技改/设备采购 → 项目贷款、设备融资、科技创新和技术更新改造再贷款、平安租赁
- 订单增长/备货增加 → 短贷、普惠信用贷、银票贴现、国内信用证
- 应收账款增加/账期较长 → 付融通、保理、商票保贴、商票e贴
- 供应链上下游关系明确 → 订单融资、订货贷、平台数字贷、供应链金融
- 出口/海外业务 → 跨境支付结算、人民币国际证+福费廷、外币存款、跨境资金管理、平安避险
- 资金账户分散/管理复杂 → 数字财资、资产池、慧收款、移企付、口袋管家
- 员工规模较大/企业主需求明显 → 平安薪、个贷、家族信托、财富权益

### 第五步:企业高层与团队背景要求

企业关键信息中必须体现高层和团队背景,但要简洁。

重点关注:
- 董事长、实控人、总经理、CFO、CTO、核心创始人
- 教育背景:毕业学校、专业、学位
- 科研背景:导师、实验室、研究方向、学术成果,如公开可查
- 职业经历:曾任职企业、产业经历、管理经历、创业经历
- 产业资源:是否来自龙头企业、高校科研院所、政府平台、上市公司、外企、核心客户体系
- 银行关注点:其背景是否有助于判断企业技术实力、客户资源、融资能力、资本市场潜力或决策链条

注意:
- 只使用公开可查信息。
- 不得虚构个人履历。
- 未披露的信息写"未披露"或"待核实"。

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
# 【目标行业】行业商机周报

## 一、行业动态与发展总结
(仅全国/国家/行业层面,不含浙江内容)

⚠️ **本板块不分子项，统一以 2-4 段话总结本周全国层面行业动态即可**，涵盖政策信号、产业规划方向、行业景气趋势和产业链核心变化，最后附一段综合影响闭环（事实信号 → 行业影响 → 金融需求 → 产品匹配 → 营销动作）。不要出现"近期政策变动""政府规划""发展趋势""上下游"等子标题。

要求:
- 不要简单罗列政策标题，提炼核心信号。
- 说明政策/规划对【目标行业】的影响。
- 说明可能带来的银行业务机会。
- 浙江政策/项目不要放在这里。

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
⚠️ **硬性结构要求（不可压缩/不可省略）**：每一家企业必须严格保留下列字段和小标题；不得把"企业关键信息"合并成一段，也不得把"推荐理由""银行展业机会"改写成无结构长段。若资料不足，字段仍保留，并写"未披露/待核实"。生成完成后必须逐家自检：是否包含【推荐等级、所属行业、所在地区、产业链位置、推荐方向、企业关键信息-基本情况、企业关键信息-高层与团队背景、企业关键信息-银行关注点、推荐理由、银行展业机会、推荐产品组合、风险提示】；缺一项必须返工。

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

**风险提示：**
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
- **固定保存目录**:`/Users/leidongqiao/.openclaw/workspace/workspace-AIResearcher/reports/ai-weekly/`(即当前工作空间的 `reports/ai-weekly/`),不得保存到其他目录;如目录不存在先创建。
- **本地上传目录同步**:生成 Word 前,先清空 `/Users/leidongqiao/Documents/codex project/local-uploader/data/AI/` 目录下的文件,但保留该目录本身。生成 `AI-weekly-YYYYMMDD.docx` 后,必须复制一份同名 Word 文件到该目录,供 local-uploader 使用。推荐命令:
  ```bash
  mkdir -p "/Users/leidongqiao/Documents/codex project/local-uploader/data/AI"
  find "/Users/leidongqiao/Documents/codex project/local-uploader/data/AI" -type f -delete
  cp "/Users/leidongqiao/.openclaw/workspace/workspace-AIResearcher/reports/ai-weekly/AI-weekly-YYYYMMDD.docx" "/Users/leidongqiao/Documents/codex project/local-uploader/data/AI/"
  ```
- 文件名格式:`AI-weekly-YYYYMMDD.docx`(与 wiki 节点标题 `AI-weekly-YYYYMMDD` 保持一致)
- **同名覆盖检查**:生成前先检查该目录下是否已有同名文件,若存在则直接覆盖,不保留重复文件。
- 字体使用华文楷体
- **Word 样式优化**:Word 版必须是干净的报告排版,不要把 Markdown 原始符号带入正文;生成 docx 时需去掉 `- **`、`**`、表格竖线等 Markdown 标记。普通段落用自然段,企业信息可用短段落或简洁项目符号,但不要让每段前面都出现 `- **`。推荐产品组合不得用表格。
- Word 正文只写报告内容,不写自身下载地址、飞书 Drive 地址、本地路径或"Word版下载"字段。
- 生成后上传为飞书 Drive 文件,获取可下载链接;该链接只写入飞书 wiki 知识库正文开头和最终推送摘要中的「周报全文(Word)」,不要写回 Word 正文。

#### 版本B:飞书 wiki 版(知识库存档格式)

- 内容与 Word 版结构一致,适配飞书文档 Markdown 格式
- 通过第九步写入知识库
- wiki 正文开头(标题下方、覆盖周期/资料来源前)必须写入:`**Word版下载:** [点击下载Word版周报](飞书Drive下载链接)`。
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

从第七步周报的「四、客户经理行动建议」中提取需要跟进的浙江企业,写入「商机挖掘」电子表格。

**🔴 关键规则(必须严格遵守):**
- **从行动建议提取**:从周报「四、客户经理行动建议」中提取明确提及的浙江企业,这些是需要客户经理优先跟进的商机
- **写入前必须去重**:先读取 A 列,用「规范化核心简称精确匹配」判断是否已存在
- **禁止重复写入同一企业**:同一核心简称只保留一行,已有行则更新,无则追加

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

⚠️ **严禁**:
- 更新行时修改A列客户名称(包括加后缀、改格式等),必须保持原名称不变
- 用包含匹配(如"蚂蚁"匹配到"蚂蚁灵光"),必须用核心简称完全匹配

**写入流程(严格执行):**
1. 读取 A 列全量数据
2. 对 A 列每个非空名称做规范化:去掉括号内容,得到**已有核心简称列表**
3. 对本次商机先去重:按核心简称合并同名企业,每个核心简称只保留一条
4. 对每个去重后的商机:提取核心简称 → 精确匹配 → 匹配到则更新,未匹配则追加
5. ⚠️ **更新已有商机时,创建日期(I列)必须更新为当前日期(YYYY-MM-DD)**
6. ⚠️ **如果匹配到的已有行状态为终态(closed/已关闭/已落地),则跳过该行,不更新**
7. ⚠️ **新增商机的状态列统一填写「待联系」,不要写 active/open**
8. ⚠️ **更新已有商机时,状态列保持不变,不修改**
9. ⚠️ **写入完成后,必须对整个表格进行时间倒序重排 + 清理残留空行**(见下方「表格排序与清理」)

**字段顺序**:客户名称、行业/领域、触发信号、优先级、推荐方案、预计金额、联系人、状态、创建日期、备注

**⚠️ 表格排序与清理(每次写入后必须执行):**

使用 Python 脚本完整读取表格数据、按日期倒序排序、写回并清理残留行:
```python
import json, subprocess

# 1. 读取全表
result = subprocess.run(
    ['bash', '-c', '~/.npm-global/bin/lark-cli sheets +read --spreadsheet-token FwBOsiErhh5U9Qtr5pvclx9Zncl --range "28609d!A1:J100"'],
    capture_output=True, text=True
)
raw = result.stdout
start = raw.find('{')
end = raw.rfind('}') + 1
data = json.loads(raw[start:end])
rows = data['data']['valueRange']['values']

header = rows[0]
data_rows = [r for r in rows[1:] if len(r) > 0 and r[0] and r[0].strip()]

# 2. 按日期列(index 8)倒序排列(最新在前)
data_rows.sort(key=lambda x: x[8] if len(x) > 8 and x[8] else '', reverse=True)

# 3. 写入排序后的数据
with open('/tmp/sheet_data.json', 'w') as f:
    json.dump(data_rows, f)

end_row = 1 + len(data_rows)
subprocess.run(
    ['bash', '-c', f'~/.npm-global/bin/lark-cli sheets +write --as bot --spreadsheet-token FwBOsiErhh5U9Qtr5pvclx9Zncl --range "28609d!A2:J{end_row}" --values "$(cat /tmp/sheet_data.json)"'],
    capture_output=True, text=True
)

# 4. 清理 end_row+1 之后的残留空行(防止之前写入残留)
info_result = subprocess.run(
    ['bash', '-c', '~/.npm-global/bin/lark-cli sheets +info --spreadsheet-token FwBOsiErhh5U9Qtr5pvclx9Zncl'],
    capture_output=True, text=True
)
info_raw = info_result.stdout
info_data = json.loads(info_raw[info_raw.find('{'):info_raw.rfind('}') + 1])
sheet_max_row_count = None
for sheet in info_data['data']['sheets']['sheets']:
    if sheet.get('sheet_id') == '28609d':
        sheet_max_row_count = sheet['grid_properties']['row_count']
        break

# 只有存在残留行时才删除;end-index 必须等于 sheetMaxRowCount,禁止硬编码 200/1000
if sheet_max_row_count is not None and end_row < sheet_max_row_count:
    subprocess.run(
        ['bash', '-c', f'~/.npm-global/bin/lark-cli sheets +delete-dimension --as bot --spreadsheet-token FwBOsiErhh5U9Qtr5pvclx9Zncl --sheet-id "28609d" --dimension "ROWS" --start-index {end_row} --end-index {sheet_max_row_count}'],
        capture_output=True, text=True
    )
```

⚠️ **关键说明:**
- 排序后如存在残留行,必须用 `+delete-dimension` 删除 end_row 之后的所有行,否则会残留空行和旧数据
- 删除前必须通过 `sheets +info` 读取当前 `grid_properties.row_count`;若 `end_row >= row_count`,说明无残留行,禁止执行删除
- `+delete-dimension --end-index` 必须使用当前 `row_count`,不要硬编码 `200`、`1000` 等值,否则会触发 `90202 dimension endIndex wrong`
- 如果之前写入范围小于实际数据量(如写了 A2:J26 但旧数据在 52-53 行),中间会留下大量空行,必须删除

###  第九步:写入知识库(飞书 wiki 版)

**写入内容:第七步版本B(飞书 wiki 版),结构与 Word 版一致,适配飞书 Markdown 格式。**

**Word 下载链接位置要求:** Word 版生成后必须先上传飞书 Drive 获取下载链接;wiki 正文开头(标题下方、覆盖周期/资料来源前)必须写入 `**Word版下载:** https://.../file/...`,不得只在文末附链接,不得使用尖括号 `<...>`。

**重要:每次生成都覆盖当前同名文件(AI-weekly-YYYYMMDD),不要有重复日期的文档。Wiki 节点标题必须固定为 `AI-weekly-YYYYMMDD`,不得使用中文报告名;中文报告名只用于 Word 文件名和正文展示标题。**

**🔴 关键规则(必须严格遵守):**
- 文档必须创建在知识库**根目录**(`parent_node_token` 为空字符串),**不能**创建在「首页」或其他节点下面
- wiki 的创建、查询、移动、删除、正文写入和回读校验全部必须使用**机器人身份**(所有 `lark-cli wiki ...` 与 `lark-cli docs ...` 命令都显式带 `--as bot`),不得使用用户身份或省略身份参数
- wiki 节点 title 必须是 `AI-weekly-YYYYMMDD`。搜索、创建、覆盖、去重全部按这个固定 title 执行,不得用 `行业商机周报_【目标行业】_YYYYMMDD` 或其他中文标题作为节点名
- 空间名称是 `AI行研`(没有空格),不是 `AI 行研`

**步骤:**

1. **列出知识库所有节点,查找是否已有同名文档(搜索全部节点,不限根目录!)**:
   ```bash
   lark-cli wiki nodes list --as bot --params '{"space_id":"7630717889183534041","page_size":50}'
   ```
   从返回结果中搜索 title 为 `AI-weekly-YYYYMMDD` 的节点,提取 `obj_token` 和 `node_token`。
   ⚠️ **必须搜索所有节点**(不限 `parent_node_token`),否则第一次创建时可能被放在「首页」下,第二次搜不到就重复创建了!
   ⚠️ **如果找到多个同名文档**,选 `obj_edit_time` 最新的那个,用 `docs +update` 覆盖;其余重复 wiki 节点用下面命令删除,禁止使用 `drive files patch` 删除:
   ```bash
   lark-cli wiki +node-delete --as bot \
     --space-id "7630717889183534041" \
     --node-token "<duplicate_node_token>" \
     --obj-type wiki \
     --yes
   ```
   说明:`drive files patch` 新版只支持 `new_title` 等文件元数据更新,不能设置 `trash_type`。

2. **如果找到同名文档**:
   - 先 `cd` 到 wiki Markdown 文件所在目录,再使用 `lark-cli docs +update --api-version v2 --doc <obj_token> --as bot --command overwrite --doc-format markdown --content @./AI-weekly-YYYYMMDD-wiki.md` 覆盖内容
   - 立刻用 `lark-cli drive files patch --as bot --params '{"file_token":"<obj_token>","type":"docx"}' --data '{"new_title":"AI-weekly-YYYYMMDD"}'` 把文档/节点标题修回固定英文日期名,防止正文中文 H1 覆盖节点标题
   - 输出文档链接:`https://www.feishu.cn/wiki/<node_token>`
   - 执行「根目录周报倒序重排」(见下方第 4 步),确保该节点排在「商机挖掘」后面。

3. **如果未找到同名文档**:
   - 优先使用当前 CLI 能明确落到知识库根目录的创建方式。已验证 `wiki +move` 的 docs-to-wiki 模式在不传 `--target-parent-token` 时会移动到目标空间 root;如果先创建 Drive Docx 再入库,使用:
     ```bash
     lark-cli wiki +move --as bot \
       --target-space-id "7630717889183534041" \
       --obj-type "docx" \
       --obj-token "<drive_docx_token>"
     ```
   - 如果必须使用 `wiki +node-create`,不要误以为 `--parent-node-token ""` 一定生效:当前 CLI dry-run 会省略空 parent。可使用以下命令创建,但创建后必须检查位置:
     ```bash
     lark-cli wiki +node-create --as bot \
       --space-id "7630717889183534041" \
       --title "AI-weekly-YYYYMMDD" \
       --obj-type "docx"
     ```
   - 从返回结果提取 `obj_token`(用于内容更新)和 `node_token`(用于 URL)
   - 先 `cd` 到 wiki Markdown 文件所在目录,再使用 `lark-cli docs +update --api-version v2 --doc <obj_token> --as bot --command overwrite --doc-format markdown --content @./AI-weekly-YYYYMMDD-wiki.md` 写入内容
   - 立刻用 `lark-cli drive files patch --as bot --params '{"file_token":"<obj_token>","type":"docx"}' --data '{"new_title":"AI-weekly-YYYYMMDD"}'` 把文档/节点标题修回固定英文日期名,防止正文中文 H1 覆盖节点标题
   - 输出文档链接:`https://www.feishu.cn/wiki/<node_token>`
   - ⚠️ 创建后用 `wiki nodes list --as bot` 确认 `parent_node_token`。如果不在根目录,说明直接根节点创建失败,必须立刻用 `wiki +move --as bot --target-parent-token ""` 移回根目录,并在内部备注记录异常。
   - 执行「根目录周报倒序重排」(见下方第 4 步),确保新周报排在「商机挖掘」后面。

4. **根目录周报倒序重排(必须执行)**:
   - 先列出 AI 行研知识库根目录节点,并确认「商机挖掘」在第一位:
     ```bash
     lark-cli wiki +node-list --as bot \
       --space-id "7630717889183534041" \
       --page-all \
       --format json
     ```
   - 从根目录节点中筛选标题匹配 `AI-weekly-YYYYMMDD` 的周报节点,按日期降序排序。
   - 设本次最新周报为排序后的第一个节点。由于飞书 API 不支持"插入到某节点后",用已验证的追加行为完成排序:保持「商机挖掘」和最新周报不动,把其余旧周报按日期降序依次移动到根目录末尾:
     ```bash
     lark-cli wiki +move --as bot \
       --node-token "<旧周报node_token>" \
       --target-space-id "7630717889183534041"
     ```
   - 重新执行 `wiki +node-list --as bot --space-id "7630717889183534041" --page-all --format json` 校验根目录前几项。必须满足:
     1. 第 1 项标题为 `商机挖掘`
     2. 第 2 项为最新 `AI-weekly-YYYYMMDD`
     3. 后续 `AI-weekly-*` 按日期倒序排列
   - 如果校验失败,不要继续群聊推送,先报告失败原因和当前顺序。

**禁止**使用 `feishu_wiki_space_node` 工具(该工具可能将文档创建在首页下)。必须使用 bot 身份的 `lark-cli wiki` / `lark-cli docs` 命令,并以根目录位置校验为准。

### 第十步:推送至群聊(极简概要 + 链接,200字左右)

**🔴 关键规则:推送到群聊的内容是极简概要和链接,不是全文!手机端必须能一次读完。**

**长度限制:正文控制在 200 字左右(不含链接 URL),最多不超过 300 字。**

推送至群聊的消息格式如下:

```markdown
📌 【目标行业】商机周报·浙江|YYYY.MM.DD-MM.DD
🔥 主线:XXX、XXX、XXX
🏠 浙江机会:XXX
🏢 优先跟进:XXX、XXX、XXX
🎯 切入方向:XXX/XXX/XXX

Word:<飞书Drive下载链接>
Wiki:<https://www.feishu.cn/wiki/XXXX>
商机表:<https://xxx.feishu.cn/wiki/XXXX>
```

####  10.1 同步至工作空间

推送前,先把要推送的极简摘要写一份到本地工作空间:

1. **清空目录:**删除 `reports/summary/` 目录下所有文件(目录本身保留)。
2. **写入文件:**将即将推送的群聊摘要内容写入 `reports/summary/AI-summary.md`。

```bash
# 清空目录
rm -f ~/.openclaw/workspace/workspace-AIResearcher/reports/summary/*
# 写入摘要
echo '<摘要内容>' > ~/.openclaw/workspace/workspace-AIResearcher/reports/summary/AI-summary.md
```

#### 10.2 推送至群聊

**推送内容要求:**
- 行业动态:只提炼 2-3 个主线关键词,不逐条列新闻
- 浙江区域:只写 1 句机会集中方向
- 企业推荐:只列重点 3 家以内,不写推荐理由
- 行动建议:只写 1 句"优先跟进 + 切入方向"
- 样式要求:正文四行呈现,固定为「🔥 主线 / 🏠 浙江机会 / 🏢 优先跟进 / 🎯 切入方向」,不要写成一大段话
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
5. 若需要向用户说明执行状态,只能在非群聊/人工排查上下文说明;在群聊定时任务中,最终输出仍必须是第十步摘要模板。

### 第十一步:表达风格

面向客户经理,不面向学术研究。写作风格规则:

1. **面向客户经理**:语言专业、直接、可执行,不是学术研究。
2. **不堆砌新闻**:不要简单罗列新闻标题,要说明影响和机会。
3. **不堆砌产品**:产品配置不要堆砌,采用"主推产品 + 配套产品"方式,每家企业一般推荐2-4类;重点企业推荐中的「推荐产品组合」用一段话总结,不用表格。
4. **企业重点讲清3件事**：推荐理由 → 银行展业机会 → 推荐产品组合。
5. **简要呈现企业基本信息**:不需要机械罗列全部工商信息。
6. **帮助形成判断**:输出要帮助客户经理回答--今天该联系谁、为什么联系、聊什么产品、怎么切入。
7. **Word输出**:字体使用华文楷体;版式要像正式报告,去掉 Markdown 原始符号(尤其是 `- **`、`**`、表格分隔线),避免每段前面都有项目符号和加粗标记。
8. **正文去来源括注**:正文面向客户经理,不写"(5月14日吹风会,杭州网/人民网浙江)""(iFinD新闻,5月20日)"等来源括注;证据来源统一在"资料来源"中概括即可。

### 第十二步:输出完成

输出完成后,由调用方(定时任务等)通过 delivery 配置推送到飞书群,无需在 skill 内执行推送。

⚠️ 但要注意:**delivery 推送的是最终 assistant 回复**。因此最终回复不能写"已完成/执行摘要/文件路径/抓取源清单"等状态说明,必须直接输出第十步规定的群聊摘要模板(概要 + Word Drive 链接 + wiki 链接 + sheets 链接)。

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
3. **地域限制**:本地行业动态、行动清单仅限浙江本地企业;大企业/大厂(阿里、腾讯等)动态不纳入本地行业动态
4. **禁止推荐不合规业务**
5. **双版本输出**:Word 版用于详细报告(华文楷体),wiki 版用于知识库存档(飞书 Markdown 格式),内容结构一致
6. **知识库标题**:AI-weekly-YYYYMMDD。该标题是 wiki 节点名/去重键,禁止替换成中文报告名
7. **知识库写入**:必须使用 bot 身份的 `lark-cli wiki` / `lark-cli docs` 命令写入 AI 行研知识库,禁止使用 `feishu_wiki_space_node` 工具。优先选择能明确落到根目录的路径;当前 `wiki +node-create --parent-node-token ""` dry-run 会省略空 parent,不能视为可靠直达根目录。去重时**搜索全部节点**(不限 parent_node_token),避免重复创建。所有 wiki/docs 操作显式 `--as bot`,不得用用户身份。写入后必须执行根目录重排:`商机挖掘` 第一,`AI-weekly-*` 按日期倒序跟在其后
8. **群聊推送**:推送概要 + 链接,不是全文
9. **商机挖掘表格**:数据来源为周报「四、客户经理行动建议」中提及的企业。写入前必须去重,只写浙江本地企业。更新已有商机时日期必须更新为当天。写入后必须按时间倒序重排并清理残留空行
10. **搜索限流策略**:默认使用 SearXNG(`SEARXNG_URL=http://localhost:8080 python3 ~/.openclaw/skills/searxng/scripts/searxng.py search "query" -n 10 --format json`);Brave `web_search` 仅作为备用。若回退 Brave,必须串行执行,避免免费套餐 1 次/秒限流导致 429。
11. **代理配置**:Gateway 进程需配置代理环境变量(`HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:7890`),否则 Brave API 连接超时。lark-cli 会检测到代理变量并发出警告,不影响功能
12. **Word 输出**:使用华文楷体字体,固定保存到 `/Users/leidongqiao/.openclaw/workspace/workspace-AIResearcher/reports/ai-weekly/`,文件名格式 `AI-weekly-YYYYMMDD.docx`(与 wiki 节点标题一致);生成前检查同名文件并覆盖;生成后上传飞书 Drive,并将下载链接写在 wiki 正文开头及推送摘要中;Word 正文不得写自身下载地址、飞书 Drive 地址或本地路径,且必须清理 Markdown 标记,推荐产品组合不用表格。
13. **正文来源格式**:周报正文去掉媒体/网站来源括注;不要出现"(日期,来源)""(来源:XXX)"。资料来源只在报告开头或文末统一概括。

## 文件路径

```
skills/ai-weekly-report/
├── SKILL.md                    # 本文件
└── references/
    └── (预留)
```

## lark-cli profile 设置(执行前必须验证)

所有 lark-cli wiki/docs/sheets/drive 操作使用 `--as bot`,bot 身份由 lark-cli 当前 profile 决定。wiki 相关操作尤其不能使用 `--as user`,也不能省略 `--as bot`。
**不要依赖自动检测脚本**,因为 grep 模式可能匹配失败导致 fallback 到错误的 bot。
当前环境已确认 `lark-cli` 版本不低于 1.0.36;不要再把 "current 1.0.17 / 版本偏旧" 当成本任务问题。若未来命令参数异常,先执行 `lark-cli --version` 和对应子命令 `--help`,以实际版本帮助为准。

```bash
# 第一步:确认当前 profile 对应的 appId
lark-cli profile list
# 检查 active profile 的 appId 是否是 ai_bot (cli_a96ca9994c795bb4)

# 如果 active profile 不是 ai_bot,修复 ~/.lark-cli/openclaw/config.json
# 将其 appId 和 appSecret.id 改为 ai_bot 的值

# 第二步:验证能看到目标 wiki 空间
lark-cli wiki spaces list --as bot
# 必须看到 space_id=7630717889183534041 name='AI行研'
# 如果看不到,说明 profile 错了,立即停止修复

# 第三步:验证能读取商机表格
lark-cli sheets +read --as bot --spreadsheet-token FwBOsiErhh5U9Qtr5pvclx9Zncl --range "28609d!A1:J5"
# 返回客户名称等数据说明权限正常
```

## 关键参数速查

```
# 商机挖掘表格
spreadsheet_token: FwBOsiErhh5U9Qtr5pvclx9Zncl
sheet_id: 28609d
去重查询: 28609d!A:A(只查客户名称列)
追加写入: 28609d!A:J

# AI 行研知识库(注意:空间名称是 AI行研,没有空格)
space_id: 7630717889183534041
节点标题 / Word 文件名: AI-weekly-YYYYMMDD(wiki 节点标题和 Word 文件名保持一致)

# 当前 bot 身份
ai_bot: appId=cli_a96ca9994c795bb4
profile 配置文件: ~/.lark-cli/openclaw/config.json
```
