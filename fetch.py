# -*- coding: utf-8 -*-
"""每日自动更新入口（GitHub Actions 调用）：
1) 抓列表页取最新 id；2) 已收录则无更新退出；3) 抓新期并入 _raw.json；
4) 重建 data.json 与 index.html（保留最近 7 天）。
"""
import html as _html, io, json, os, re, subprocess, sys, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = BASE + '_raw.json'
LIST_URL = 'https://www.dapenti.com/blog/blog.asp?subjectid=70&name=xilei'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def dec(t):
    return _html.unescape(t or '')

def parse_seg(seg):
    """按 <p> 序列解析一段条目；微博作者段（个人主页链接）开启新组，拆成多条。
    话题标签（weibo?q=）不是作者，不拆分。"""
    seg2 = re.sub(r'<br\s*/?>', ' ', seg)
    ps = re.findall(r'<p[^>]*>(.*?)</p>', seg2, re.S)
    groups = []
    cur = None
    for t in ps:
        inner = re.sub(r'<[^>]+>', '', t).strip()
        a = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)
        href = a.group(1) if a else ''
        atext = dec(re.sub(r'<[^>]+>', '', a.group(2))).strip() if a else ''
        is_author = a and atext and len(atext) <= 6 and not re.search(r'[\d，。！？、：:；;#]', atext) \
            and ('weibo.com/u/' in href or 'm.weibo.cn/u/' in href)
        if is_author:
            cur = {'author': atext, 'texts': [], 'imgs': []}
            groups.append(cur)
            continue
        if cur is None:
            cur = {'author': '', 'texts': [], 'imgs': []}
            groups.append(cur)
        inner = dec(inner)
        if inner:
            cur['texts'].append(inner)
        cur['imgs'] += re.findall(r'<img[^>]+src="([^"]+)"', t)
    return groups

def fetch_issue(iid):
    html = get('https://www.dapenti.com/blog/more.asp?name=xilei&id=%s' % iid).decode('gb2312', errors='replace')
    m = re.search(r'<title>([^<]+)</title>', html)
    title = (m.group(1).strip() if m else '').rstrip(' -_')
    start = html.find('每天一图卦')
    if start < 0:
        start = html.find('一图卦')
    end = html.find('来源：')
    if start < 0 or end < 0 or end <= start:
        return {'id': iid, 'title': title, 'items': [], 'raw_len': len(html)}
    body = html[start:end]
    parts = re.split(r'【(\d+)】', body)
    items = []
    for k in range(1, len(parts) - 1, 2):
        n = int(parts[k])
        seg = parts[k + 1]
        for g in parse_seg(seg):
            plain = g['author'] or ''
            for t in g['texts']:
                if t.strip():
                    plain = t.strip()
                    break
            if not plain:
                all_text = re.sub(r'<[^>]+>', ' ', seg)
                lines = [ln.strip() for ln in re.split(r'[\n\r]', all_text) if ln.strip()]
                plain = dec(lines[0]) if lines else ''
            body_text = ' '.join(g['texts'])
            body_text = re.sub(r'\s+', ' ', body_text).strip()[:400]
            items.append({'n': n, 'title': dec(plain), 'body': body_text, 'imgs': g['imgs'], 'author': g['author']})
    return {'id': iid, 'title': title, 'items': items}

def main():
    html = get(LIST_URL).decode('gb2312', errors='replace')
    ids = []
    for i in re.findall(r'more\.asp\?name=xilei&id=(\d+)', html):
        if i not in ids:
            ids.append(i)
    if not ids:
        print('no id found'); sys.exit(1)
    latest_id = ids[0]
    raw = {}
    if os.path.exists(RAW):
        with io.open(RAW, encoding='utf-8') as f:
            raw = json.load(f)
    if latest_id in raw:
        print('already have', latest_id, '- no update')
        return
    issue = fetch_issue(latest_id)
    raw[latest_id] = issue
    with io.open(RAW, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False)
    print('fetched new issue', latest_id, issue['title'][:50], 'items:', len(issue['items']))
    # 纯图条目 OCR（Actions 环境已装 tesseract；本地缺 tesseract 时自动跳过）
    try:
        subprocess.check_call([sys.executable, os.path.join(BASE, '_ocr.py')])
    except Exception as e:
        print('ocr skipped:', e)
    subprocess.check_call([sys.executable, os.path.join(BASE, '_build.py')])
    subprocess.check_call([sys.executable, os.path.join(BASE, '_render.py')])
    print('updated OK')

if __name__ == '__main__':
    main()
