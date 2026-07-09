# Long-Term Memory


## Promoted From Short-Term Memory (2026-05-06)

<!-- openclaw-memory-promotion:memory:memory/2026-05-01.md:3:3 -->
- 用户反馈周报格式太丑，要求美化。 [score=0.878 recalls=0 avg=0.620 source=memory/2026-05-01.md:3-3]
<!-- openclaw-memory-promotion:memory:memory/2026-05-01.md:12:12 -->
- **更新文件：** `skills/ai-weekly-report/SKILL.md` 第七步模板 [score=0.878 recalls=0 avg=0.620 source=memory/2026-05-01.md:12-12]

## Promoted From Short-Term Memory (2026-05-07)

<!-- openclaw-memory-promotion:memory:memory/2026-05-01.md:5:5 -->
- **改动内容：** [score=0.834 recalls=0 avg=0.620 source=memory/2026-05-01.md:5-5]

## Promoted From Short-Term Memory (2026-06-13)
- 东桥要求：1）双周报银行展业机会必须写明具体产品名称和推荐原因，不能空泛写业务方向；2）商机清单已有的企业不再重复推荐，写入前必须用核心简称精确匹配去重。
- 群聊中凡是要求改周报的内容，都必须走 skill 第七到第十步完整流程（生成双版本→更新商机表→写入知识库→推送群聊摘要），不能只改局部。

## Promoted From Short-Term Memory (2026-06-06)

<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:3:5 -->
- AI 周报发布后，发现「商机表」链接曾把 sheet token 错拼为 wiki URL。后续凡是发飞书链接前，必须用 `lark-cli drive +inspect` 校验最终 URL 的 `type/title/token`。; 东桥要求 AI 行研知识库根目录按「商机挖掘」在前、周报按时间倒序排列。已验证飞书 wiki API 不支持指定 sibling 插入位置，但 `wiki +move --target-space-id <space_id>` 会把节点追加到根目录末尾。已把 `AI-weekly-20260528` 调整到「商机挖掘」后面，并在 `skills/ai-weekly-report/SKILL.md` 写入后续固定重排规则。; 东桥要求 AI 周报 Word 生成流程同步本地上传目录：生成前清空 `/Users/leidongqiao/Documents/ codex project/local-uploader/data/AI/` 内文件但保留目录，生成后复制一份 `AI-weekly-YYYYMMDD.docx` 到该目录。已写入 `skills/ai-weekly-report/SKILL.md` 第七步 Word 输出要求。 [score=1.000 recalls=0 avg=0.620 source=memory/2026-05-28.md:3-5]
<!-- openclaw-memory-promotion:memory:memory/2026-05-20.md:4:7 -->
- AI 行业周报生成（2026-05-20）: 覆盖期间：2026-05-13 至 2026-05-20; Word 版：~/.openclaw/workspace/AI行研/行业商机周报_AI_20260520.docx; Wiki 版：https://www.feishu.cn/wiki/QBJ9wAhHpiwKdZknH97cMdornjh; 商机表格：新增 3 家（阶跃星辰、华虹公司-浙江供应链、能科科技），共 36 家 [score=0.930 recalls=0 avg=0.620 source=memory/2026-05-20.md:4-7]
<!-- openclaw-memory-promotion:memory:memory/2026-05-20.md:8:8 -->
- AI 行业周报生成（2026-05-20）: 核心信号：中国AI大模型融资决战周（月之暗面20亿/阶跃星辰25亿/DeepSeek 515亿估值）、国家具身智能中试基地在杭揭牌、宁波AI+制造方案、芯片产业链大涨 [score=0.930 recalls=0 avg=0.620 source=memory/2026-05-20.md:8-8]

## Promoted From Short-Term Memory (2026-06-15)

<!-- openclaw-memory-promotion:memory:memory/2026-06-12.md:3:3 -->
- 修复飞书 `docs +update` 旧参数残留：2026-06-12 09:00 `ai-weekly-research-report` cron 因旧写法 `--mode overwrite --markdown` 被 OpenClaw 判定失败，实际周报产物已生成。已将相关 reusable skills 中的可执行模板统一改为 `--api-version v2 --command overwrite --doc-format markdown --content @./file.md`，并清理 workspace 内其他周报 skill 的旧参数说明，避免后续代理误用。 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-12.md:3-3]

## Promoted From Short-Term Memory (2026-06-29)

<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:11:13 -->
- 2026-06-26 09:30 Asia/Shanghai - Pre-compaction memory flush: Before compaction, a command output showed `lark-cli profile list` beginning with profiles: `default` appId `cli_a96ca9994c795bb4` active true, `bdt_bot` appId `cli_a9719ed2abf55bc8`, `ne_bot` appId `cli_a97152fac6b81bd4`; output was truncated, so continue checking full profiles/config instead of assuming.; A command output also exposed product-matching material for Ping An Bank.... [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-26.md:11-13]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:3:6 -->
- 2026-06-26 09:30 Asia/Shanghai - Pre-compaction memory flush: Active task before compaction: cron `ad52930e-d9ed-4b81-a40f-9c289606fee8 ai-weekly-research-report` asked to execute `ai-weekly-report` skill and generate this week's AI industry research weekly report. Current date/time at trigger was Friday 2026-06-26 09:00 Asia/Shanghai.; Must continue from the existing task, not restart casually.... [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-26.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:7:10 -->
- 2026-06-26 09:30 Asia/Shanghai - Pre-compaction memory flush: Search/fetch pitfalls to preserve: prefer SearXNG, inspect quality; if poor, rewrite query first with year/month/Zhejiang/policy/financing/pilot/base etc.; only then serially fall back to Brave with >=1.2s spacing. Vertical-source 403/JS failures should be recorded internally and skipped after one attempt.; iFinD pitfall: `call-node.js` is a module, not direct CLI. Create a temp JS script requiring it and call `call(server_type, tool_name, params)`, check `ok`, delete temp script.... [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-26.md:7-10]
