# -*- coding: utf-8 -*-
"""合并最近7天喷嚏图卦数据：过滤敏感 + 自动五分类 + 生成 data.json"""
import io, json, re, datetime, os

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = BASE + '_raw.json'
OUT = BASE + 'data.json'

# 敏感人物过滤名单（命中标题/正文即整条跳过，不转述）
BLOCK = ['\u738b\u4e39', '\u5218\u6653\u6ce2']

def load(p):
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)

def clean(t):
    return re.sub(r'[【】#\s]+', '', t or '').strip()

def pick_title(it):
    t = (it.get('title') or '').strip()
    author = (it.get('author') or '').strip()
    b = (it.get('body') or '').strip()
    ocr = (it.get('ocr') or '').strip()
    # 微博段子带作者：标题 = 作者 · 内容（内容不以作者开头时拼接）
    if author and t and not t.startswith(author):
        return (author + ' · ' + t)[:64]
    # 标题为纯作者名（短、无标点）→ 作者 + 正文首句
    if author and (len(t) <= 6 and not re.search(r'[\d，。！？、：:；;]', t) or t == author):
        src = b or ocr
        first = re.split(r'[\n。]', src)[0].strip() if src else ''
        first = clean(first)
        if first and first != t:
            return (t + ' · ' + first)[:64]
    if len(t) >= 6 and not t.startswith('@'):
        return t[:64]
    src = b or ocr
    if not src:
        return t[:64] or '（图片）'
    first = re.split(r'[\n。]', src)[0].strip()
    first = clean(first)
    return first[:64] or t[:64] or '（图片）'

def pick_body(it, title):
    b = (it.get('body') or '').strip()
    b = b.replace('\r\n', '\n').replace('\r', '\n')
    ocr = (it.get('ocr') or '').strip()
    img_desc = (it.get('img_desc') or '').strip()
    if not b:
        # 纯图条目：优先 OCR 文字，其次人工视觉描述，都没有才标"配图"
        src = ocr or img_desc
        if src:
            return src[:6000] or '配图'
        return '配图'
    if (it.get('title') or '').strip().startswith('@') or len((it.get('title') or '').strip()) < 6:
        parts = re.split(r'[\n。]', b, 1)
        rest = parts[1] if len(parts) > 1 else ''
        if rest.strip():
            b = rest
    # 去掉与标题第一行重复的前缀（保留原文换行/空格排版）
    head = title.split('\n')[0][:15]
    if head:
        pos = b.find(head)
        if pos >= 0:
            b = b[pos + len(head):].lstrip(' ，。')
    b = b.strip()
    if not b:
        # 去重后为空（正文即标题本身）→ 回退图片 OCR/描述
        src = ocr or img_desc
        if src:
            return src[:6000] or '配图'
        return '配图'
    return b[:6000] or '配图'

# 国际强词（政治/地缘主体，命中即国际）；弱词参与分数竞争
INTL_STRONG = ['特朗普','拜登','白宫','国会','五角大楼','普京','俄罗斯','乌克兰','泽连斯基','伊朗','以色列','中东','胡塞','也门','沙特','土耳其','叙利亚','伊拉克','北约','欧盟','朝鲜','金正恩','国事访问','华盛顿','莫斯科','基辅','俄乌','美伊','联合国']
INTL_WEAK = ['美国','日本','韩国','英国','法国','德国','意大利','西班牙','欧洲','菲律宾','越南','泰国','印度','巴基斯坦','曼谷','东京','首尔','中美','外媒','美媒','韩媒','日媒','全球','国际']

