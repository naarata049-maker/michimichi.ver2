# 日本郵便の郵便番号データ（読みがな付き）から、市区町村コード×町名→ひらがな の表を県ごとに作る
import csv, io, json, os, re, unicodedata, urllib.request, zipfile
URL = 'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip'
raw = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL).read())).read('KEN_ALL.CSV').decode('cp932')
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
