#!/usr/bin/env python3
import json, subprocess, re, sys
from pathlib import Path
BOT='im_bot'
LARK='/Users/leidongqiao/.npm-global/bin/lark-cli'
SPREADSHEET_TOKEN='HheAswhqEhm6QSt17DjclAdGn8c'
SHEET_ID='a39f2b'
TODAY='2026-05-22'

def run(args, input=None):
    p=subprocess.run(args, input=input, text=True, capture_output=True)
    if p.returncode!=0:
        print('CMD FAIL', ' '.join(args), p.stderr, p.stdout)
        raise SystemExit(p.returncode)
    return p.stdout

def core(name):
    s=(name or '').strip().replace('（','(').replace('）',')')
    s=re.sub(r'\([^)]*\)','',s).strip()
    aliases={
        '宇树科技':'宇树科技股份有限公司',
        '宇树科技股份有限公司':'宇树科技股份有限公司',
        '杭州宇树科技':'宇树科技股份有限公司',
        '云深处科技':'杭州云深处科技股份有限公司',
        '云深处科技股份有限公司':'杭州云深处科技股份有限公司',
        '杭州云深处科技有限公司':'杭州云深处科技股份有限公司',
        '杭州云深处科技股份有限公司':'杭州云深处科技股份有限公司',
        '宁波中亿智能':'宁波中亿智能股份有限公司',
        '宁波中亿智能股份有限公司':'宁波中亿智能股份有限公司',
        '浙江柔荷新能源材料有限公司':'浙江柔荷新能源材料有限公司',
        '柔荷新能源材料':'浙江柔荷新能源材料有限公司',
        '宁波瑞凌新能源科技有限公司':'宁波瑞凌新能源科技有限公司',
        '瑞凌新能源':'宁波瑞凌新能源科技有限公司',
        '宁波昂霖智能装备有限公司':'宁波昂霖智能装备有限公司',
        '昂霖智能':'宁波昂霖智能装备有限公司',
    }
    return aliases.get(s,s)

new_companies=[
 ['宇树科技股份有限公司','具身智能机器人','宁波产业园总投资12.42亿元，杭州研发+宁波量产；2025年营收17.08亿元/净利2.88亿元','高','付融通、商票e贴、资产池、平安租赁、跨境支付结算','待沟通','待沟通','待联系',TODAY,'关注量产供应商付款、设备投入、跨境订单；王兴兴创立，核心团队细节待核实'],
 ['杭州云深处科技股份有限公司','具身智能机器人','5月18日科创板IPO获受理，拟募资25.03亿元；2025年营收3.37亿元/净利2868.4万元','高','数字财资、资产池、订单融资、商票贴现、平安薪','待沟通','待沟通','待联系',TODAY,'朱秋国、李超（浙大背景）创立；To B电力/消防/工业巡检收入闭环明确'],
 ['宁波中亿智能股份有限公司','机器视觉/AI智能质检','新华网宁波“五小虎”；高端轴承检测装备首台套，300多家客户云端数据库','高','订单融资、国内信用证、银票极速贴现、普惠金融科创贷','待沟通','待沟通','待联系',TODAY,'董事长刘建军；项目交付和验收回款资金占用需核实'],
 ['浙江柔荷新能源材料有限公司','新能源材料/电池热防护','宁波“五小虎”；2024年成立，4条陶瓷纳米纤维气凝胶智能化产线，进入电池热防护场景','中高','普惠金融科创贷、科技创新和技术更新改造再贷款、平安租赁、银票贴现','待沟通','待沟通','待联系',TODAY,'董事长闫建华；客户认证、订单合同和现金流需核实'],
 ['宁波瑞凌新能源科技有限公司','辐射制冷材料/超材料','与宇树机器人硬件平台结构组推进防爆特种机器人散热材料应用测试','中高','订单融资、普惠金融科创贷、银票贴现、平安租赁、慧收款','待沟通','待沟通','待联系',TODAY,'副总裁刘丰维；关注测试转订单和宇树供应链切入'],
 ['宁波昂霖智能装备有限公司','智慧交通/AGV移动机器人','智能交通锥“自行锥”在杭州千岛湖大桥潮汐车道项目使用，切入交通应急安全场景','中','订单融资、境内保函、银票极速贴现、慧收款','待沟通','待沟通','待联系',TODAY,'总经理于显超；关注项目合同、验收节点和业主回款路径'],
]

# read table
out=run([LARK,'sheets','+read','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--range',f'{SHEET_ID}!A1:J200','--jq','.data.valueRange.values'])
rows=json.loads(out)
if not rows: rows=[['客户名称','行业/领域','触发信号','优先级','推荐方案','预计金额','联系人','状态','创建日期','备注']]
header=rows[0]
existing={}
for i,row in enumerate(rows[1:], start=2):
    if row and len(row)>0 and (row[0] is not None and str(row[0]).strip()):
        existing[core(row[0])]=(i,row[0],row)

# merge new by core
merged={}
for c in new_companies:
    merged[core(c[0])]=c

updates=[]; appends=[]
for k,c in merged.items():
    if k in existing:
        rownum, orig, old=existing[k]
        status=old[7] if len(old)>7 else ''
        if status in ('closed','已关闭','已落地'):
            print('skip terminal', orig, status); continue
        new=[orig]+c[1:7]+[status]+[TODAY]+[c[9]]
        updates.append((rownum,new))
    else:
        appends.append(c)

for rownum,new in updates:
    run([LARK,'sheets','+write','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--range',f'{SHEET_ID}!A{rownum}:J{rownum}','--values',json.dumps([new],ensure_ascii=False)])
    print('updated', rownum, new[0])

if appends:
    start=len([r for r in rows if r and len(r)>0 and (r[0] is not None and str(r[0]).strip())])+1
    end=start+len(appends)-1
    run([LARK,'sheets','+write','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--range',f'{SHEET_ID}!A{start}:J{end}','--values',json.dumps(appends,ensure_ascii=False)])
    print('appended', len(appends))

# sort and clean
out=run([LARK,'sheets','+read','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--range',f'{SHEET_ID}!A1:J200','--jq','.data.valueRange.values'])
rows=json.loads(out)
header=rows[0]
data=[r for r in rows[1:] if r and len(r)>0 and (r[0] is not None and str(r[0]).strip())]
data.sort(key=lambda r: str(r[8] if len(r)>8 and r[8] is not None else ''), reverse=True)
end_row=1+len(data)
if data:
    run([LARK,'sheets','+write','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--range',f'{SHEET_ID}!A2:J{end_row}','--values',json.dumps(data,ensure_ascii=False)])
info=json.loads(run([LARK,'sheets','+info','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--jq','.data.sheets.sheets[0].grid_properties.row_count']))
try: max_rows=int(info)
except Exception: max_rows=200
if max_rows>end_row:
    run([LARK,'sheets','+delete-dimension','--profile',BOT,'--as','bot','--spreadsheet-token',SPREADSHEET_TOKEN,'--sheet-id',SHEET_ID,'--dimension','ROWS','--start-index',str(end_row+1),'--end-index',str(max_rows)])
print('done rows', len(data), 'end_row', end_row)
