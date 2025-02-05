
function clone(object) { return JSON.parse(JSON.stringify(object)); }

async function sfetch(url, mode, data = null) {
  headers = { 'Accept': 'application/json, text/plain, */*', 'Content-Type': 'application/json' }
  req = { method: mode, headers: headers }
  if (mode.toUpperCase() == 'POST') req['body'] = JSON.stringify(data);
  return await fetch(url, req);
}

async function post(url, data) { return await sfetch(url, 'POST', data); }
async function get(url) { return await sfetch(url, 'GET'); }
async function del(url) { return await sfetch(url, 'DELETE'); }
