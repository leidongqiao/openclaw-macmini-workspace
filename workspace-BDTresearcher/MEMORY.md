# Long-Term Memory

- Joe 偏好：当他明确要求修改现有 skill / 工作流规则时，直接修改 live 文件并验证结果，不要先走“生成提案/等待应用”的弹框流程。只有在他明确要求创建可复用提案、审批、分享或不确定是否要落地时，才使用 proposal 方式。


## Promoted From Short-Term Memory (2026-06-06)

<!-- openclaw-memory-promotion:memory:memory/2026-05-25.md:11:11 -->
- 2026-05-25 16:54 memory flush: Joe preference from this exchange: when workflow issues happen, he wants root cause, direct fixes, and process hardening in the skill so the same pitfall is not repeated. [score=0.975 recalls=0 avg=0.620 source=memory/2026-05-25.md:11-11]
<!-- openclaw-memory-promotion:memory:memory/2026-05-25.md:3:6 -->
- 2026-05-25 16:54 memory flush: Joe asked to audit the generated BDT semiconductor weekly report against `skills/bdt-weekly-report/SKILL.md`. Result: report was broadly compliant and deliverable; issues found were process/audit gaps rather than content failures.; Weekly report outputs from earlier today: Word `https://www.feishu.cn/file/Lz5FblicoofdOMxmtNDcD4nnnYg`, Wiki `https://www.feishu.cn/wiki/CPtOw0w7ui6TjWko8MicROWdnAc`, business sheet `https://www.feishu.cn/sheets/RpI5svn81hl9axtuaqUcwtAenBM?sheet=89c832`.; SearXNG failure root cause: service was up, but `/tmp/searxng-config/settings.yml` had `search.formats: [html]`, so... [score=0.975 recalls=0 avg=0.620 source=memory/2026-05-25.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-05-25.md:7:10 -->
- 2026-05-25 16:54 memory flush: Weekly report process pitfalls identified: incomplete source material landing/audit trail; Wiki node initially created under non-root parent then moved to root; Feishu permission grant `skipped` can be benign; Wiki fetch may convert plain URLs to markdown links; sheet reads beyond row_count can show null rows and cause false alarms; product name should use `商票e贴`; `docs +fetch` v1 deprecation should be recorded.; Updated `skills/bdt-weekly-report/SKILL.md` to prevent repeat issues: force Wiki root creation with `--parent-node-token ""` and immediate parent check/move fallback; SearXNG JSON API... [score=0.975 recalls=0 avg=0.620 source=memory/2026-05-25.md:7-10]
<!-- openclaw-memory-promotion:memory:memory/2026-05-29.md:1:4 -->
- 2026-05-29 14:00 BDT 周报 cron 再次把错误日志推到飞书群。根因不是三项产物失败，Word/Wiki/商机表与 `reports/summary/BDT-summary.md` 都已生成；cron 最终状态被一个非核心 shell 展示/查看命令失败覆盖：`run for f → run do echo → show $f → print text → run done`，OpenClaw `delivery.mode=announce` 在 `status=error` 时投递 failure notification。; 已补发正确极简摘要到「半导体行研」群 `oc_2363a2114d6d509dbb01abc63cb41831`，bot 身份 `bdt_bot`，消息 ID `om_x100b6ea69697c490c2bd1246469c9f2`。; 已更新 cron `bdt-weekly-research-report`：设置 `failureAlert:false`，并强化 payload：摘要文件生成后不要再执行任何工具调用；最终 assistant 回复只能是第十步极简摘要。; 已更新 `skills/bdt-weekly-report/SKILL.md`：新增“最终工具调用禁令”，`BDT-summary.md` 写入后不得再执行 `cat`、`for f... [score=0.958 recalls=0 avg=0.620 source=memory/2026-05-29.md:1-4]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:12:13 -->
- 2026-05-28 周报执行复盘: 执行中踩坑：1）非核心校验失败会让 cron 整体标红；2）`lark-cli` 输出不总是纯 JSON；3）Wiki 节点创建后可能默认进入“首页”下，需要 move 回根目录；4）`wiki +move` 参数应使用 `--target-parent-token`，不是 `--parent-node-token`；5）`docs +fetch` 有 deprecated 提示但功能可用，不应贸然改未验证路径；6）商机表需处理公司别名归一，如甬矽电子相关名称；7）清理表格残留行后要确认 `row_count`，但此类检查不得阻断摘要发送。; 已按“增改查、不重复”复核 `skills/bdt-weekly-report/SKILL.md`：已有的别名去重、row_count、根目录、deprecated、摘要交付规则不重复添加；补充了 `lark-cli` 首个完整 JSON 对象解析 helper；修正了 Wiki 排序说明，`wiki +move` 只能用 `--target-parent-token`，精确排到商机表之后要用原生 Wiki move API 的 `after_node_token`，不要写不存在的 `wiki +move --after-node-token`。 [score=0.951 recalls=0 avg=0.620 source=memory/2026-05-28.md:12-13]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:8:11 -->
- 2026-05-28 周报执行复盘: 本次 cron `bdt-weekly-research-report` 生成了本周半导体行业研究周报（聚焦浙江）。产物链接：Word `https://www.feishu.cn/file/QI6cbHbSEoDzO3xzRvwcyNvSn0U`；Wiki `https://www.feishu.cn/wiki/Ik3MwaW6QiqSVtkD91Nc6ZTqndc`；商机表 `https://www.feishu.cn/sheets/RpI5svn81hl9axtuaqUcwtAenBM?sheet=89c832`。; 摘要内容：主线是设备更新再贷款、AI 算力/先进封装、设备材料国产化；浙江机会包括杭州钱塘芯谷+长芯展升温、宁波封测/材料、衢州电子化学品；优先跟进士兰微、长川科技、甬矽电子；切入方向是技改融资/票据/供应链金融/跨境结算。; 失败命令性质：失败发生在商机表写入后的只读校验脚本，读取 `reports/bdt-weekly/sheets_read_verify.json` 并解析前几行确认字段，不是核心生成、上传、写 Wiki 或写表动作。; 失败原因：`lark-cli` 输出文件中正常 JSON 后混入 warning/notice 文本，脚本把从第一个 `{` 到文件末尾整体传给 `json.loads()`，触发 `JSONDecodeError: Extra data`。后续用“截取首个完整... [score=0.951 recalls=0 avg=0.620 source=memory/2026-05-28.md:8-11]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:3:4 -->
- BDT 周报 cron 摘要交付规则: Joe 明确要求：以后周报流程中，不影响结果产物的错误（只读校验、JSON 解析、重复行检查、排序检查、临时文件清理、CLI warning/notice 等）直接忽略或记 warning，不得影响结果摘要输出；必须继续把极简摘要发到配置的飞书群聊。; 2026-05-28 的半导体周报实际 Word/Wiki/商机表已成功，但一次商机表校验 JSON 解析失败导致 cron 标红并阻断群聊摘要。已将规则写入 `skills/bdt-weekly-report/SKILL.md`，并更新 cron `bdt-weekly-research-report` payload。 [score=0.919 recalls=0 avg=0.620 source=memory/2026-05-28.md:3-4]
<!-- openclaw-memory-promotion:memory:memory/2026-05-22.md:3:4 -->
- bdt-weekly-report skill hardening: Updated `skills/bdt-weekly-report/SKILL.md` after repeated 2026-05-22 weekly-report pitfalls.; Added safeguards for missing `config.json`, SearXNG result drift (EDA/HBM false positives), iFinD local Node script requirement, Drive `file_token` URL construction, wiki fetch regex false positives (`data.markdown` only), wiki Word-link pure URL format, company alias dedupe for repeated entities such as 甬矽电子, and zsh-safe summary cleanup using `find ... -delete` instead of `rm -f dir/*`. [score=0.871 recalls=0 avg=0.620 source=memory/2026-05-22.md:3-4]
<!-- openclaw-memory-promotion:memory:memory/2026-05-15.md:16:17 -->
- 14:00 BDT 半导体行业周报生成（2026.05.09-05.15）: **知识库**：创建成功，URL: https://www.feishu.cn/wiki/EsbFwkDGri17wSkuMXvceiNEn3g; **技术问题**：docx API text block (type=12) 返回 invalid param，改用 quote block (type=15) 代替 [score=0.867 recalls=0 avg=0.620 source=memory/2026-05-15.md:16-17]
<!-- openclaw-memory-promotion:memory:memory/2026-05-15.md:4:7 -->
- 14:00 BDT 半导体行业周报生成（2026.05.09-05.15）: **触发**：cron 定时任务 bdt-weekly-research-report; **信息源**：同花顺、财联社、新华网、经济观察网 + 5组 web_search + 垂直源; **iFinD**：新闻/公告检索成功，热点事件查询 time_scope 参数失败; **浙江重点事件**： [score=0.867 recalls=0 avg=0.620 source=memory/2026-05-15.md:4-7]

## Promoted From Short-Term Memory (2026-06-07)

<!-- openclaw-memory-promotion:memory:memory/2026-05-15.md:8:11 -->
- 14:00 BDT 半导体行业周报生成（2026.05.09-05.15）: 中欣晶圆科创板IPO获受理（募资54.7亿）; 杰华特模拟芯片IPO过会; 《浙江省新型工业化规划》发布（2030年集成电路营收目标4500亿）; 创豪半导体22亿IC载板一期设备搬入 [score=0.859 recalls=0 avg=0.620 source=memory/2026-05-15.md:8-11]

## Promoted From Short-Term Memory (2026-06-10)

<!-- openclaw-memory-promotion:memory:memory/2026-06-07.md:3:3 -->
- 18:27 Joe 反馈商机表客户名单重复度过高，确认执行三项改进： [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-07.md:3-3]
<!-- openclaw-memory-promotion:memory:memory/2026-06-07.md:4:6 -->
- 1) **冷却规则**：最近2期推荐企业进入冷却，锚定企业最多保留1-2家，重复率≤40% 2) **新标的补充搜索**：新增第13.5轮 SearXNG 搜索「浙江半导体 专精特新/小巨人/融资/投产/产业园/招商」 4) **商机表轮换**：已closed或超过N周无更新的企业降权 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-07.md:4-6]
<!-- openclaw-memory-promotion:memory:memory/2026-06-07.md:7:10 -->
- 已更新 `skills/bdt-weekly-report/SKILL.md`：; 新增第1.5节「企业推荐轮换规则」; 新增第13.5轮非上市/专精特新补充搜索; 新增第10.0步冷却名单记录（recommended_companies_latest.txt） [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-07.md:7-10]

## Promoted From Short-Term Memory (2026-06-11)

<!-- openclaw-memory-promotion:memory:memory/2026-06-07.md:11:12 -->
- 新增注意事项16（企业推荐轮换自检）; 更新源审计留痕，覆盖13.5轮 [score=0.869 recalls=0 avg=0.620 source=memory/2026-06-07.md:11-12]
