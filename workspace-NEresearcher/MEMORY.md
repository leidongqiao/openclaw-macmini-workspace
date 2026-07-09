# Long-Term Memory

- 2026-07-09: Joe 明确偏好：以后修改现有 skill 时先直接写 live 文件并验证，不要把 pending proposal 当作最终交付；Skill Workshop 只做记录/审计，不作为阻止写入的审批关卡，避免繁琐弹框。

## Promoted From Short-Term Memory (2026-06-06)

<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:21:24 -->
- 新能源周报 cron 与飞书推送排查: `wiki +move` 实际返回成功：`ok: true`，`parent_node_token: ""`，`space_id: "7637082931059706850"`；节点 `Hbtwwve09iXkUHkAijdcXqUknAf` 已在根目录。; 真正失败的是后续 `docs +update` 参数使用了旧写法：`--mode overwrite --markdown @./wiki_content.md`; 当前 `lark-cli docs +update --api-version v2` 需要：`--command overwrite --content @... --doc-format markdown`; 错误验证信息包括 `--command is required` 和 `--command overwrite requires --content`。 [score=1.000 recalls=0 avg=0.620 source=memory/2026-05-28.md:21-24]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:5:8 -->
- 新能源周报 cron 与飞书推送排查: 18:14 左右，cron `ne-weekly-research-report` 执行 `ne-weekly-report` skill，要求严格读取全量 skill 内容，生成本周新能源行业研究周报，聚焦浙江。; 本次生成的对外摘要为：; 标题：`新能源商机周报·浙江｜2026.05.22-05.28`; 主线：多用户绿电直连、储能高排产、光伏组件分化 [score=1.000 recalls=0 avg=0.620 source=memory/2026-05-28.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-05-29.md:3:6 -->
- 09:38 Joe 反馈 `ne-weekly-research-report` cron 把失败通知推送到了飞书群。核查后确认周报 Word/Wiki/商机表/摘要已生成并成功推送，失败是后续 `docs +update` 收尾步骤被 runtime 记录为 error，导致 announce delivery 向同一飞书群发送 failure notification。; 已处理：将 `skills/ne-weekly-report/SKILL.md` 中第九步残留的旧 `docs +update --mode overwrite --markdown` 操作说明改为 v2 写法：`--api-version v2 --command overwrite --content @./wiki_content.md --doc-format markdown`；并更新 cron payload，强调非关键收尾步骤失败只记内部日志，不应让 cron 以 error 结束。; 已处理：将 cron `ad7728d0-5dc4-4674-b822-2f86c1286ff3` 的 `failureAlert` 设为 `false`，避免后续失败告警继续打到群聊；正常成功摘要仍通过原 `delivery.announce` 发到群。; 09:55 Joe 追问为什么这些坑反复出现。复盘结论：不是没有记录，而是记录分散、旧命令和新命令并存、软性提醒不能阻止... [score=1.000 recalls=0 avg=0.620 source=memory/2026-05-29.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:13:16 -->
- 新能源周报 cron 与飞书推送排查: Wiki: `https://qcn8k445rrbc.feishu.cn/wiki/Hbtwwve09iXkUHkAijdcXqUknAf`; 商机表: `https://qcn8k445rrbc.feishu.cn/wiki/C5ZgwhqJciryiTkGLH0cvlXzn5b?fromScene=spaceOverview`; Joe 19:32 询问为什么推送到飞书群聊。排查发现不是模型临时决定，而是 cron delivery 配置中写了飞书群目标：; `ne-weekly-research-report` 的 delivery 为 `channel: feishu`, `to: oc_8cb0dc6f77d3a46ef37259ee4d913727` [score=0.941 recalls=0 avg=0.620 source=memory/2026-05-28.md:13-16]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:17:20 -->
- 新能源周报 cron 与飞书推送排查: 另有独立“周五行业摘要播报”任务会读取 `reports/summary/NE-summary.md` 并发到 `oc_a387040cc398a4f050fb50109486531b`; Joe 19:34 追问为什么群里没推上面的摘要而是报错信息。原因：摘要文件已生成，但本次 cron 最终状态被记录为 `error`，OpenClaw announce delivery 因失败状态发送了 failure notification，而不是正常 summary。; 起初日志摘要看起来像 `lark-cli wiki +move ... failed`，后续进一步确认实际不是 `wiki +move` API 本身失败：; 原命令把两步串在一条 shell 中：`lark-cli wiki +move ... && lark-cli docs +update ...` [score=0.919 recalls=0 avg=0.620 source=memory/2026-05-28.md:17-20]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:25:28 -->
- 新能源周报 cron 与飞书推送排查: 因为整条 shell 命令以 `wiki +move` 开头，runtime 截断后的错误摘要误导成 move 失败。; 后来已用正确参数补跑 `docs +update` 成功，但由于先前工具调用已被 runtime 记录为错误诊断，cron 仍按失败任务处理，导致群里收到错误通知。; 已修改 `skills/ne-weekly-report/SKILL.md` 的思路：`wiki +move` 作为非关键收尾步骤处理。以后先检查是否已在根目录；已在根目录则跳过 move；不在才 move。move 失败最多重试 1 次，仍失败只写内部日志，不应中断任务；摘要写入与群推送不应被非关键归档/移动步骤阻断。; 经验：周报生成任务中，外部可见推送应以摘要生成成功为准。Wiki 归档、移动、排序、刷新这类整理步骤必须降级为非关键错误，避免把用户可读摘要替换成底层报错推送到群里。 [score=0.919 recalls=0 avg=0.620 source=memory/2026-05-28.md:25-28]
<!-- openclaw-memory-promotion:memory:memory/2026-05-28.md:9:12 -->
- 新能源周报 cron 与飞书推送排查: 浙江机会：机制电价落地后，分布式光伏、工商业储能、交通场站光储充项目进入可测算窗口; 优先跟进：正泰新能、运达能源科技、容百科技; 切入方向：供应链金融/票据保函/设备融资/跨境结算/数字财资; Word: `https://qcn8k445rrbc.feishu.cn/file/OIrmbJGNSoehzmxBNwIcWeyrnoh` [score=0.919 recalls=0 avg=0.620 source=memory/2026-05-28.md:9-12]
<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:12:13 -->
- 周报生成 (18:27): 浙江新三样/风电出口数据亮眼; 必访企业：吉利富江能源（P0） [score=0.836 recalls=0 avg=0.620 source=memory/2026-05-11.md:12-13]
<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:8:11 -->
- 周报生成 (18:27): 四部门《AI与能源双向赋能行动方案》（★★★★★）; 吉利桐庐钠电产线落地（★★★★，浙江本地）; 光伏组件五巨头Q1集体亏损96亿; 风电出海收入超300亿 [score=0.836 recalls=0 avg=0.620 source=memory/2026-05-11.md:8-11]
<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:3:6 -->
- 周报生成 (18:27): 生成本周周报 ne-weekly-20260511 (覆盖05.05-05.11); 知识库链接: https://www.feishu.cn/wiki/PU9Gw6ptLixFUqkNX2kcB1b9n8g; 商机表格已更新（吉利富江能源日期更新为05-11）; 推送到飞书群 oc_8cb0dc6f77d3a46ef37259ee4d913727 [score=0.826 recalls=0 avg=0.620 source=memory/2026-05-11.md:3-6]

## Promoted From Short-Term Memory (2026-06-07)

<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:4:6 -->
- 初始化: 完成了 bootstrap，身份设定为新能源行业研究员 🔋; 用户：Joe，时区 Asia/Shanghai; 研究方向：光伏、风电、储能、氢能、电动汽车及产业链 [score=0.804 recalls=0 avg=0.620 source=memory/2026-05-07.md:4-6]
