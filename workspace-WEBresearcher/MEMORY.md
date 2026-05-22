# Long-Term Memory


## Promoted From Short-Term Memory (2026-05-12)

<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:51:51 -->
- export PATH="$HOME/.npm-global/bin:$PATH" [score=0.902 recalls=0 avg=0.620 source=memory/2026-05-07.md:51-51]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:3:3 -->
- > 2026-05-07 以机器人身份在"互联网行研"知识库创建文档，耗时 ~25 分钟 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:3-3]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:21:21 -->
- `~/.lark-cli/config.json` 指向 keychain，但 keychain 里没有。真实凭证在 `~/.openclaw/openclaw.json` → `channels.feishu.accounts`。 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:21-21]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:24:24 -->
- 等用户手动提供。应该先调 `GET /open-apis/wiki/v2/spaces`。 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:24-24]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:27:27 -->
- API 返回 `131006 permission denied`。用哪个 bot 的 token 都行，问题是 wiki 空间成员列表里没有这个 bot。需要先加为管理员。 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:27-27]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:30:30 -->
- 裸调 `docx/v1/documents/{id}/blocks/{id}/children` 连续报三个错：`99992402`、`1770001`、`1770029`。应该直接用 `feishu_update_doc`。 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:30-30]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:33:33 -->
- `openclaw agent` 命令启动子进程很慢（每次要等 30-60s），来回调了好几次（添加管理员、更新文档内容）。其实拿到凭证后直接用 curl 调 API 更快。 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:33-33]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:36:36 -->
- 同一个问题踩了两遍： [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-07.md:36-36]

## Promoted From Short-Term Memory (2026-05-13)

<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:40:40 -->
- 本质是坑 1 的连锁反应——lark-cli 就在 `~/.npm-global/bin` 里，只是 PATH 没覆盖到。 [score=0.861 recalls=0 avg=0.620 source=memory/2026-05-07.md:40-40]
<!-- openclaw-memory-promotion:memory:memory/2026-05-07.md:54:55 -->
- APP_ID=$(jq -r '.channels.feishu.accounts.web_bot.appId' ~/.openclaw/openclaw.json) APP_SECRET=$(jq -r '.channels.feishu.accounts.web_bot.appSecret' ~/.openclaw/openclaw.json) [score=0.861 recalls=0 avg=0.620 source=memory/2026-05-07.md:54-55]
<!-- openclaw-memory-promotion:memory:memory/2026-05-08.md:5:5 -->
- 执行了互联网行业研究周报生成（聚焦浙江），覆盖 2026.05.02-05.08。 [score=0.827 recalls=0 avg=0.620 source=memory/2026-05-08.md:5-5]

## Promoted From Short-Term Memory (2026-05-18)

<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:5:5 -->
- 生成本周互联网行业研究周报（2026.05.05-05.11，聚焦浙江） [score=0.885 recalls=0 avg=0.620 source=memory/2026-05-11.md:5-5]

## Promoted From Short-Term Memory (2026-05-22)

<!-- openclaw-memory-promotion:memory:memory/2026-05-08.md:22:34 -->
- - 宁波：美团快乐猴进入、灯具产业带出海 - 嘉兴：盒马NB长三角布局 - 金华：义乌小商品跨境电商+GEO数字化 - 温州：入夏即时零售需求释放 ### 商机挖掘 - 写入5条必访商机到表格（ZvM9scRdph9aqzthwPAchTJ8nTe） - 表格此前为空，本次为首批写入 ### 知识库 - 创建 internet-weekly-20260508 文档（根目录） - Wiki URL: https://www.feishu.cn/wiki/IPRww7FkWiDxwokDLwYc6prynWd [score=0.948 recalls=4 avg=1.000 source=memory/2026-05-08.md:22-34]
