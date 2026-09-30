# -*- coding: utf-8 -*-
"""每日自动更新入口（GitHub Actions 调用）：
1) 抓列表页取最新 id；2) 已收录则无更新退出；3) 抓新期并入 _raw.json；
4) 重建 data.json 与 index.html（保留最近 7 天）。
"""
import io, json, os, re, subprocess, sys, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = BASE + '_raw.json'
LIST_URL = 'https://www.dapenti.com/blog/blog.asp?subjectid=70&name=xilei'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

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
        texts = re.findall(r'<p[^>]*>(.*?)</p>', seg, re.S)
        plain = ''
        for t in texts:
            t2 = re.sub(r'<[^>]+>', '', t).strip()
            if t2:
                plain = t2
                break
        if not plain:
            all_text = re.sub(r'<[^>]+>', ' ', seg)
            lines = [ln.strip() for ln in re.split(r'[\n\r]', all_text) if ln.strip()]
            plain = lines[0] if lines else ''
        imgs = re.findall(r'<img[^>]+src="([^"]+)"', seg)
        body_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', seg)).strip()[:400]
        items.append({'n': n, 'title': plain, 'body': body_text, 'imgs': imgs})
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
    subprocess.check_call([sys.executable, os.path.join(BASE, '_build.py')])
    subprocess.check_call([sys.executable, os.path.join(BASE, '_render.py')])
    print('updated OK')

if __name__ == '__main__':
    main()
