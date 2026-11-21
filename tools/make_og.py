"""링크를 공유할 때 뜨는 미리보기 그림(img/og.jpg, 1200x630)을 만든다.

python -I tools/make_og.py <사이트 폴더>
tools/og.html 을 크롬(화면 없이)으로 찍어 JPG 로 저장한다. 글꼴·궤도 모양은 og.html 에서 고친다.
미리보기 서버(launch.json 의 minsu-profile, 포트 5184)가 켜져 있어야 한다.
"""
import os, sys, subprocess, tempfile
from PIL import Image

SITE = sys.argv[1]
URL = 'http://127.0.0.1:5184/tools/og.html'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Edge 는 화면 없이 찍기가 안 됐다(11-21)

with tempfile.TemporaryDirectory() as tmp:
    png = os.path.join(tmp, 'og.png')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    f'--user-data-dir={os.path.join(tmp, "prof")}', '--window-size=1200,630',
                    '--virtual-time-budget=8000', f'--screenshot={png}', URL], check=True, timeout=120,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(png).convert('RGB')
    assert im.size == (1200, 630), im.size
    im.save(os.path.join(SITE, 'img', 'og.jpg'), quality=88, optimize=True)
print('og ok')
