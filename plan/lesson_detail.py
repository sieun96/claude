# -*- coding: utf-8 -*-
"""레슨별 실무 상세. code(복붙 코드), prompt(AI 프롬프트 전문), readout(결과 읽는 법).
plan.py가 이 DETAIL을 각 레슨에 붙인다. 없는 레슨은 그대로 둔다."""

DETAIL = {}


def d(id, code=None, prompt=None, readout=None):
    DETAIL[id] = {"code": code, "prompt": prompt, "readout": readout}


# ============================== M1 실험 설계 ==============================
d("L01",
  prompt="""내 A/B 테스트 결과를 검정하려 한다. 먼저 가설을 정리해줘.
- 실험: [무엇을 바꿨는지, 예: 유리젖병 240ml 상세페이지 2P vs 3P 옵션]
- 주지표: [예: 구매전환율]
가설을 이 형식으로 써줘:
  귀무가설(H0): 두 안의 [주지표]는 같다
  대립가설(H1): 다르다 (양측)
그리고 1종 오류와 2종 오류가 이 실험에서 각각 어떤 실무 손해로 이어지는지 한 줄씩 알려줘.""",
  readout="""가설을 쓸 때 확인할 것:
· H0는 항상 '차이가 없다'. 검정은 이걸 버릴 근거를 찾는 것이지 H1을 증명하는 게 아니다.
· 양측(다르다) vs 단측(더 낫다). 특별한 이유가 없으면 양측이 기본. 단측은 반대 방향 변화를 못 잡는다.
· 1종 오류(없는 차이를 있다고 판정) = 효과 없는 안을 채택해 비용 낭비.
  2종 오류(있는 차이를 놓침) = 좋은 안을 버림. 어느 쪽 손해가 큰지가 α·검정력 설정을 좌우한다.""")

d("L02",
  code="""# 표본 크기 감각: 세 가지 MDE 비교
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import NormalIndPower
import math

base = 0.04            # 기준 전환율 4%
daily = 800           # 하루 방문(두 그룹 합)
for mde in (0.02, 0.01, 0.005):
    es = proportion_effectsize(base + mde, base)
    n = NormalIndPower().solve_power(effect_size=es, alpha=0.05,
                                     power=0.8, alternative='two-sided')
    days = math.ceil((n * 2 / daily) / 7) * 7      # 7일 단위 올림
    print(f"MDE +{mde*100:.1f}%p → 그룹당 {math.ceil(n):,}명 · {days}일")
""",
  readout="""출력:  +2.0%p → 1,846명·7일 / +1.0%p → 6,726명·21일 / +0.5%p → 25,531명·64일
· MDE를 절반으로 줄이면 표본은 약 4배(제곱 반비례). 이게 감각의 핵심.
· 0.5%p는 그룹당 2.5만 명. 대부분 상품은 현실적으로 못 잡는다. 큰 변화만 테스트하라는 신호.""")

d("L03",
  code="""# sample_size.py: 실험 기간 계산기 (복붙해서 저장)
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import NormalIndPower
import math

def plan_experiment(base_cvr, mde_pp, daily_visits, split=0.5):
    \"\"\"base_cvr: 현재 전환율(0.04) / mde_pp: 잡을 최소차이(%p, 0.01)
       daily_visits: 하루 총 방문 / split: 배분(0.5=50:50)\"\"\"
    es = proportion_effectsize(base_cvr + mde_pp, base_cvr)
    n = NormalIndPower().solve_power(effect_size=es, alpha=0.05,
                                     power=0.8, alternative='two-sided')
    n = math.ceil(n)
    per_day = daily_visits * min(split, 1 - split) * 2   # 두 그룹 유효 유입
    days = math.ceil((n * 2 / daily_visits) / 7) * 7
    return {"그룹당_표본": n, "총_표본": n * 2, "필요_일수": days}

print(plan_experiment(0.04, 0.01, 800))
# → {'그룹당_표본': 6726, '총_표본': 13452, '필요_일수': 21}
""",
  prompt="""위 plan_experiment 함수를 만들고 싶다. statsmodels로 작성해줘.
입력은 기준 전환율·최소차이(%p)·하루 방문수·배분, 출력은 그룹당 표본·필요 일수(7일 단위 올림).
0.04, 0.01, 800을 넣어 6,726명·21일이 나오는지 검증도 같이 해줘.""",
  readout="""· 그룹당 표본이 상식 범위인가: 전환율 4%·1%p면 보통 수천 명. 수백이 나오면 계산 오류 의심.
· 필요 일수는 7일 배수여야 요일 구성이 두 그룹에 고르게 들어간다.
· 이 함수를 테스트 시작 전에 돌려 '며칠 필요'를 관리대장 비고에 먼저 적는다.""")

