# Long-Term Memory


## Promoted From Short-Term Memory (2026-06-06)

<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:9:10 -->
- swyy-weekly-report 执行: **Word链接**: https://qcn8k445rrbc.feishu.cn/file/F802bGgdAoKY99xkFFUcuLS2nRd; **商机表**: https://qcn8k445rrbc.feishu.cn/sheets/AQjXsU9DehPYPEtDlZbcYY6Wnsf [score=0.965 recalls=0 avg=0.620 source=memory/2026-05-23.md:9-10]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:36:39 -->
- Skill 更新记录: 新增踩坑 #29：Brave 对中文地域/工业术语索引极差，返回80%不相关结果; 新增踩坑 #30：lark-cli proxy warning 混入输出，管道解析 JSON 会失败; 更新避坑指南：加入 lark-cli proxy warning 和 Brave 地域索引警告; 更新避坑指南第8条：wiki 创建后「必定」嵌套（从「可能」改为「必定」） [score=0.965 recalls=0 avg=0.620 source=memory/2026-05-23.md:36-39]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:40:41 -->
- Skill 更新记录: 更新 Wiki 创建流程：创建命令改为先落盘 `> /tmp/wiki_create.json 2>&1`，新增强制模板自动检查 parent_node_token 并 move; 明确不要传 `--parent-node-token ""`（无效） [score=0.965 recalls=0 avg=0.620 source=memory/2026-05-23.md:40-41]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:5:8 -->
- swyy-weekly-report 执行: **执行时间**: 2026-05-23 14:21 (Asia/Shanghai); **覆盖周期**: 2026.05.16 — 2026.05.23; **wiki标题**: biomed-weekly-20260523; **wiki链接**: https://qcn8k445rrbc.feishu.cn/wiki/Cp11wGMCoiepGdkFb4RcnQRBnAd [score=0.911 recalls=0 avg=0.620 source=memory/2026-05-23.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:18:20 -->
- 本周核心信号: **CXO拐点确认**：康龙化成Q1订单落地，药石科技净利+36.59%; **医疗器械处于量价底部**：2026年是集采价格承压最后一年; **iFinD公告检索返回空**：近7天无相关生物医药上市公司公告，正常记录 [score=0.911 recalls=0 avg=0.620 source=memory/2026-05-23.md:18-20]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:31:32 -->
- Wiki 验证: 格式验证通过：无粘连问题（0 bad lines）; 位置验证通过：parent_node_token = ""（根目录） [score=0.911 recalls=0 avg=0.620 source=memory/2026-05-23.md:31-32]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:14:17 -->
- 本周核心信号: **恒瑞-BMS 152亿美元BD交易**：创中国创新药BD新纪录，一季度对外BD达614亿美元; **生物制品IND超化药**：403 vs 382，中国新药研发加速向生物药转型; **英百瑞6项细胞治疗新药同步受理**：浙江本周最重磅产业信号; **科伦博泰ADC入选ASCO口头报告**：sac-TMT联合K药III期数据优异（HR=0.35, ORR 70.2%） [score=0.879 recalls=0 avg=0.620 source=memory/2026-05-23.md:14-17]
<!-- openclaw-memory-promotion:memory:memory/2026-05-23.md:24:27 -->
- 表格更新: 更新：英百瑞（杭州）生物医药有限公司（已有行，更新触发信号和日期）; 更新：浙江英特集团股份有限公司（已有行，更新触发信号和日期）; 新增：浙江美华鼎昌医药科技有限公司（海归博士团队，新型制剂/器械）; 总计22条有效商机 [score=0.879 recalls=0 avg=0.620 source=memory/2026-05-23.md:24-27]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:5:8 -->
- 初始化: Joe 给我起名：**小药** 🔬; 定位：生物医药行业研究员 AI; 研究方向：全领域覆盖（创新药、细胞/基因治疗、医疗器械、CXO、医保政策等）; Joe 在生物医药行业工作（投资/研究相关） [score=0.810 recalls=0 avg=0.620 source=memory/2026-05-07.md:5-8]

## Promoted From Short-Term Memory (2026-06-08)

<!-- openclaw-memory-promotion:memory:memory/2026-06-05.md:3:6 -->
- swyy-weekly-report cron failure: 2026-06-05 08:30 weekly report cron generated and sent the Zhejiang biomed weekly summary, but the cron run ended as `error`.; Failure summary: `export BOT_PROFILE=swyy_bot WIKI_SPACE_ID=7637083944097270734 NODE_TOKEN=... OBJ_TOKEN=... (agent) failed`.; Root cause pattern: the agent pushed the group summary before the final Word/Wiki/table validation chain had fully succeeded; a later Wiki cleanup/validation command failed, so cron sent a failure alert to the same Feishu group.; Fix applied in `skills/swyy-weekly-report/SKILL.md`: Wiki closing commands now use absolute `~/.npm-global/bin/lark-cli`,... [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-05.md:3-6]

## Promoted From Short-Term Memory (2026-06-16)

