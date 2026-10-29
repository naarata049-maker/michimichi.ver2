# 日本郵便の郵便番号データ（読みがな付き）から、市区町村コード×町名→ひらがな の表を県ごとに作る
import csv, io, json, os, re, unicodedata, urllib.request, zipfile
URLS = ['https://www.post.japanpost.jp/zipcode/dl/utf/zip/utf_ken_all.zip',
        'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip',
        'https://www.post.japanpost.jp/service/search/zipcode/dl/utf/zip/utf_ken_all.zip',
        'https://www.post.japanpost.jp/service/search/zipcode/dl/kogaki/zip/ken_all.zip']
def fetch():
    for u in URLS:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            z = zipfile.ZipFile(io.BytesIO(data))
            b = z.read([n for n in z.namelist() if n.lower().endswith('.csv')][0])
            print('ok', u)
            try: return b.decode('utf-8')
            except UnicodeDecodeError: return b.decode('cp932')
        except Exception as e:
            print('ng', u, e)
    # どれもだめなら、ダウンロードの案内ページにあるzipの場所を出して終わる
    for page in ['https://www.post.japanpost.jp/zipcode/download.html','https://www.post.japanpost.jp/zipcode/dl/kogaki-zip.html','https://www.post.japanpost.jp/zipcode/dl/utf-zip.html']:
        try:
            h = urllib.request.urlopen(urllib.request.Request(page, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8','ignore')
            print(page, re.findall(r'href="([^"]+\.zip)"', h))
        except Exception as e:
            print('ng', page, e)
    raise SystemExit(1)
raw = fetch()
def hira(s):
    s = unicodedata.normalize('NFKC', s)
    return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
out = {}
for r in csv.reader(io.StringIO(raw)):
    code, town_k, town = r[0], r[5], r[8]
    if town in ('以下に掲載がない場合',) or '（' in town and '）' not in town:
        continue
    town = re.sub(r'（.*?）', '', town)
    town_k = re.sub(r'\(.*?\)', '', unicodedata.normalize('NFKC', town_k))
    town = re.sub(r'[一二三四五六七八九十]+丁目$', '', town)
    town_k = re.sub(r'(イチ|ニ|サン|ヨン|ゴ|ロク|ナナ|ハチ|キュウ|ジュウ)+チョウメ$', '', town_k)
    if not town or not town_k:
        continue
    out.setdefault(code[:2], {}).setdefault(code, {}).setdefault(town, hira(town_k))
os.makedirs('kana', exist_ok=True)
for pref, d in out.items():
    with open(f'kana/{pref}.json', 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
print(sum(len(v) for d in out.values() for v in d.values()), 'towns')
