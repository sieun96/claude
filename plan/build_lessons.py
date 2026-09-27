# -*- coding: utf-8 -*-
import json, sys, html
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('plan.json', encoding='utf-8'))
L = d['lessons']; WHY = d['why']


def esc(s): return html.escape(str(s or ''))


MODNAME = {'M1': '실험 설계와 표본 크기', 'M2': '비율 비교와 p값', 'M3': '회귀 분석',
           'M4': '시계열', '면접': '면접 준비', '지원': '지원·협상'}
MODCOL = {'M1': 'm1', 'M2': 'm2', 'M3': 'm3', 'M4': 'm4', '면접': 'iv', '지원': 'ap'}
mods = {}
for l in L:
    mods.setdefault(l['mod'], []).append(l)

cards = []
for m, ls in mods.items():
    inner = []
    for l in ls:
        concepts = ''.join('<li>%s</li>' % c for c in (l.get('concepts') or []))
        practice = ''.join('<li>%s</li>' % esc(p) for p in (l.get('practice') or []))
        out = '<div class="lo"><span>산출물</span>%s</div>' % esc(l['output']) if l.get('output') else ''
        iv = '<div class="lo iv"><span>면접</span>%s</div>' % esc(l['interview']) if l.get('interview') else ''
        use = '<p class="use"><b>실무에 쓰는 법</b> %s</p>' % esc(l.get('use')) if l.get('use') else ''
        inner.append(
            '<details class="lesson"><summary><span class="lid">%s</span><span class="lt">%s</span><span class="ld">%s</span></summary>'
            '<div class="lb"><p class="goal">%s</p>'
            '<div class="blk"><h4>개념</h4><ul>%s</ul></div>'
            '<div class="blk"><h4>실습</h4><ul class="p">%s</ul></div>'
            '<div class="quiz"><div class="q">Q. %s</div><div class="a">%s</div></div>'
            '%s%s%s</div></details>'
            % (esc(l['id']), esc(l['title']), esc(l['date']), esc(l['goal']),
               concepts, practice, esc(l['q']), esc(l['a']), use, out, iv))
    cards.append(
        '<section class="mod %s"><div class="mh"><span class="mtag">%s</span><h2>%s</h2><span class="mc">%d개 레슨</span></div>'
        '<p class="why">%s</p><div class="ll">%s</div></section>'
        % (MODCOL[m], esc(m), MODNAME.get(m, m), len(ls), esc(WHY.get(m, '')), ''.join(inner)))

CSS = open('lessons.css', encoding='utf-8').read()
HTML = (
    '<title>통계 학습 프로그램</title>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">\n'
    '<style>%s</style>\n<div class="wrap"><header>'
    '<div class="lbl">STUDY PROGRAM · 52 LESSONS</div>'
    '<h1>실무 통계 학습 프로그램 전체 목록</h1>'
    '<p class="sub">계산은 AI가, 검수는 내가. 데일리 앱이 날짜마다 하나씩 보여주는 레슨을 여기서 한눈에 본다. 각 레슨을 눌러 개념·실습·확인문제를 펼친다.</p>'
    '<div class="legend"><span class="lg m1">M1 실험설계</span><span class="lg m2">M2 p값</span><span class="lg m3">M3 회귀</span><span class="lg m4">M4 시계열</span><span class="lg iv">면접</span><span class="lg ap">지원</span></div>'
    '</header>%s'
    '<footer>박시은 · 통계 학습 · 데일리 앱에 통합 · 2026.09.29~2027.03</footer></div>'
    % (CSS, ''.join(cards)))
open('lessons.html', 'w', encoding='utf-8').write(HTML)
print('lessons.html:', len(HTML) // 1000, 'KB /', len(L), '레슨')