CATS = {
    'intl': INTL_STRONG + INTL_WEAK,
    'tech': ['AI','人工智能','大模型','GPT','OpenAI','谷歌','微软','苹果','Meta','英伟达','芯片','半导体','华为','小米','字节','阿里','腾讯','百度','马斯克','SpaceX','星舰','火箭','卫星','NASA','航天','融资','估值','上市','IPO','加密货币','比特币','软件','算法','机器人','智能体','智能','股市','A股','港股','美股','股价','市值','涨停','基金','券商','加息','降息','债券','收益率','AMD','收购'],
    'econ': ['GDP','经济','财政','税收','税','房价','楼市','房地产','地产','购房','房贷','贷款','消费','就业','失业','招聘','裁员','工资','养老金','社保','医保','物价','通胀','CPI','出口','进口','关税','贸易','企业','工厂','产业','制造','国资委','央企','补贴','债务','银行','保险','保费','县城','超市','电商','快递','油价','汽油','能源','农业','电力','房租','租金','收入'],
    'soc': ['教育','学校','学生','教师','教授','大学','幼儿园','医院','医生','护士','疾病','疫苗','药品','食品安全','火灾','爆炸','事故','地震','台风','暴雨','洪水','警方','公安','法院','检察院','被判','获刑','立案','调查','举报','通报','辟谣','谣言','反腐','落马','被查','拘留','判刑','婚姻','离婚','户籍','养老','育儿','健康','心理','自杀','死亡','失踪','城管','法规','条例','立法','新规','规定'],
    'cult': ['电影','电视剧','导演','演员','歌手','音乐','歌曲','小说','作家','漫画','动画','游戏','体育','足球','篮球','乒乓球','比赛','冠军','奥运','亚运','颁奖','奥斯卡','话剧','戏剧','综艺','明星','演唱会','票房','艺术','文化','历史','段子','搞笑','网红','博主','球迷'],
}

PRIORITY = ['tech', 'intl', 'econ', 'cult', 'soc']

def classify(it, title, body):
    ocr = (it.get('ocr') or '').strip()
    text = title + ' ' + (body or '')[:120] + ' ' + ocr[:100]
    low = text.lower()
    scores = {}
    for cat, kws in CATS.items():
        s = 0
        for kw in kws:
            if kw.lower() in low:
                s += 2 if kw.lower() in title.lower() else 1
        scores[cat] = s
    if any(k.lower() in low for k in INTL_STRONG):
        return 'intl'
    top = max(scores.values())
    if top == 0:
        return 'soc'
    for c in PRIORITY:
        if scores[c] == top:
            return c
    return 'soc'

raw = load(RAW)
# 从期标题自动解析日期：'【喷嚏图卦20260930】' -> 20260930
raw_by_date = {}
for iid, v in raw.items():
    m = re.search(r'(\d{8})', v.get('title') or '')
    if m:
        raw_by_date[m.group(1)] = v
    else:
        raw_by_date.setdefault(iid, v)

today = datetime.date(2026, 9, 30)
# 用数据里最新日期兜底：若解析出的日期晚于今天，以数据为准
if raw_by_date:
    mx = max(raw_by_date.keys())
    mxd = datetime.date(int(mx[:4]), int(mx[4:6]), int(mx[6:8]))
    if mxd > today:
        today = mxd
days = []
for i in range(6, -1, -1):
    d = today - datetime.timedelta(days=i)
    days.append(d.strftime('%Y%m%d'))

CAT_ORDER = ['econ', 'soc', 'intl', 'tech', 'cult']

out_days = []
dropped = []
for ds in days:
    src = raw_by_date.get(ds)
    if not src:
        continue
    cats = {c: [] for c in CAT_ORDER}
    for it in src['items']:
        full = (it.get('title') or '') + ' ' + (it.get('body') or '')
        if any(k in full for k in BLOCK):
            dropped.append((ds, it['n'], it.get('title')))
            continue
        title = pick_title(it)
        body = pick_body(it, title)
        cat = classify(it, title, body)
        cats[cat].append({
            'n': it['n'],
            't': title,
            'b': body,
            'href': 'https://www.dapenti.com/blog/more.asp?name=xilei&id=%s#:~:text=【%d】' % (src['id'], it['n'])
        })
    out_days.append({
        'date': ds,
        'label': '%s月%s日' % (int(ds[4:6]), int(ds[6:8])),
        'week': ['周一','周二','周三','周四','周五','周六','周日'][datetime.date(int(ds[:4]), int(ds[4:6]), int(ds[6:8])).weekday()],
        'id': src['id'],
        'title': re.sub(r'^\d{8}', '', src['title'].replace('铂程斋--【喷嚏图卦', '').replace('】', '')).strip(),
        'cats': cats
    })

data = {'days': out_days}
with io.open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print('days:', [(d['date'], d['id'], sum(len(v) for v in d['cats'].values())) for d in out_days])
print('dropped:', dropped)
print('total:', sum(sum(len(v) for v in d['cats'].values()) for d in out_days))
