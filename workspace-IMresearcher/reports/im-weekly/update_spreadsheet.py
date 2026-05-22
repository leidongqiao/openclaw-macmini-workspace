#!/usr/bin/env python3
"""更新商机挖掘表格：去重、写入、排序、清理"""
import json, subprocess, urllib.request, urllib.error

SPREADSHEET_TOKEN = "HheAswhqEhm6QSt17DjclAdGn8c"
SHEET_ID = "a39f2b"
APP_ID = "cli_a9715315cdb8dbcf"
APP_SECRET = subprocess.run(
    ['bash', '-c', 'jq -r \'.channels.feishu.accounts.im_bot.appSecret\' ~/.openclaw/openclaw.json'],
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

token = get_tenant_token()

# 1. 读取全表
resp = api_call(token, "GET", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A1:J100")
rows = resp["data"]["valueRange"]["values"]

header = rows[0]
existing = {}  # core_name -> (row_index, full_name)
for i, row in enumerate(rows[1:], 1):
    if row and row[0] and row[0].strip():
        name = row[0].strip()
        # 规范化：去掉括号内容
        core = name.replace('（', '(').replace('）', ')')
        if '(' in core:
            core = core[:core.index('(')].strip()
        existing[core] = (i, name)

print(f"已有 {len(existing)} 条记录:")
for core, (idx, name) in existing.items():
    print(f"  Row {idx}: {name} (core={core})")

# 2. 本次商机数据（从行动建议提取）
today = "2026-05-20"
new_companies = [
    ["云深处科技（杭州）", "具身智能机器人", "科创板IPO申请获受理(5/18)，2025年营收3.37亿/净利2868万，毛利率52.8%", "高", "IPO综合金融服务、跨境结算、设备融资", "待沟通", "待沟通", "待联系", today, "电力巡检市占率85%，产品覆盖50国，朱秋国（浙大教授）实控"],
    ["宇树科技（杭州）", "具身智能机器人（四足/人形）", "年内提交科创板IPO，C轮融资估值超100亿，全球四足市占率>60%", "高", "IPO综合金融服务、项目贷款、平安薪代发", "待沟通", "待沟通", "active", today, "腾讯/阿里/中国移动领投，王兴兴（浙大）创立，拟募资42亿"],
    ["翼菲科技（浙江）", "工业机器人（轻工业全品类）", "港股上市(5/20)市值136亿港元，医疗机器人赛道CAGR 22.4%", "高", "跨境金融、供应链金融、付融通", "待沟通", "待沟通", "待联系", today, "张赛（清华+哥大+清华博士）创立，医疗积压订单3150万"],
    ["千寻智能", "具身智能（通用具身大模型）", "30天完成30亿融资，20万小时交互数据，京东/宁德时代已落地", "中", "科创贷、数字财资", "待沟通", "待沟通", "待联系", today, "聚焦具身智能大模型，数据采集成本降至1/10"],
    ["节卡机器人", "工业协作机器人", "入选2026具身智能十大龙头，3C电子/汽车制造柔性智造需求", "中", "付融通、商票保贴、订单融资", "待沟通", "待沟通", "待联系", today, "上海企业，在浙江有业务布局"],
]

# 3. 去重+匹配
updates = {}  # row_index -> new_row_data
appends = []

for company in new_companies:
    name = company[0].strip()
    core = name.replace('（', '(').replace('）', ')')
    if '(' in core:
        core = core[:core.index('(')].strip()
    
    if core in existing:
        row_idx, orig_name = existing[core]
        # 检查是否为终态
        old_row = rows[row_idx]
        status = old_row[7] if len(old_row) > 7 else ""
        if status in ('closed', '已关闭', '已落地'):
            print(f"跳过终态: {orig_name} (status={status})")
            continue
        # 更新该行，保持A列原名称不变
        new_row = [orig_name] + company[1:]
        updates[row_idx] = new_row
        print(f"更新 Row {row_idx}: {orig_name}")
    else:
        appends.append(company)
        print(f"追加: {name}")

# 4. 应用更新
for row_idx, new_row in updates.items():
    col_letter = 'A'
    end_col = 'J'
    range_str = f"{SHEET_ID}!{col_letter}{row_idx + 1}:{end_col}{row_idx + 1}"
    api_call(token, "PUT", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{range_str}", {
        "valueRange": {"values": [new_row]}
    })

# 5. 追加新行
if appends:
    start_row = len(rows) + 1
    end_row = start_row + len(appends) - 1
    range_str = f"{SHEET_ID}!A{start_row}:J{end_row}"
    api_call(token, "PUT", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{range_str}", {
        "valueRange": {"values": appends}
    })
    print(f"追加 {len(appends)} 行至 {range_str}")

# 6. 重新读取全表并按日期倒序排序
resp = api_call(token, "GET", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A1:J200")
rows = resp["data"]["valueRange"]["values"]
header = rows[0]
data_rows = [r for r in rows[1:] if len(r) > 0 and r[0] and r[0].strip()]

# 按日期列(index 8)倒序
data_rows.sort(key=lambda x: x[8] if len(x) > 8 and x[8] else '', reverse=True)

# 写入排序后的数据
end_row = 1 + len(data_rows)
api_call(token, "PUT", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A2:J{end_row}", {
    "valueRange": {"values": data_rows}
})

# 清理残留空行
api_call(token, "POST", f"/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/sheets/{SHEET_ID}/dimensionRanges/delete", {
    "ranges": [{"dimension": "ROWS", "startIndex": end_row, "endIndex": 200}]
})

print(f"\n完成！共 {len(data_rows)} 条数据，已按日期倒序排列。")
