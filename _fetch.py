# -*- coding: utf-8 -*-
"""抓取喷嚏图卦单期原文并解析为结构化条目（含正文）"""
import io, json, re, sys, urllib.request

def fetch_issue(iid):
    url = 'https://www.dapenti.com/blog/more.asp?name=xilei&id=%s' % iid
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode('gb2312', errors='replace')
    m = re.search(r'<title>([^<]+)</title>', html)
    title = m.group(1).strip() if m else ''
    title = re.sub(r'[\s\-_]+$', '', title)
    start = html.find('每天一图卦')
    end = html.find('来源：')
    if start < 0:
        start = html.find('一图卦')
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
        body_text = re.sub(r'<[^>]+>', ' ', seg)
        body_text = re.sub(r'\s+', ' ', body_text).strip()[:400]
        items.append({'n': n, 'title': plain, 'body': body_text, 'imgs': imgs})
    return {'id': iid, 'title': title, 'items': items}

if __name__ == '__main__':
    ids = sys.argv[1:]
    out = {}
    for iid in ids:
        d = fetch_issue(iid)
        out[iid] = d
        print(iid, '|', d['title'][:40], '| items:', len(d['items']))
    with io.open('/home/user/Doubao/chats/38442480054038530/pentu-daily/_raw.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('saved _raw.json')