d("L04",
  code="""# 상품별 실험 가능 여부: 트래픽으로 거르기
import pandas as pd, math
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import NormalIndPower

# 실제 상품 데이터로 교체 (최근 4주 일평균)
products = pd.DataFrame([
    {"상품":"유리젖병240","일방문":420,"전환율":0.045},
    {"상품":"라놀린10ml","일방문":180,"전환율":0.032},
    {"상품":"수유패드","일방문":650,"전환율":0.051},
])
def need_days(cvr, mde, daily):
    es = proportion_effectsize(cvr + mde, cvr)
    n = NormalIndPower().solve_power(effect_size=es, alpha=.05, power=.8, alternative='two-sided')
    return math.ceil((math.ceil(n)*2/daily)/7)*7

for mde in (0.005, 0.01, 0.02):
    products[f"+{mde*100:.1f}%p"] = products.apply(
        lambda r: (lambda d: "실험불가" if d > 56 else f"{d}일")(need_days(r.전환율, mde, r.일방문)), axis=1)
print(products.to_string(index=False))
""",
  readout="""· 8주(56일)를 넘으면 '실험 불가'로 표시. 그 사이 시즌·트렌드가 섞여 결과를 못 믿는다.
· 트래픽 적은 상품(라놀린10ml)은 작은 MDE 칸이 전부 '실험불가'로 뜬다.
· 결론: 트래픽 적은 상품은 큰 변화(2%p)만 테스트하거나, 여러 상품을 묶거나, 실험 대신 전후+대조군(M4).""")

d("L05",
  code="""# Peeking이 거짓 양성을 얼마나 키우나: 직접 시뮬레이션
import numpy as np
rng = np.random.default_rng(0)
base, daily, days, trials = 0.04, 800, 21, 4000
false_pos_fixed = false_pos_peek = 0
from statsmodels.stats.proportion import proportions_ztest
for _ in range(trials):
    a = rng.random((days, daily//2)) < base   # 실제 차이 0
    b = rng.random((days, daily//2)) < base
    # 매일 확인(peeking): 하루라도 유의하면 양성
    peeked = False
    for dd in range(1, days+1):
        ca, cb = a[:dd].sum(), b[:dd].sum()
        na, nb = dd*(daily//2), dd*(daily//2)
        _, p = proportions_ztest([ca, cb], [na, nb])
        if p < 0.05: peeked = True; break
    if peeked: false_pos_peek += 1
    # 마지막 날만 판정
    _, p = proportions_ztest([a.sum(), b.sum()], [days*(daily//2)]*2)
    if p < 0.05: false_pos_fixed += 1
print(f"기간고정 거짓양성 {false_pos_fixed/trials*100:.1f}% (기대 5%)")
print(f"매일 peeking 거짓양성 {false_pos_peek/trials*100:.1f}%")
""",
  readout="""· 출력: 기간고정 약 5%, peeking 약 25%. 매일 훔쳐보면 거짓 양성이 5배로 뛴다.
· 이게 '기간을 먼저 정하고 그 전엔 판정 안 한다'가 원칙인 이유. 본인 눈으로 확인하는 시뮬레이션.
· 중간에 볼 수 있는 건 운영 사고(품절·트래킹 오류)뿐. 성과는 정한 날에만 본다.""")

d("L06",
  prompt="""실험 설계서 템플릿을 만들려 한다. 아래 항목을 채우는 마크다운 표를 만들어줘.
가설(H0/H1) · 주지표(1개) · 보조지표 · 기준 전환율 · MDE · 그룹당 표본 · 기간(시작~종료) ·
배정 방식(동시분할/시기분할) · 중단 기준 · 판정 기준(결과 보기 전 확정) · 결과 기록란
그리고 다음에 돌릴 실험 하나를 예시로 채워줘: [실험 내용 입력]""",
  readout="""· 주지표는 반드시 1개. 2개 이상이면 하나가 우연히 유의해진다(L15 다중비교).
· 판정 기준은 '결과를 보기 전에' 적는다. 결과 보고 기준을 고르면 검정이 무의미.
· 이 템플릿 1장이 포트폴리오에서 '실험 체계를 만들었다'의 증거물이 된다.""")

