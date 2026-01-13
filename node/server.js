const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

// 获取 sites 目录下的所有 json 文件名（不带扩展名）
function getSiteList() {
  const sitesDir = path.join(__dirname, '../sites');
  if (!fs.existsSync(sitesDir)) return [];
  return fs.readdirSync(sitesDir)
    .filter(f => f.endsWith('.json'))
    .map(f => f.replace(/\.json$/, ''));
}

// 获取当前默认站点（只有一个时自动选中）
function getDefaultSite() {
  const sites = getSiteList();
  if (sites.length === 1) return sites[0];
  return null;
}

// 允许跨域
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

// 获取当前默认站点名
app.get('/api/site', (req, res) => {
  const site = getDefaultSite();
  if (site) {
    res.json({ site });
  } else {
    res.status(404).json({ error: '未找到唯一站点' });
  }
});

// 获取分类列表
app.get('/api/types', (req, res) => {
  const site = req.query.site;
  if (!site) return res.status(400).json({ error: 'site参数缺失' });
  const filePath = path.join(__dirname, '../sites', site + '.json');
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: '站点不存在' });

  const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  const types = (data.class || []).sort((a, b) => a.type_id - b.type_id);
  res.json(types);
});

// 获取视频列表
app.get('/api/list', (req, res) => {
  const site = req.query.site;
  const type_id = parseInt(req.query.type_id || '0');
  if (!site) return res.status(400).json({ error: 'site参数缺失' });
  const filePath = path.join(__dirname, '../sites', site + '.json');
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: '站点不存在' });

  const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  let list = data.list || [];
  if (type_id !== 0) {
    list = list.filter(item => item.type_id === type_id);
  }
  res.json(list);
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});