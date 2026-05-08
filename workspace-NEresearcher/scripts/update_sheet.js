const https = require('https');
const { execSync } = require('child_process');

const APP_SECRET = execSync("jq -r '.channels.feishu.accounts.ne_bot.appSecret' ~/.openclaw/openclaw.json", {encoding:'utf8'}).trim();
let TOKEN;

function apiCall(method, path, body) {
  return new Promise((resolve, reject) => {
    const url = 'https://open.feishu.cn' + path;
    const data = body ? JSON.stringify(body) : null;
    const req = https.request(url, {method, headers:{Authorization: 'Bearer '+TOKEN, 'Content-Type':'application/json'}}, res => {
      let b = '';
      res.on('data', d => b += d);
      res.on('end', () => {
        try { resolve(JSON.parse(b)); } catch(e) { reject(new Error(b)); }
      });
    });
    req.on('error', reject);
    if(data) req.write(data);
    req.end();
  });
}

// Get token
function getToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({app_id: 'cli_a97152fac6b81bd4', app_secret: APP_SECRET});
    const req = https.request('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {method:'POST', headers:{'Content-Type':'application/json'}}, res => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => {
        const parsed = JSON.parse(body);
        resolve(parsed.tenant_access_token);
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

const SPREADSHEET_TOKEN = 'C5ZgwhqJciryiTkGLH0cvlXzn5b';
const SHEET_ID = 'f2ad53';

(async () => {
  TOKEN = await getToken();
  console.log('Token OK');

  // Update rows 1-3 (existing companies)
  const updatedRows = [
    ['零跑汽车（杭州/金华）', '新能源汽车', '4月交付7.1万辆创新高，产能扩至100万辆/年，出口爆发', 'P0', '募集资金监管+项目融资+订单融资+汇率锁汇', '30亿+', '--', '待联系', '2026-05-08', '出口意大利市占33.5%，全年目标105万辆'],
    ['德业股份（宁波）', '储能逆变器/户储', '储能业务高增长，德国/澳洲政策推动需求', 'P0', '固贷追加+流贷+订单融资+汇率锁汇', '15亿+', '--', '待联系', '2026-05-08', '2025营收122亿净利31.7亿，储能逆变器头部'],
    ['惠柏新材（宁波）', '风电叶片材料', '净利暴增808%，匈牙利基地投产，珠海新产能9月投产', 'P1', '海外项目融资+订单融资', '5亿+', '--', '待联系', '2026-05-08', '风电环氧树脂龙头，出海建厂']
  ];

  const putResp = await apiCall('PUT', `/open-apis/sheets/v2/spreadsheets/${SPREADSHEET_TOKEN}/values/${SHEET_ID}!A2:J4`, {
    valueRange: { values: updatedRows }
  });
  console.log('PUT result:', JSON.stringify(putResp));
})();
