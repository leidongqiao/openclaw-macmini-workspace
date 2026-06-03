#!/usr/bin/env python3
import json, subprocess, re, sys
from pathlib import Path
BOT='cli_a9715315cdb8dbcf'
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
        '温州市具身智能科技':'温州市具身智能科技有限公司',
        '温州市具身智能科技有限公司':'温州市具身智能科技有限公司',
        '杭州大数云智科技':'杭州大数云智科技有限公司',
        '杭州大数云智科技有限公司':'杭州大数云智科技有限公司',
    }
    return aliases.get(s,s)

new_companies=[
 ['杭州云深处科技股份有限公司','具身智能机器人','科创板IPO申请获受理，拟募资25.03亿元；重点沟通账户体系、订单回款、供应商付款和研发/产业化资金安排','高','普惠金融科创贷、科技创新和技术更新改造再贷款、订单融资、付融通、商票e贴、数字财资','待沟通','待沟通','待联系',TODAY,'朱秋国、李超浙大背景；To B电力/消防/工业巡检收入闭环明确'],
 ['宇树科技股份有限公司','具身智能机器人','杭州具身智能中试基地生态核心企业；建议从供应链、跨境和核心供应商/经销商批量获客切入','高','数字财资、供应链金融、银票极速贴现、商票e贴、跨境支付结算、外币存款、平安薪','待沟通','待沟通','待联系',TODAY,'王兴兴创立；关注供应商付款、海外收款和量产供应链资金需求'],
 ['温州市具身智能科技有限公司','具身智能/机器人平台','优必选、温州市数据集团、温州国投股权投资基金等参与设立；建议争取基本户、项目资金账户、薪酬代发和早期科技金融方案','中','数字财资、慧收款、平安薪、普惠金融科创贷、普惠金融担保贷、订单融资、平安租赁','待沟通','待沟通','待联系',TODAY,'新设公司，股东方体现头部企业+地方国资+产业基金协同；业务订单和财务数据待核实'],
 ['杭州大数云智科技有限公司','具身智能应用/机器人场景解决方案','已在杭州具身智能中试基地落地智慧餐厅机器人、监察巡视机器人等场景；建议以项目合同和回款路径切入','中','订单融资、银票极速贴现、商票e贴、慧收款、数字财资、平安租赁','待沟通','待沟通','待联系',TODAY,'场景服务商，关注设备采购、交付垫资、回款周期和项目复制能力'],
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
