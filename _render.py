# -*- coding: utf-8 -*-
"""渲染日报页面：读 data.json → 生成单文件 index.html（内联数据 + 日期切换）"""
import io, json, os

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
DATA = BASE + 'data.json'
OUT = BASE + 'index.html'

with io.open(DATA, encoding='utf-8') as f:
    data = json.load(f)

days = data['days']
latest = days[-1]

json_str = json.dumps(data, ensure_ascii=False)
json_str = json_str.replace('<', '\\u003c')

day_buttons = '\n'.join(
    '<button class="day-btn%s" data-date="%s" onclick="showDay(\'%s\')"><b>%s</b><span>%s</span></button>'
    % (' active' if d['date'] == latest['date'] else '', d['date'], d['date'], d['label'], d['week'])
    for d in days
)

TEMPLATE = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>喷嚏图卦 · 每日图卦 2026.09.24–09.30</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='10' fill='%2320242B'/%3E%3Crect x='12' y='12' width='16' height='16' rx='3' fill='%232662B8'/%3E%3Crect x='36' y='12' width='16' height='16' rx='3' fill='%2312805E'/%3E%3Crect x='12' y='36' width='16' height='16' rx='3' fill='%23C0443B'/%3E%3Crect x='36' y='36' width='16' height='16' rx='3' fill='%236A48B0'/%3E%3Crect x='24' y='24' width='16' height='16' rx='3' fill='%23B07A1E'/%3E%3C/svg%3E">
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@600;700;900&family=Noto+Sans+SC:wght@400;500;700&display=swap">
<style>
  :root{
    --paper:#F5F4EF; --card:#FFFFFF; --ink:#20242B; --ink-2:#5A5F68; --line:#E2E0D8;
    --blue:#2662B8; --green:#12805E; --red:#C0443B; --purple:#6A48B0; --amber:#B07A1E;
    --blue-soft:rgba(38,98,184,.06); --green-soft:rgba(18,128,94,.06);
    --red-soft:rgba(192,68,59,.06); --purple-soft:rgba(106,72,176,.06); --amber-soft:rgba(176,122,30,.06);
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{background:var(--paper);color:var(--ink);font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;line-height:1.75;-webkit-font-smoothing:antialiased}
  .wrap{max-width:800px;margin:0 auto;padding:0 20px}
  a{color:inherit}
  ::selection{background:rgba(176,122,30,.25)}

  /* 报头 */
  .masthead{background:var(--ink);color:#F5F4EF}
  .masthead-inner{max-width:840px;margin:0 auto;padding:34px 20px 30px}
  .brand-row{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
  .brand{font-family:"Noto Serif SC",serif;font-weight:900;font-size:26px;letter-spacing:.12em}
  .brand .dot{color:var(--amber)}
  .slogan{font-size:13px;color:#A9AEBB;letter-spacing:.08em}
  .issue-date{font-size:13px;color:#8C93A3;letter-spacing:.2em;margin-top:6px}
  .issue-title{font-family:"Noto Serif SC",serif;font-weight:900;font-size:clamp(24px,4.6vw,36px);line-height:1.4;margin:16px 0 4px;color:#fff}
  .issue-sub{font-size:13px;color:#8C93A3}

  /* 日期切换 */
  .daybar{background:#1B1E24;border-top:1px solid rgba(255,255,255,.1)}
  .daybar-inner{max-width:840px;margin:0 auto;padding:12px 20px;display:grid;grid-template-columns:repeat(7,1fr);gap:8px}
  .day-btn{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#A9AEBB;border-radius:8px;padding:8px 6px 6px;cursor:pointer;font-family:inherit;transition:all .15s}
  .day-btn b{display:block;font-size:13px;font-weight:600;color:#E7E9EE}
  .day-btn span{font-size:11px;color:#8C93A3}
  .day-btn:hover{background:rgba(255,255,255,.14)}
  .day-btn.active{background:var(--amber);border-color:var(--amber);color:#20242B}
  .day-btn.active b{color:#20242B}
  .day-btn.active span{color:#20242B}

  /* 导航 */
  .section-nav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
  .nav-inner{max-width:840px;margin:0 auto;padding:10px 20px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}
  .nav-inner::-webkit-scrollbar{display:none}
  .nav-inner a{display:inline-flex;align-items:center;gap:7px;white-space:nowrap;text-decoration:none;font-size:14px;font-weight:500;color:var(--ink-2);padding:5px 12px;border-radius:999px;transition:all .15s}
  .nav-inner a:hover{background:var(--line);color:var(--ink)}
  .nav-inner a i{width:8px;height:8px;border-radius:50%;background:var(--nc)}
  .to-top{margin-left:auto;color:var(--ink-2);font-size:13px;text-decoration:none;padding:5px 10px;border:1px solid var(--line);border-radius:999px;flex-shrink:0}
  .to-top:hover{background:var(--ink);color:#fff;border-color:var(--ink)}

  /* 主题板块 */
  main{padding:36px 0 20px}
  section.panel{margin-bottom:56px;scroll-margin-top:64px}
  .panel-head{display:flex;align-items:center;gap:16px;margin-bottom:4px}
  .panel-mark{width:46px;height:46px;border-radius:10px;background:var(--sec);color:#fff;font-family:"Noto Serif SC",serif;font-weight:700;font-size:17px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .panel-title{font-family:"Noto Serif SC",serif;font-weight:700;font-size:clamp(20px,3.2vw,24px);color:var(--sec)}
  .panel-title span{font-size:13px;color:var(--ink-2);font-family:"Noto Sans SC",sans-serif;font-weight:400;display:block;margin-top:2px}
  .panel-line{height:2px;background:var(--sec);opacity:.25;margin:14px 0 20px}

  /* 条目 */
  .items{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start}
  .item{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--sec);border-radius:0 8px 8px 0;padding:12px 15px;transition:background .18s;break-inside:avoid;cursor:pointer;position:relative}
  .item:hover{background:var(--sec-soft)}
  .item-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
  .item-head .src{flex-shrink:0}
  .item .src{font-size:11.5px;font-weight:500;letter-spacing:.05em;opacity:.95}
  .item h3{font-family:"Noto Serif SC",serif;font-weight:700;font-size:14.5px;line-height:1.45;margin:2px 0 4px}
  .item p.clamp{display:-webkit-box;-webkit-line-clamp:6;-webkit-box-orient:vertical;overflow:hidden;font-size:12.8px;color:#4A4F58;line-height:1.6}
  .item p.full{font-size:12.8px;color:#4A4F58;line-height:1.6}
  .item.has-more::after{content:"… 点击查看全文";position:absolute;right:10px;bottom:6px;font-size:11px;color:var(--sec);background:linear-gradient(90deg,transparent,var(--card) 30%);padding:2px 6px 2px 14px;pointer-events:none}
  .item.has-more p.clamp{position:relative}
  .src-link{font-size:11px;color:var(--ink-2);text-decoration:none;white-space:nowrap;border-bottom:1px dashed var(--line);transition:color .15s,border-color .15s;position:relative;z-index:2}
  .src-link:hover{color:var(--sec);border-color:var(--sec)}
  .item.full{grid-column:1/-1}
  .src-mon{color:var(--blue)} .src-tue{color:var(--green)} .src-wed{color:var(--purple)} .src-thu{color:var(--red)}
  .src-fri{color:var(--amber)} .src-sat{color:#3E7D8C} .src-sun{color:#2F6B7A}

  /* 全文弹层 */
  .modal-mask{position:fixed;inset:0;background:rgba(20,22,28,.62);z-index:200;display:flex;align-items:center;justify-content:center;padding:20px;opacity:0;visibility:hidden;transition:opacity .18s}
  .modal-mask.open{opacity:1;visibility:visible}
  .modal{background:var(--paper);max-width:640px;width:100%;max-height:82vh;border-radius:14px;box-shadow:0 24px 60px rgba(0,0,0,.35);display:flex;flex-direction:column;transform:translateY(10px);transition:transform .18s}
  .modal-mask.open .modal{transform:translateY(0)}
  .modal-head{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 20px 12px;border-bottom:1px solid var(--line)}
  .modal-tag{font-size:12px;color:var(--sec);font-weight:600;letter-spacing:.06em}
  .modal-close{background:none;border:none;font-size:22px;line-height:1;color:var(--ink-2);cursor:pointer;padding:4px 8px;border-radius:6px}
  .modal-close:hover{color:var(--ink);background:var(--line)}
  .modal-body{overflow-y:auto;padding:18px 20px 22px}
  .modal h3{font-family:"Noto Serif SC",serif;font-weight:700;font-size:18px;line-height:1.5;margin-bottom:12px}
  .modal p{font-size:14.5px;line-height:1.9;color:#33363D;white-space:pre-wrap;word-break:break-word}
  .modal-src{margin-top:16px;font-size:12.5px}
  .modal-src a{color:var(--sec);text-decoration:none;border-bottom:1px dashed var(--line)}

  /* 页脚 */
  footer{background:var(--ink);color:#A9AEBB;margin-top:20px}
  .footer-inner{max-width:840px;margin:0 auto;padding:30px 20px;font-size:13px;line-height:1.9}
  .footer-inner a{color:#F5F4EF;text-decoration:none}
  .footer-inner a:hover{color:var(--amber)}
  .footer-inner .src{color:#8C93A3}
  .footer-links{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px 18px;margin:10px 0 14px}
  .footer-links div{display:flex;align-items:baseline;gap:8px;min-width:0}
  .footer-links .src{flex-shrink:0}
  .footer-links a{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.item,.nav-inner a,.day-btn{transition:none}}
  @media (max-width:720px){
    .daybar-inner{grid-template-columns:repeat(4,1fr)}
    .items{grid-template-columns:1fr}
    .footer-links{grid-template-columns:repeat(2,minmax(0,1fr))}
  }
</style>
</head>
<body>

<script id="daily-data" type="application/json">__DATA__</script>

<header class="masthead">
  <div class="masthead-inner">
    <div class="brand-row">
      <div class="brand">喷嚏图卦</div>
      <div class="slogan">每天一图卦，让我们更清楚地了解这个世界</div>
    </div>
    <div class="issue-date" id="hd-date"></div>
    <h1 class="issue-title" id="hd-title"></h1>
    <div class="issue-sub" id="hd-sub"></div>
  </div>
</header>

<div class="daybar">
  <div class="daybar-inner">
__DAY_BUTTONS__
  </div>
</div>

<nav class="section-nav" aria-label="主题导航">
  <div class="nav-inner" id="nav-inner"></div>
</nav>

<main class="wrap" id="top">
  <div id="panels"></div>
</main>

<div class="modal-mask" id="modal-mask" role="dialog" aria-modal="true" aria-label="条目全文">
  <div class="modal">
    <div class="modal-head">
      <div class="modal-tag" id="modal-tag"></div>
      <button class="modal-close" id="modal-close" aria-label="关闭">×</button>
    </div>
    <div class="modal-body">
      <h3 id="modal-title"></h3>
      <p id="modal-body-text"></p>
      <div class="modal-src" id="modal-src"></div>
    </div>
  </div>
</div>

<footer>
  <div class="footer-inner">
    <p>本页内容整理自喷嚏网·喷嚏图卦栏目原文（标题与摘要为转述，原文为准），点击条目"来源"可打开当日原文并定位到该条。数据保留最近 7 天，每日 18:00 自动更新。</p>
    <div class="footer-links" id="footer-links"></div>
    <p style="margin-top:10px;color:#8C93A3" id="footer-note"></p>
  </div>
</footer>

<script>
var DATA = JSON.parse(document.getElementById('daily-data').textContent);
var DAYS = DATA.days;
var CATS = [
  {id:'econ', mark:'一', name:'经济与民生', sub:'消费 · 就业 · 楼市 · 社保 · 产业', nc:'var(--blue)', soft:'var(--blue-soft)'},
  {id:'soc', mark:'二', name:'社会与健康', sub:'法治 · 教育 · 医疗 · 食品安全', nc:'var(--green)', soft:'var(--green-soft)'},
  {id:'intl', mark:'三', name:'国际', sub:'中美 · 中东 · 俄乌 · 欧洲 · 亚洲', nc:'var(--red)', soft:'var(--red-soft)'},
  {id:'tech', mark:'四', name:'科技与财经', sub:'AI · 大模型 · 航天 · 芯片 · 股市', nc:'var(--purple)', soft:'var(--purple-soft)'},
  {id:'cult', mark:'五', name:'文化娱乐', sub:'影视 · 音乐 · 体育 · 人物 · 段子', nc:'var(--amber)', soft:'var(--amber-soft)'}
];
var WD = {0:'周日',1:'周一',2:'周二',3:'周三',4:'周四',5:'周五',6:'周六'};
var cur = DAYS[DAYS.length - 1].date;

function dayOf(dateStr){
  var y = +dateStr.slice(0,4), m = +dateStr.slice(4,6), d = +dateStr.slice(6,8);
  return WD[new Date(y, m-1, d).getDay()];
}

function esc(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderDay(dateStr){
  cur = dateStr;
  var day = null;
  for (var i=0;i<DAYS.length;i++){ if (DAYS[i].date === dateStr){ day = DAYS[i]; break; } }
  if (!day) return;
  document.getElementById('hd-date').textContent = '每日图卦 · ' + day.label + '（' + day.week + '）';
  document.getElementById('hd-title').textContent = day.title || '喷嚏图卦';
  var total = 0;
  CATS.forEach(function(c){ total += day.cats[c.id].length; });
  document.getElementById('hd-sub').textContent = day.label + ' · ' + total + ' 条 · 五类标签：经济与民生 / 社会与健康 / 国际 / 科技与财经 / 文化娱乐';
  var nav = '';
  CATS.forEach(function(c){
    nav += '<a href="#' + c.id + '" style="--nc:' + c.nc + '"><i></i>' + c.name + '</a>';
  });
  nav += '<a href="#top" class="to-top">回到顶部 ↑</a>';
  document.getElementById('nav-inner').innerHTML = nav;
  var panels = '';
  CATS.forEach(function(c, ci){
    var items = day.cats[c.id];
    panels += '<section class="panel" id="' + c.id + '" style="--sec:' + c.nc + ';--sec-soft:' + c.soft + '">'
      + '<div class="panel-head"><div class="panel-mark">' + c.mark + '</div>'
      + '<div class="panel-title">' + c.name + '<span>' + c.sub + ' · ' + items.length + ' 条</span></div></div>'
      + '<div class="panel-line"></div><div class="items">';
    items.forEach(function(it, i2){
      var wd = dayOf(dateStr);
      var full = items.length === 1 ? ' full' : '';
      var pcl = it.b.length > 90 ? 'clamp' : 'full';
      panels += '<article class="item' + full + '" data-ci="' + ci + '" data-i="' + i2 + '" title="点击查看全文"><div><div class="item-head">'
        + '<div class="src src-' + ['sun','mon','tue','wed','thu','fri','sat'][new Date(+dateStr.slice(0,4), +dateStr.slice(4,6)-1, +dateStr.slice(6,8)).getDay()] + '">' + wd + ' · ' + (it.n < 10 ? '0' : '') + it.n + '</div>'
        + '<a class="src-link" href="' + it.href + '" target="_blank" rel="noopener">来源</a></div>'
        + '<h3>' + esc(it.t) + '</h3><p class="' + pcl + '">' + esc(it.b.replace(/\\s+/g,' ')) + '</p></div></article>';
    });
    panels += '</div></section>';
  });
  document.getElementById('panels').innerHTML = panels;
  // 检测正文是否超出 6 行 → 标记"点击查看全文"
  var itemsEls = document.querySelectorAll('.item p.clamp');
  for (var i=0;i<itemsEls.length;i++){
    var p = itemsEls[i];
    if (p.scrollHeight > p.clientHeight + 2){
      var art = p.closest('.item');
      art.classList.add('has-more');
    } else {
      p.className = 'full';
    }
  }
  bindModal();
  var btns = document.querySelectorAll('.day-btn');
  for (var i=0;i<btns.length;i++){
    btns[i].className = btns[i].getAttribute('data-date') === dateStr ? 'day-btn active' : 'day-btn';
  }
  var links = '';
  DAYS.forEach(function(d){
    links += '<div><span class="src">' + d.label + '</span><a href="https://www.dapenti.com/blog/more.asp?name=xilei&id=' + d.id + '" target="_blank" rel="noopener" title="' + esc(d.title) + '">' + esc(d.title) + '</a></div>';
  });
  document.getElementById('footer-links').innerHTML = links;
  document.getElementById('footer-note').textContent = '喷嚏图卦 · ' + DAYS[0].label + ' – ' + DAYS[DAYS.length-1].label + ' 日报 · ' + DAYS.length + ' 期 · 五主题分类 · 每日 18:00 自动更新';
  history.replaceState(null, '', '#' + dateStr);
}

function showDay(dateStr){ renderDay(dateStr); document.getElementById('top').scrollIntoView({behavior:'smooth'}); }

var curCat = '', curItem = null;
function bindModal(){
  var arts = document.querySelectorAll('.item');
  for (var i=0;i<arts.length;i++){
    arts[i].onclick = function(e){
      if (e.target.closest('.src-link')){ return; }
      var ci = +this.getAttribute('data-ci'), ii = +this.getAttribute('data-i');
      var it = DAYS.filter(function(d){ return d.date === cur; })[0].cats[CATS[ci].id][ii];
      openModal(CATS[ci], it, cur);
    };
  }
}
function openModal(cat, it, dateStr){
  var day = DAYS.filter(function(d){ return d.date === dateStr; })[0];
  document.getElementById('modal-tag').textContent = day.label + '（' + day.week + '） · ' + cat.name + ' · 序号 ' + it.n;
  document.getElementById('modal-title').textContent = it.t;
  document.getElementById('modal-body-text').textContent = it.b;
  document.getElementById('modal-src').innerHTML = '原文：<a href="' + it.href + '" target="_blank" rel="noopener">打开喷嚏网原文</a>';
  document.getElementById('modal-mask').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(){
  document.getElementById('modal-mask').classList.remove('open');
  document.body.style.overflow = '';
}
document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('modal-mask').addEventListener('click', function(e){
  if (e.target === this){ closeModal(); }
});
document.addEventListener('keydown', function(e){ if (e.key === 'Escape'){ closeModal(); } });

window.addEventListener('hashchange', function(){
  var h = location.hash.slice(1);
  if (h && h.length === 8 && DAYS.some(function(d){ return d.date === h; })){ renderDay(h); }
});

renderDay(cur);
</script>

</body>
</html>
'''

html = TEMPLATE.replace('__DATA__', json_str).replace('__DAY_BUTTONS__', day_buttons)

with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
    f.write(html)
print('rendered:', OUT, len(html))
