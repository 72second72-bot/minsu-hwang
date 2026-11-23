"""작품·연구 보기 창에 쓰는 그림을 만든다.

python -I tools/build_works.py <사이트 폴더> <슬라이드 PNG 폴더>
  슬라이드 PNG 폴더: 키별 하위 폴더(gyeyang, ydp, thesis, ghm, smoke, goyang)에 001.png … (PowerPoint/PDF 에서 2000px 로 내보낸 것)
결과: img/works/<키>/NN.jpg(보기용) · t/NN.jpg(작은 그림) · panel-N.jpg(판넬) · img/thumb-<키>.jpg(카드) · js/works-data.js
"""
import os, sys, json
import fitz
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SITE, SL = sys.argv[1], sys.argv[2]
IMG = os.path.join(SITE, 'img')
PF = r'E:/01_회사관련/12_KG 신입 입사서류/황민수_도시계획_포트폴리오.pdf'

def rng(*parts):
    out = []
    for p in parts:
        if isinstance(p, tuple): out += list(range(p[0], p[1] + 1))
        else: out.append(p)
    return out

DECKS = {
    'goyang': rng(2, 4, 6, 7, (9, 11), (13, 24), (26, 28), (30, 33), (35, 38), (40, 43), (45, 53), 55, 56, (58, 62), (64, 68)),
    'gyeyang': rng((1, 28)),
    'ydp': rng((2, 32)),
    'thesis': rng((1, 42)),
    'ghm': rng((1, 49)),  # 50~52 는 중간발표 때 비워 둔 자리(통계 검증·결론)라 뺀다
    'smoke': rng((1, 22)),
}
TITLES = {
    'goyang': '2040 고양 도시기본계획 & 장항·대곡 지구단위계획',
    'gyeyang': '인천 계양 신도시계획',
    'ydp': '영등포 스마트복합지구 재개발 지구단위계획',
    'thesis': 'POI 빅데이터와 공간회귀모형 및 기계학습 알고리즘을 활용한 도시의 물리적 환경과 여름철 지표온도의 관계 분석',
    'ghm': '새로운 광화문광장 조성 후의 여름철 미기후 및 열쾌적성 변화',
    'smoke': '서울 강남대로 일대 공공가로에 설치된 흡연구역에 대한 이용자 및 보행자 만족도 비교',
    'envidx': '빅데이터 기반 인공지능을 활용한 도시계획기술 개발',
    'twin': '디지털트윈 시뮬레이션 기술 기반 스마트시티 통합 설계 솔루션 개발',
}
SET_NAME = {'goyang': '발표 자료', 'gyeyang': '발표 자료', 'ydp': '발표 자료', 'thesis': '학위논문 심사 발표',
            'ghm': '연구 발표 자료', 'smoke': '학술대회 발표 자료'}

_pf = fitz.open(PF)
_pfcache = {}
def pf_page(n):
    if n not in _pfcache:
        x = _pf[n - 1].get_images(full=True)[0][0]
        pix = fitz.Pixmap(_pf, x)
        if pix.n > 3: pix = fitz.Pixmap(fitz.csRGB, pix)
        _pfcache[n] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    return _pfcache[n]

def save(im, path, maxw=None, maxh=None, q=80):
    im = im.convert('RGB')
    if maxw and im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    if maxh and im.height > maxh: im = im.resize((round(im.width * maxh / im.height), maxh), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, quality=q, optimize=True, progressive=True)
    return im.size

