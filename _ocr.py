# -*- coding: utf-8 -*-
"""对带图条目做 OCR：下载 imgs[0] → tesseract(chi_sim+eng) → 文本写入 item['ocr']"""
import io, json, os, re, subprocess, sys, tempfile, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = BASE + '_raw.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)

def ocr(path):
    try:
        out = subprocess.run(['tesseract', path, 'stdout', '-l', 'chi_sim+eng'],
                             capture_output=True, timeout=90)
        text = out.stdout.decode('utf-8', errors='replace')
    except Exception as e:
        return ''
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return '\n'.join(lines)

def main():
    with io.open(RAW, encoding='utf-8') as f:
        raw = json.load(f)
    done = 0
    with tempfile.TemporaryDirectory() as tmp:
        for iid, v in raw.items():
            for it in v['items']:
                if it.get('ocr'):
                    continue
                imgs = it.get('imgs') or []
                if not imgs:
                    continue
                url = imgs[0]
                if not url.startswith('http'):
                    url = 'https://www.dapenti.com:99/' + url.lstrip('/')
                try:
                    path = os.path.join(tmp, 'img_%s_%d.jpg' % (iid, it['n']))
                    download(url, path)
                    txt = ocr(path)
                except Exception as e:
                    print('  fail', iid, it['n'], str(e)[:80])
                    continue
                it['ocr'] = txt[:600] if txt.strip() else ''
                done += 1
                print('ocr', iid, 'n=', it['n'], '| chars:', len(it['ocr']))
    with io.open(RAW, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False)
    print('OCR done:', done)

if __name__ == '__main__':
    main()
