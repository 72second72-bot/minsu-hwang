"""링크를 공유할 때 뜨는 미리보기 그림(img/og.jpg, 1200x630)을 만든다.

python -I tools/make_og.py <사이트 폴더>
문구를 바꾸면 index.html 의 og:description · twitter:description 과 og:image 의 ?v= 번호도 함께 올린다.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

SITE = sys.argv[1]
EYEBROW = 'URBAN PLANNER · 도시계획 엔지니어'
NAME = '황민수'
LINE1 = '데이터로 읽고,'
LINE2_ACCENT, LINE2_REST = '더 나은 도시와 미래', '를 계획합니다.'
FIELDS = '정비계획 · 공공주택 · 도시관리계획 · 지역개발'

W, H = 1200, 630
im = Image.new('RGB', (W, H), '#0f2f4d'); d = ImageDraw.Draw(im)
for y in range(H):
    t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((15, 47, 77), (10, 31, 53))))
for x in range(0, W, 22):
    for y in range(0, H, 22): d.point((x, y), fill=(40, 70, 100))
d.ellipse((640, 40, 1180, 600), outline=(70, 110, 140), width=2)

ph = Image.open(os.path.join(SITE, 'img', 'profile.jpg')).convert('RGB')
pw = 360; ph = ph.resize((pw, int(ph.height * pw / ph.width))).crop((0, 0, pw, 460))
mask = Image.new('L', (pw, 460), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, 460), radius=150, fill=255)
im.paste(ph, (760, 85), mask)

F = 'C:/Windows/Fonts/'
B = ImageFont.truetype(F + 'malgunbd.ttf', 88); M = ImageFont.truetype(F + 'malgun.ttf', 34)
MB = ImageFont.truetype(F + 'malgunbd.ttf', 34); S = ImageFont.truetype(F + 'malgunbd.ttf', 24)
R = ImageFont.truetype(F + 'malgun.ttf', 24)
d.text((80, 150), EYEBROW, font=S, fill='#8fb6cf')
d.text((80, 195), NAME, font=B, fill='white')
d.text((80, 320), LINE1, font=M, fill='white')
x = 80; d.text((x, 368), LINE2_ACCENT, font=MB, fill='#f5a524'); x += d.textlength(LINE2_ACCENT, font=MB)
d.text((x, 368), LINE2_REST, font=M, fill='white')
d.text((80, 470), FIELDS, font=R, fill=(190, 208, 225))
im.save(os.path.join(SITE, 'img', 'og.jpg'), quality=86)
print('og ok')