d("L07",
  code="""# 메타 소재 테스트: 광고세트 내 비교가 왜 편향되나 확인
# 운영_소재 CSV에서 같은 광고세트에 여러 소재가 있는 경우를 찾는다
import csv
from collections import defaultdict
rows = list(csv.DictReader(open('sheets/creative__운영_소재.csv', encoding='utf-8-sig')))
byset = defaultdict(list)
for r in rows:
    if r.get('세트이름','').strip():
        byset[r['세트이름']].append((r['소재명'], r.get('노출',''), r.get('클릭','')))
multi = {k:v for k,v in byset.items() if len(v) > 1}
print(f"소재 2개 이상인 광고세트: {len(multi)}개")
for s, mats in list(multi.items())[:3]:
    print(f"\\n[{s}]")
    for nm, imp, clk in mats:
        print(f"  {nm[:30]} 노출 {imp} 클릭 {clk}")
print("\\n→ 이 세트들은 메타가 노출을 몰아줘서 소재 간 CTR 비교가 편향됨")
""",
  readout="""· 한 광고세트에 소재를 여러 개 넣으면 메타가 '좋아 보이는' 소재에 노출을 몰아준다(무작위 아님).
· 그래서 소재끼리 CTR을 비교해 검정하는 건 엄밀하지 않다. 공정하려면 메타 A/B 테스트 기능으로 대상을 겹치지 않게 나눈다.
· 노출 단위 CTR은 같은 사람의 반복 노출이 섞여 독립이 아니다. 도달(사람) 기준을 함께 본다.""")

d("L08",
  code="""# 61건 인벤토리 자동 골격: 테스트 운영기록에서 실험 목록 추출
import csv, glob
files = glob.glob('sheets/test__*.csv')
inv = []
for f in files:
    prod = f.split('test__')[1].replace('.csv','')
    for r in csv.reader(open(f, encoding='utf-8-sig')):
        ch = (r[0] if r else '').strip()
        if ch in ('자사몰','스마트스토어','쿠팡','네이버'):
            inv.append({"상품":prod, "채널":ch, "테스트명":r[1] if len(r)>1 else '',
                        "시작":r[2] if len(r)>2 else '', "종료":r[3] if len(r)>3 else ''})
print(f"총 {len(inv)}건")
for x in inv[:5]: print(x)
# 필요 열 추가: 배정방식, 그룹별 방문/주문, 주지표, 당시판정 → 수동 보강
""",
  readout="""· 자동으로 뽑히는 건 상품·채널·테스트명·기간까지. 나머지(그룹별 방문·주문)는 수동 확인.
· 주문 수만 있고 방문 수가 없는 실험은 비율 검정 불가 → '데이터 부족'으로 분류(그것도 정직한 결과).
· 이 인벤토리가 11월 재분석의 입력. 빈칸마다 어느 리포트에서 채울지 메모.""")

d("L09",
  prompt="""내가 만든 실험 설계 체계를 면접 답변 60초로 만들어줘. 아래 사실을 써서:
- 예전엔 며칠 보고 감으로 판단했다
- 표본 크기 계산기를 만들어 '전환율 4%에서 1%p 잡으려면 그룹당 6,700명, 하루 800명이면 3주'를 먼저 계산한다
- 기간을 정하면 그 전엔 판정 안 한다(peeking 방지)
'문제 → 조치 → 결과' 순서, 숫자 포함, 60초 분량.""",
  readout="""· 답변에 반드시 숫자를 넣는다: 6,700명·3주 같은 구체값이 '체계가 있다'를 증명한다.
· '표본 크기를 어떻게 정하나' 질문의 4요소: 기준 전환율·MDE·유의수준(0.05)·검정력(0.8).
· 60초를 넘기면 요점이 흐려진다. 소리 내어 읽고 시간을 잰다.""")

d("L10",
  readout="""버퍼 주간. 밀린 레슨을 먼저 끝낸다. 다 했으면 계산기에 'MDE별 필요일수 표를 한 번에 출력'하는 기능을 더한다.
막히는 개념은 메모에 적고, AI에게 '이 개념을 실무 예시 3개로 다시 설명해줘'로 물어 채운다.""")


# ── M2~M4 병합 ──
try:
    from lesson_detail_m234 import MORE
    for _id, _v in MORE.items():
        DETAIL[_id] = {"code": _v.get("code"), "prompt": _v.get("prompt"),
                       "readout": _v.get("readout"), "interview": _v.get("interview")}
except ImportError:
    pass
