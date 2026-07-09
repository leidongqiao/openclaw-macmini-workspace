# Long-Term Memory


## Promoted From Short-Term Memory (2026-06-06)

<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:5:8 -->
- im-weekly-report 修复: Joe 指出本周智能制造周报 Wiki 知识库文档出现乱码/转义问题，且生成后未充分自检。; 核查发现当前 Wiki `im-weekly-20260528` 正文被写成 JSON 字符串，中文显示为 `\uXXXX` 转义；根因是写入链路把 JSON 编码后的 Markdown 当正文写入。; 已用本地 `reports/im-weekly/im-weekly-20260528.md` 通过 `docs +update --api-version v2 --command overwrite --doc-format markdown --content @file` 覆盖修复，并 fetch 回读确认无 Unicode 转义、JSON/XML 正文化、字段黏连，Word 链接存在。; 已更新 `skills/im-weekly-report/SKILL.md`：新增 Wiki 回读校验、乱码/转义失败判定、大段 Markdown 必须 `@file` 传参、Word 链接一致性、本地同步目录唯一性、推送前发布链路自检等规则。 [score=1.000 recalls=0 avg=0.620 source=memory/2026-05-28.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:9:9 -->
- im-weekly-report 修复: 纠正一处误判：Joe 确认本地同步目录真实路径就是 `/Users/leidongqiao/Documents/ codex project/local-uploader/data/智能制造`，`Documents/` 后的空格不是错误。已把 skill 中相关规则改回带空格路径。 [score=1.000 recalls=0 avg=0.620 source=memory/2026-05-28.md:9-9]
<!-- openclaw-memory-promotion:memory:memory/2026-05-22.md:5:6 -->
- SKILL.md 修复：执行日志混入周报正文: **问题**：周报正文/群聊推送中出现了执行日志（如「36氪研究院入口页存在404/页面删除，已按规则记录并跳过；iFinD公告探测成功，长查询返回空结果，热点事件接口无权限」）; **根因**：SKILL.md 多处明确指示 agent 在报告中标注跳过/失败/无权限等状态 [score=0.961 recalls=0 avg=0.620 source=memory/2026-05-22.md:5-6]
<!-- openclaw-memory-promotion:memory:memory/2026-05-22.md:8:11 -->
- SKILL.md 修复：执行日志混入周报正文: 新增「报告正文纯净锁」规则（SKILL.md 第八步下方），明确禁止 6 类执行日志出现在 Word/Wiki 正文; 修改所有「在报告中标注」为「不要在报告正文中标注」（4 处）; 修改「记录并继续」为「继续」（2 处）; 失效名单、JS 渲染失败跳过时增加「不要在报告中提及」 [score=0.932 recalls=0 avg=0.620 source=memory/2026-05-22.md:8-11]
<!-- openclaw-memory-promotion:memory:memory/2026-05-29.md:3:6 -->
- 修复智能制造周报 cron 群聊误推错误诊断：本次 `im-weekly-research-report` 已生成正确 `reports/summary/IM-summary.md`，但 cron 因一次 `lark-cli docs +update` 工具失败将运行标记为 error，OpenClaw 自动把失败诊断推送到飞书群，而不是推送摘要。; 已补发正确周报摘要到飞书群 `oc_fb74967477b8b68e2818ac14d837f55a`。; 已更新 cron `36858a7f-4374-4144-905b-9069e17b1ad2`：`delivery.mode=none`、`failureAlert=false`，payload 明确要求完成自检后读取 `reports/summary/IM-summary.md` 并用 `message` 工具显式发送到目标飞书群。; 已更新 `skills/im-weekly-report/SKILL.md`：新增 cron 投递规则，禁止依赖 cron delivery 自动转发最终回复或失败诊断；定时任务必须显式发送极简摘要。 [score=0.926 recalls=0 avg=0.620 source=memory/2026-05-29.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-05-22.md:12:13 -->
- SKILL.md 修复：执行日志混入周报正文: 更新「信息源全部失败」特殊场景指引; 踩坑记录新增 #13 [score=0.912 recalls=0 avg=0.620 source=memory/2026-05-22.md:12-13]
<!-- openclaw-memory-promotion:memory:memory/2026-05-22.md:17:20 -->
- 周报发布补救：lark-cli OpenClaw bind 与 bot profile: **问题**：2026-05-22 周报生成后，飞书发布阶段误走 OpenClaw 飞书工具/user 授权路径，返回 `need_user_authorization`；改按 skill 使用 `lark-cli --as bot` 时，lark-cli 又提示 OpenClaw context 未绑定。; **处理**：按用户确认的 bot 路线执行 `lark-cli config bind --source openclaw --app-id cli_a9715315cdb8dbcf --identity bot-only`，随后实际可用 profile 为 `cli_a9715315cdb8dbcf`，不是旧配置里的 `im_bot`。; **结果**：Word 已上传并设置为组织内链接可读，Wiki `im-weekly-20260522` 已覆盖写入并 fetch 抽查，商机表已写入/排序/清理，`reports/summary/IM-summary.md` 已补齐 Word/Wiki/商机表链接。; **后续规则**：`im-weekly-report/config.json` 的 `bot_profile` 已改为 `cli_a9715315cdb8dbcf`；后续周报发布务必先读 config，并统一使用该 profile + `--as bot`。 [score=0.871 recalls=0 avg=0.620 source=memory/2026-05-22.md:17-20]
<!-- openclaw-memory-promotion:memory:memory/2026-05-21.md:5:8 -->
- 执行结果: 成功生成 Word 版周报 + Wiki 版 + 商机表更新; 6 家企业推荐：宇树科技(P0)、云深处科技(P0)、宁波中亿智能(P1)、柔荷新能源(P1)、瑞凌新能源(P1)、昂霖智能(P2); Wiki 链接：https://www.feishu.cn/wiki/PCx3wWwSSiNDZdkjiPOc2UCYnhb; Word：https://qcn8k445rrbc.feishu.cn/file/JdWzbCdDloTCvbxmepXcLRAknBb [score=0.864 recalls=0 avg=0.620 source=memory/2026-05-21.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-05-21.md:11:14 -->
- 踩坑记录(已写入 SKILL.md): lark-cli 不在 PATH，绝对路径 ~/.npm-global/bin/lark-cli; 证券时报 404、IT之家 404、36氪研究院 404 — 跳过; searxng JSON 输出被截断 — 先落盘再解析; iFinD search_trending_news 403、search_notice 空 — 正常标注 [score=0.864 recalls=0 avg=0.620 source=memory/2026-05-21.md:11-14]
<!-- openclaw-memory-promotion:memory:memory/2026-05-21.md:15:18 -->
- 踩坑记录(已写入 SKILL.md): Wiki 节点创建后挂在子目录 — +move 移回根; 商机表去重别名问题：杭州云深处 vs 云深处科技（杭州）— 需映射表; 排序 key 有 None 报 TypeError — str(r[8] or ''); 宇树旧状态 active 与新增待联系混用 — 符合规则 [score=0.864 recalls=0 avg=0.620 source=memory/2026-05-21.md:15-18]

## Promoted From Short-Term Memory (2026-06-07)

<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:4:7 -->
- Initialization: Joe 上线，完成首次对话; 设定身份：**小智** — Joe 的智能制造行业研究员; 研究方向：工业4.0、数字化工厂、工业互联网、工业机器人、AI+制造、工业软件等; 更新了 IDENTITY.md、USER.md、SOUL.md [score=0.804 recalls=0 avg=0.620 source=memory/2026-05-07.md:4-7]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:11:12 -->
- TODO: [ ] 了解 Joe 具体的研究需求（细分领域、公司、市场）; [ ] 了解 Joe 偏好的信息格式（报告、简报、数据表） [score=0.804 recalls=0 avg=0.620 source=memory/2026-05-07.md:11-12]

## Promoted From Short-Term Memory (2026-07-06)

<!-- openclaw-memory-promotion:memory:memory/2026-07-03.md:1:1 -->
- im-weekly-research-report cron 误向飞书群发送失败告警：2026-07-03 执行周已成功用 message 工具显式发送 `reports/summary/IM-summary.md` 到群，但 agent 后续因 `lark-cli docs +fetch`/自检脚本 `SystemExit(2)` 被标记失败；由于 cron 配置仍是 `delivery.mode=announce`，OpenClaw 又把失败通知投递到同一飞书群。已将 cron `ebf528b4-bcce-4030-98d9-09659c0f58fb` 更新为 `delivery.mode=none`、`failureAlert=false`，后续只允许通过 message 工具发送通过自检的摘要。 [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-03.md:1-1]