def fit169(im, pad=None, top=0.5):
    """16:9 로 맞춘다. 넓으면 가운데를 자르고, 높으면 top 비율 위치에서 자른다. pad 색을 주면 자르지 않고 채운다."""
    W, H = im.size; target = 16 / 9
    if pad is not None:
        if W / H > target: nw, nh = W, round(W / target)
        else: nw, nh = round(H * target), H
        c = Image.new('RGB', (nw, nh), pad); c.paste(im, ((nw - W) // 2, (nh - H) // 2)); return c
    if W / H > target:
        nw = round(H * target); x = (W - nw) // 2; return im.crop((x, 0, x + nw, H))
    nh = round(W / target); y = round((H - nh) * top); return im.crop((0, y, W, y + nh))

def frac(im, box):
    W, H = im.size
    return im.crop((round(box[0] * W), round(box[1] * H), round(box[2] * W), round(box[3] * H)))

data = {}
def add_set(key, name, items, kind='slides'):
    data.setdefault(key, {'title': TITLES[key], 'sets': []})['sets'].append({'name': name, 'kind': kind, 'items': items})

# 1) 발표 자료 슬라이드
for key, pages in DECKS.items():
    items = []
    for i, n in enumerate(pages, 1):
        src = os.path.join(SL, key, f'{n:03d}.png')
        im = Image.open(src)
        w, h = save(im, os.path.join(IMG, 'works', key, f'{i:02d}.jpg'), maxw=1800, q=78)
        save(im, os.path.join(IMG, 'works', key, 't', f'{i:02d}.jpg'), maxw=240, q=70)
        items.append({'src': f'img/works/{key}/{i:02d}.jpg', 't': f'img/works/{key}/t/{i:02d}.jpg', 'w': w, 'h': h})
    add_set(key, SET_NAME[key], items)
    print(key, len(items), flush=True)

# 2) 연구 과제: 포트폴리오에 정리한 쪽만
for key, pages in {'envidx': [11, 12], 'twin': [13, 14]}.items():
    items = []
    for i, n in enumerate(pages, 1):
        im = pf_page(n)
        w, h = save(im, os.path.join(IMG, 'works', key, f'{i:02d}.jpg'), maxw=2400, q=80)
        save(im, os.path.join(IMG, 'works', key, 't', f'{i:02d}.jpg'), maxw=240, q=70)
        items.append({'src': f'img/works/{key}/{i:02d}.jpg', 't': f'img/works/{key}/t/{i:02d}.jpg', 'w': w, 'h': h})
    add_set(key, '연구 요약', items)
    print(key, len(items), flush=True)

# 3) 판넬 (원본 포트폴리오 8001x4501 에서 자름)
p7 = pf_page(7)
panels = [('Colorize Goyang', (0, 250, 2000, 4250)), ('Realize Janghang', (2000, 250, 5000, 4250)),
          ('Harmonize Daegok', (5000, 250, 8001, 4250))]
items = []
for i, (nm, box) in enumerate(panels, 1):
    im = p7.crop(box)
    w, h = save(im, os.path.join(IMG, 'works', 'goyang', f'panel-{i}.jpg'), maxh=3400, q=82)
    save(im, os.path.join(IMG, 'works', 'goyang', 't', f'panel-{i}.jpg'), maxh=240, q=70)
    items.append({'src': f'img/works/goyang/panel-{i}.jpg', 't': f'img/works/goyang/t/panel-{i}.jpg', 'w': w, 'h': h, 'cap': nm})
add_set('goyang', '판넬', items, 'panel')
p10 = pf_page(10)
im = p10.crop((825, 0, 7200, 4501)).rotate(-90, expand=True)
w, h = save(im, os.path.join(IMG, 'works', 'gyeyang', 'panel-1.jpg'), maxw=2600, q=82)
save(im, os.path.join(IMG, 'works', 'gyeyang', 't', 'panel-1.jpg'), maxh=240, q=70)
add_set('gyeyang', '판넬', [{'src': 'img/works/gyeyang/panel-1.jpg', 't': 'img/works/gyeyang/t/panel-1.jpg', 'w': w, 'h': h}], 'panel')
# 판넬을 먼저 보이게
for k in ('goyang', 'gyeyang'):
    data[k]['sets'].sort(key=lambda s: s['kind'] != 'panel')

# 4) 카드 대표 그림 (16:9)
def slide(key, n): return Image.open(os.path.join(SL, key, f'{n:03d}.png')).convert('RGB')
thumbs = {
    'goyang': fit169(p7.crop((2000, 620, 5000, 2330))),
    # 오른쪽 검은 테두리·반쯤 잘린 방위표가 보여 '우측이 잘린 느낌'(11-23 민수님) → 마스터플랜 안쪽만, 양옆 원형 그림 여백을 맞춰 자름
    'gyeyang': fit169(p10.crop((2860, 1065, 4790, 4496)).rotate(-90, expand=True)),
    'ydp': fit169(frac(slide('ydp', 13), (0, 0.09, 1, 1))),
    'thesis': fit169(frac(slide('thesis', 32), (0.02, 0.09, 0.98, 0.98)), top=0.45),
    'ghm': fit169(frac(slide('ghm', 24), (0, 0.16, 1, 0.96))),
    'smoke': fit169(frac(slide('smoke', 12), (0.03, 0.205, 0.97, 0.9)), top=0.1),
    'envidx': fit169(pf_page(12).crop((250, 1080, 6900, 4180)), pad=pf_page(12).getpixel((60, 4400))),
    'twin': fit169(pf_page(14).crop((300, 1090, 4660, 4190)), pad=pf_page(14).getpixel((60, 4400))),
}
for k, im in thumbs.items():
    save(im, os.path.join(IMG, f'thumb-{k}.jpg'), maxw=1400, q=82)
print('thumbs ok')

with open(os.path.join(SITE, 'js', 'works-data.js'), 'w', encoding='utf-8') as f:
    f.write('// tools/build_works.py 가 만든다. 손으로 고치지 않는다.\nwindow.WORKS = ')
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print('data ok', {k: [len(s['items']) for s in v['sets']] for k, v in data.items()})
