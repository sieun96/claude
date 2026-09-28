# -*- coding: utf-8 -*-
"""M2~M4 레슨 실무 상세. lesson_detail.py가 import해서 병합한다."""

MORE = {
"L11": {"readout":"""p값을 정확히 읽는 3가지:
· p < 0.05 = 'H0가 참이라면 이만한 차이가 나올 확률이 5% 미만'. '차이가 있을 확률 95%'가 아니다(가장 흔한 오해).
· p > 0.05 = '차이가 없다'가 아니라 '차이를 입증하지 못했다'. 표본이 작아서일 수 있다.
· p값은 효과 크기를 말하지 않는다. 표본이 크면 무의미한 0.01%p 차이도 유의해진다.""",
  "prompt":"""내가 예전에 소재/실험 결과를 보고한 문장 3개를 붙일게. 각각 통계적으로 정확한 문장으로 고쳐줘.
특히 '차이가 없다', 'A가 이겼다' 같은 단정을 p값·신뢰구간 기준으로 바꿔줘. [문장 3개]"""},

"L12": {"code":"""from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep
a_n, a_conv = 5200, 218      # 소재A: 노출(방문), 구매 — 실제값으로 교체
b_n, b_conv = 5180, 251
stat, p = proportions_ztest([a_conv, b_conv], [a_n, b_n])
lo, hi = confint_proportions_2indep(b_conv, b_n, a_conv, a_n, method='wald')
print(f"A {a_conv/a_n*100:.2f}%  B {b_conv/b_n*100:.2f}%  차이 {(b_conv/b_n-a_conv/a_n)*100:+.2f}%p")
print(f"z={stat:.2f}  p={p:.3f}  95%CI [{lo*100:+.2f}%p, {hi*100:+.2f}%p]")
print("유의" if p < 0.05 else "유의하지 않음(구간이 0 포함하는지 확인)")""",
  "readout":"""출력 예: 차이 +0.65%p, p=0.109, 구간 [-0.15%p, +1.45%p]
· 구간이 0을 포함 → 유의하지 않음. B가 좋아 보여도 채택 금지.
· 표본 5,200은 1%p 검출에 필요한 6,726에 못 미침 → '판정 보류, 기간 연장'.
· AI가 낸 p값과 이 코드 결과를 대조하는 게 검수."""},

"L13": {"code":"""monthly_visits = 12000     # 실제값
aov = 42000                # 객단가(원)
for label, pp in [("하한", -0.0015), ("상한", 0.0145)]:   # L12 신뢰구간
    print(f"{label}: 전환율 {pp*100:+.2f}%p → 월 매출 {pp*monthly_visits*aov:+,.0f}원")""",
  "readout":"""· 통계적 유의성 ≠ 실무적 의미. 유의해도 하한 매출 영향이 변경 비용보다 작으면 무의미.
· 보고는 '월 매출 영향 ○~○원'으로. 의사결정자가 바로 판단한다."""},

"L14": {"code":"""import pandas as pd
from statsmodels.stats.proportion import proportions_ztest, proportion_effectsize
from statsmodels.stats.power import NormalIndPower
df = pd.read_csv('실험인벤토리.csv')   # 열: 방문A,구매A,방문B,구매B
def judge(r):
    if any(pd.isna(r[c]) for c in ['방문A','구매A','방문B','구매B']): return '판정불가(데이터없음)'
    _, p = proportions_ztest([r.구매A, r.구매B], [r.방문A, r.방문B])
    base = r.구매A/r.방문A
    need = NormalIndPower().solve_power(effect_size=proportion_effectsize(base+0.01, base),
                                        alpha=.05, power=.8, alternative='two-sided')
    if p < 0.05: return '유의'
    return '비유의(표본충분)' if min(r.방문A, r.방문B) >= need else '판정보류(표본부족)'
df['판정'] = df.apply(judge, axis=1)
print(df['판정'].value_counts())""",
  "readout":"""· 판정 4종: 유의 / 비유의(표본충분=효과없음) / 판정보류(표본부족) / 판정불가(데이터없음).
· '비유의'와 '판정보류' 구분이 핵심. 1~9번 먼저, 2건은 손으로 검산."""},

"L15": {"code":"""k = 6                       # 동시 비교한 각도/소재 수
alpha = 0.05
print(f"{k}개 비교 시 최소 하나 우연 유의 확률: {(1-(1-alpha)**k)*100:.0f}%")
print(f"본페로니 기준: p < {alpha/k:.4f}")
for a, pv in {"세게지르기":0.004,"좋아진모습":0.03,"불편짚기":0.21}.items():
    print(f"  {a}: p={pv} → {'위너 확정' if pv < alpha/k else '탐색결과(1:1 재검증)'}")""",
  "readout":"""· 6개 비교면 우연 유의 26%, 10개면 40%.
· 본페로니(0.05÷6≈0.008) 넘어야 위너 확정. 동시 비교는 '후보 선별'로만, 위너는 1:1 재검증.
· 소재 판정의 필수 단계.""",
  "interview":"소재 10개 중 하나가 좋았다면 우연일 가능성은요?"},

"L16": {"readout":"""L14 코드로 10~18번 처리. 61건 전체 판정 분포를 센다.
· 재분석이 당시 판정과 다르면 그대로 적는다. '당시엔 채택했지만 재분석하니 보류였다'가 가장 강한 면접 문장.
· 최종: '61건 중 n건 유의, m건 보류, k건 불가' 한 줄."""},

"L17": {"code":"""from scipy.stats import chisquare
observed = [10000, 10600]          # 실제 A/B 방문(노출)
stat, p = chisquare(observed, [sum(observed)/2]*2)
print(f"관측 {observed}  카이제곱 p={p:.5f}", "→ 배정 오류!" if p < 0.01 else "→ 정상")""",
  "readout":"""· 50:50 설계인데 방문이 크게 어긋나면 배정·트래킹 오류(SRM).
· 결과 해석 전에 항상 먼저 돌린다. 배정이 틀렸으면 어떤 결과도 못 믿는다."""},

"L18": {"prompt":"""11월 재분석으로 리포트 1장을 마크다운으로:
1) 요약 한 줄(61건 중 n건 유의, m건 보류) 2) 판정 표 3) 바뀐 운영 규칙 4) 다음 계획
불리한 결과(당시와 달라진 것)도 그대로. [재분석 표 붙여넣기]""",
  "readout":"""· 요약에 전체·유의·보류 건수 + 도입 기준(1%p MDE, 최소 21일).
· 불리한 결과 숨기지 않는 게 강점. 보고서이자 포폴 슬라이드 원본.""",
  "interview":"A/B 테스트 유의성 검정은 하셨나요?"},

"L19": {"code":"""# SKU 회귀 변수 예상 부호 먼저 적기
variables = {"광고비":"+","가격":"-","프로모션더미":"+","반감기가중":"+"}
for v, sign in variables.items(): print(f"{v}: 예상 {sign}")
# 모델 돌린 뒤 실제 부호와 비교 → 다르면 누락변수/공선성 신호""",
  "readout":"""· 모델 보기 전 예상 부호를 적는다. 광고비 coef가 음수면 역인과/누락변수 신호.
· coef는 단위 붙여: '광고비 1만원당 판매 0.8개'."""},

"L20": {"code":"""import statsmodels.api as sm, pandas as pd
df = pd.read_csv('sku_daily.csv')   # 판매량,광고비,가격,프로모션
X = sm.add_constant(df[['광고비','가격','프로모션']])
print(sm.OLS(df['판매량'], X).fit().summary())""",
  "readout":"""summary 5줄:
· coef: 부호가 상식과 맞는지. · std err: coef 대비 크면 못 믿음. · P>|t|: 0.05 넘으면 뺄지 검토.
· R²: 변수 늘면 저절로 오름. · Adj R²: R²와 크게 벌어지면 쓸모없는 변수 많음."""},

"L21": {"code":"""import pandas as pd
df = pd.read_csv('sku_daily.csv', parse_dates=['날짜'])
df['요일'] = df['날짜'].dt.dayofweek
dummies = pd.get_dummies(df['요일'], prefix='요일', drop_first=True).astype(int)
print(dummies.columns.tolist())   # 요일_1~6 (기준: 월)""",
  "readout":"""· 범주 7개면 더미 6개+기준 1개. drop_first로 기준 제외(안 하면 다중공선성).
· 계수는 '기준 대비': 토요일 +12 = 월요일보다 12개 더 판다.
· 프로모션 더미 빼면 그 효과가 광고비에 섞여 광고 효과 과대평가."""},

"L22": {"prompt":"""SKU 예측 모델을 OLS로 돌리고 모두 해줘:
① 계수를 '광고비 1만원당 N개'로 해석 ② VIF(10 넘는 것 표시) ③ 잔차 플롯 2개 ④ 신뢰 못 할 이유 먼저
[변수 목록 붙여넣기]""",
  "readout":"· 예상과 다른 부호에 표시하고 이유 추정. AI가 '문제없다'만 하면 ④번으로 반박 근거를 내게 하는 게 검수."},

"L23": {"code":"""from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm, pandas as pd
df = pd.read_csv('sku_daily.csv')
X = sm.add_constant(df[['광고비','노출수','가격','프로모션']])
for i, c in enumerate(X.columns):
    if c != 'const': print(f"{c}: VIF {variance_inflation_factor(X.values, i):.1f}")""",
  "readout":"""· VIF>10 경고. 광고비·노출수처럼 같이 움직이는 변수 넣으면 계수 불안정.
· 하나 빼거나 합친다. 예측은 괜찮아도 '왜 이 변수' 설명이 무너진다."""},

"L24": {"code":"""import statsmodels.api as sm, pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv('sku_daily.csv')
m = sm.OLS(df['판매량'], sm.add_constant(df[['광고비','가격','프로모션']])).fit()
fig, ax = plt.subplots(1,2,figsize=(11,4))
ax[0].scatter(m.fittedvalues, m.resid, s=8); ax[0].axhline(0,color='r'); ax[0].set_title('예측값 대비')
ax[1].plot(pd.to_datetime(df['날짜']), m.resid); ax[1].axhline(0,color='r'); ax[1].set_title('시간 순')
plt.tight_layout(); plt.savefig('residuals.png', dpi=150)""",
  "readout":"""· 잔차는 0 주변 고르게. 깔때기=분산 불균일, 곡선=모델 형태 오류.
· 12월에만 튀면 연말 시즌 누락 → 시즌 더미. 물결 패턴=자기상관(M4)."""},

"L25": {"prompt":"""SKU 모델을 랜덤포레스트와 선형회귀로 돌려 정확도(MAPE/RMSE) 비교하고,
'왜 선형회귀' 60초 답변 만들어줘. 근거: 정확도 차이 작음 + 발주 담당자에게 계수로 설명 필요. [데이터]""",
  "readout":"""· 상관≠인과. 계수 유의해도 '광고비 늘리면 판매 는다' 자동 성립 안 함.
· 전환은 정확도 아닌 '설명 가능성' 택한 판단. 정확도 차이(실측)를 답변에 넣는다.""",
  "interview":"랜덤포레스트가 더 정확하지 않나요?"},

"L26": {"prompt":"SKU 계수 해설 1장 마크다운: 1)목적 2)변수·계수 표 3)해석 3줄 4)한계(인과 아님·시즌) 5)선택 이유. [계수 붙여넣기]",
  "readout":"· '한계'를 스스로 쓰는 게 핵심. 면접관이 찌르기 전에 짚으면 검수 능력. SKU 8종 다룬 증거."},

"L27": {"readout":"연말 버퍼. 밀린 레슨부터. 다 했으면 M1~M3 확인문제 복습. 약한 개념은 AI에게 예시 3개로 재설명받기."},
"L28": {"readout":"신정 연휴. 쉰다. 밀리면 P1 하나만."},

"L29": {"code":"""import pandas as pd
df = pd.read_csv('daily_sales.csv', parse_dates=['날짜'])
df['요일'] = df['날짜'].dt.dayofweek; df['월'] = df['날짜'].dt.month
print("[요일별 평균]"); print(df.groupby('요일')['매출'].mean().round(0))
print("[월별 평균]"); print(df.groupby('월')['매출'].mean().round(0))
wd = df.groupby('요일')['매출'].mean()
print("요일 최대/최소 차이 %.0f%%" % ((wd.max()/wd.min()-1)*100))""",
  "readout": """· 추세·계절성·요일 셋 분리해야 전후 비교가 안 오염.
· 요일 차이 20%인데 비교 기간 요일 구성이 다르면 가짜 성과. 육아용품은 출산 시즌·명절이 계절성."""},

"L30": {"code":"""import statsmodels.api as sm, pandas as pd
from statsmodels.stats.stattools import durbin_watson
df = pd.read_csv('sku_daily.csv')
m = sm.OLS(df['판매량'], sm.add_constant(df[['광고비','가격','프로모션']])).fit()
print(f"더빈-왓슨: {durbin_watson(m.resid):.2f} (2 근처=정상, 1 미만=양의 자기상관)")""",
  "readout":"""· 일 매출은 자기상관. 일반 회귀는 독립 가정 → 자기상관 있으면 표준오차 과소 → 유의하지 않은 걸 유의로 오판.
· 더빈-왓슨 0.8이면 p값 과신 금지. 대응: 시계열 모델이나 HAC 강건 표준오차."""},

"L31": {"code":"""import pandas as pd
d = pd.read_pickle('lansinoh_meta/daily.pkl')
d['val'] = pd.to_numeric(d['purchase_value']); d['sp'] = pd.to_numeric(d['spend'])
def roas(s,u):
    m = d[(d.date>=s)&(d.date<=u)]; return m.val.sum()/m.sp.sum()
this = roas('2026-08-31','2026-09-22')/roas('2026-08-01','2026-08-30')
last = roas('2025-08-31','2025-09-22')/roas('2025-08-01','2025-08-30')
print(f"올해 배수 {this:.2f} / 작년 배수 {last:.2f} / 계절 제거 순효과 {this/last:.2f}배")""",
  "readout":"""· 8일 전후만 보면 계절성 섞임. 작년 같은 기간 변화를 붙인다.
· 작년도 같은 폭이면 계절성, 올해가 크면 조치 효과. 작년 조건 다르면 DiD로 보강.""",
  "interview":"8일 전후 비교는 계절성이 섞이지 않나요?"},

"L32": {"code":"""pre_t, post_t = 3.07, 4.92     # 처리군(내가 만진) 전/후
pre_c, post_c = 2.50, 3.10     # 대조군(안 만진) 전/후
did = (post_t-pre_t) - (post_c-pre_c)
print(f"처리군 {post_t-pre_t:+.2f} / 대조군 {post_c-pre_c:+.2f} / DiD 순효과 {did:+.2f}")""",
  "readout":"""· DiD=(처리 후-전)-(대조 후-전). 대조군의 계절·시장 변화를 빼면 내 조치만 남는다.
· 가정: 평행 추세(조치 없었다면 같은 방향). 조치 전 추세가 비슷한지 먼저 확인.
· '대조군 대비 추가 +N'이 계절성 반박 최강 근거."""},

"L33": {"readout":"""실제 캠페인으로 DiD 계산.
· 대조군: 같은 기간 안 만진 캠페인. 조치 전 4주 추세가 평행한지 그려 확인.
· 좋은 대조군 2조건: ①조치 영향 없음 ②조치 전 추세 비슷. 평행 안 하면 결과 약하게 말한다."""},

"L34": {"code":"""import pandas as pd
df = pd.read_csv('sku_daily.csv', parse_dates=['날짜']).sort_values('날짜')
split = df['날짜'].quantile(0.83)   # 앞 10개월 학습, 뒤 2개월 검증
train, test = df[df['날짜']<=split], df[df['날짜']>split]
print(f"학습 {train['날짜'].min().date()}~{train['날짜'].max().date()} / 검증 {test['날짜'].min().date()}~{test['날짜'].max().date()}")""",
  "readout":"""· 시계열은 시간 순으로 잘라 검증. 무작위 분할은 미래가 학습에 섞여 정확도 부풀림(데이터 누출).
· 무작위 분할 정확도가 더 높게 나오면 누출 신호. 검증 방식을 밝히면 신뢰 상승."""},

"L35": {"prompt":"""ROAS 방어 3줄 만들어줘. 사실: 메타 +60.2%(3주, 광고비 -20%), Blended 8월 12.4→9월 17.3(전년 2.1배), 대조군 DiD [값].
'한계 인정 → 전년 동기 → 대조군' 순, 각 줄 20초.""",
  "readout":"""· 먼저 '짧다/한계' 인정, 방어는 그 다음.
· '광고비 늘려서가 아니다'가 핵심 방어. 예산 효과 아님을 못 박는다.""",
  "interview":"ROAS가 정말 오른 건가요, 계절 효과 아닌가요?"},

"L36": {"readout":"""통계 면접 6문항 '인정→조치→숫자' 60초:
①유의성(M1·M2) ②표본크기(M1) ③다중비교(M2) ④회귀변수(M3) ⑤계절성(M4) ⑥모델선택(M3).
6개 쓰고 녹음해 듣기. 약한 답변을 2월 모의면접에서 먼저 연습."""},
}