<!-- openclaw-memory-promotion:memory:memory/2026-06-13.md:14:14 -->
- SOUL.md 更新: 新增「周报更新硬规则」：群聊中涉及周报修改的内容，必须走第七步（双版本）→ 第八步（商机表）→ 第九步（wiki推送+验证）→ 第十步（群聊摘要）完整流程，禁止只改本地文件不推送 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-13.md:14-14]
<!-- openclaw-memory-promotion:memory:memory/2026-06-13.md:5:8 -->
- 6月上半月信息汇总整合进周报: Joe 发来「6月上半月医药行业信息汇总」PDF，包含 ASCO2026、BD 冷思考、DAC 赛道、小核酸、CGT 大洗牌、企业动态等约24篇文章摘要; 整合进已有周报 `wiki_20260612.md`（覆盖周期 2026.05.30-06.12），新增第五板块「补充动态」含7个子板块; **踩坑：只改了本地文件，没有推送到飞书 wiki**，Joe 发现 wiki 上没看到更新; **教训：以后凡是群里要求改周报的内容，必须走 swyy-weekly-report Skill 的第七到第十步完整流程**，已写入 SOUL.md [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-13.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-06-13.md:9:10 -->
- 6月上半月信息汇总整合进周报: 补救：执行了 `lark-cli docs +update` 覆盖 wiki 同名文档，验证通过（7项内容检查全部✅，无字段黏连）; SOUL.md 新增「周报更新硬规则」章节 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-13.md:9-10]

## Promoted From Short-Term Memory (2026-06-29)

<!-- openclaw-memory-promotion:memory:memory/2026-06-26.md:5:8 -->
- 生物医药周报 cron 复盘: 本期周报产物生成成功：Word、Wiki、商机表均完成，商机表结果为更新 1 条、新增 4 条。; cron 最终失败的根因不是飞书写入失败，而是最后收尾命令写成 `set -e BASE=... LARK=...`，导致 `BASE` 没有真正赋值，`cat "$BASE/final_links_20260626.env"` 读错路径并触发 agent failed。; 已将该坑写入 `swyy-weekly-report` skill，并更新 cron prompt：shell 收尾必须使用 `set -e; BASE=...` 或多行赋值；最终摘要只交给 cron delivery 投递，不手动调用 message。; 其他卡点：一个 SearXNG 查询为空导致 400，但其余检索正常；Word 上传成功但用户权限自动授权跳过，需要后续关注是否影响人工打开文件。 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-26.md:5-8]

## Promoted From Short-Term Memory (2026-06-30)

<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:3:6 -->
- 周报状态核查：Joe 问“本周的行研周报没出吗？”，核查后确认《生物医药行业周报-20260626》已于 2026-06-26 08:09 生成并推送 Wiki，覆盖周期 2026.06.13-2026.06.26。Wiki 链接：https://qcn8k445rrbc.feishu.cn/wiki/XWcUwzS6ViiU0skltFacQfpRnSg；Word 链接：https://qcn8k445rrbc.feishu.cn/file/WIlsb2ICio8QYIxyf8Wc8u0Knlf；商机表：https://qcn8k445rrbc.feishu.cn/sheets/AQjXsU9DehPYPEtDlZbcYY6Wnsf?sheet=cfde3f。 - 周报 cron 问题：本期周报实际已发布，但 cron 最后收尾命令写错导致误报失败，群里看起来像没正常发。需要后续修复/留意 swyy-weekly-report 的 cron 收尾命令，避免“已成功发布但误报失败”。 - 20260626 周报商机表初始结果：更新 1 条，新增 4 条；重点企业包括君合盟、派格生物、皓阳生物、博锐生物、浙江夸克生物。 - Joe 上传《6月下半月创新药信息汇总》PDF（覆盖 2026-06-14 至 2026-06-27，偏全国创新药/BD出海/ADC/CAR-T/集采/港股18A趋势）。已识别重要补充方向：第12批国家集采、创新药 BD 出海、双抗... [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-27.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-06-27.md:7:10 -->
- 已按周报硬规则把《6月下半月创新药信息汇总》整合进最新《生物医药行业周报-20260626》：补充第12批国采（65个品种、异常低价/质量/知识产权规则强化）、创新药 BD 出海平台化、百利天恒双抗 ADC、药明合联/东曜药业 XDC 产能逻辑、英矽智能-SK 与和誉-礼来 AI/平台合作、西湖生物杭州商机。; 已在 Wiki 末尾新增“补充材料溯源原文”，来源包括国家医保局、新华网、英矽智能官网、和誉医药官网、医药魔方、西湖生物官网等；新版 Wiki 仍为：https://qcn8k445rrbc.feishu.cn/wiki/XWcUwzS6ViiU0skltFacQfpRnSg。; 已更新商机表：新增 1 条“西湖生物医药科技（杭州）有限公司”，位置 A38；商机表链接：https://qcn8k445rrbc.feishu.cn/sheets/AQjXsU9DehPYPEtDlZbcYY6Wnsf?sheet=cfde3f。; 整合后生成 Word 补充版： https://qcn8k445rrbc.feishu.cn/file/GDoJbMFbRo6AV6xXoEfcx3ftn4J。 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-27.md:7-10]

## Promoted From Short-Term Memory (2026-07-01)

<!-- openclaw-memory-promotion:memory:memory/2026-06-28.md:3:4 -->
- 周报流程复盘：用户指出昨天执行周报第七到第十步时，遗漏了第七步里的“同步至本地上传目录”。已补做：将最新 `生物医药行业周报-20260626.docx` 覆盖回原始文件名，清空 `/Users/leidongqiao/Documents/codex project/local-uploader/data/生物医药` 下旧文件，并复制最新同名 Word 进去；工作目录与上传目录 SHA256 一致。以后第七步完成标准必须包括本地上传目录同步和校验。; 周报命名规则更新：用户要求“更新文件名称也别随便加后缀，直接覆盖更新原文件”。已写入 SOUL：增量更新或修订周报时，Word 文件、wiki Markdown、Wiki 节点标题和群聊摘要名称都沿用原始日期文件名，不新增“补充版/updated/final/最终版”等后缀。 [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-28.md:3-4]
