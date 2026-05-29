import requests
import pandas as pd

# -------------------------------------------------------------------------
# 🔑 성국님 전용 비밀 열쇠 세팅 완료!
# -------------------------------------------------------------------------
TELEGRAM_TOKEN = "8986839399:AAHFNdyjVt36BW8VrqAbSLPKihSEK0iqez0"
CHAT_ID = "5309366498"

# =========================================================================
# 1단계: 네이버 금융 API에서 국내 전체 ETF 리스트 수집
# =========================================================================
url = "https://finance.naver.com/api/sise/etfItemList.nhn"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("🤖 1단계: 네이버 금융에서 전체 ETF 리스트 수집 중...")
response = requests.get(url, headers=headers)
all_etfs = response.json()['result']['etfItemList']

exclude_keywords = [
    '채권', '인버스', '레버리지', '단기채', '통안채', '국고채', 'CD금리', 'KOFR', 
    '선물', '달러', '골드', '원자재', '미국', '글로벌', '인도', '일본', '엔화', 
    '커버드콜', '타겟위클리', '프리미엄', '리츠', '부동산', '액티브'
]

filtered_etfs = []
for etf in all_etfs:
    name = etf.get('itemname', '')
    code = etf.get('itemcode', '')
    if not any(word in name for word in exclude_keywords):
        filtered_etfs.append({'code': code, 'name': name})

filtered_etfs.sort(key=lambda x: x['code'], reverse=True)
target_etfs = filtered_etfs[:6] 

# =========================================================================
# 2단계: 이번 주 신규 ETF 내부 진짜 구성종목(PDF) 실시간 추출
# =========================================================================
print("\n⚡ 2단계: 이번 주 신규 ETF 내부 진짜 구성종목(PDF) 실시간 추출 중...")
all_real_components = []

for target in target_etfs:
    pdf_url = f"https://finance.naver.com/item/getETFAssetCompositionList.nhn?code={target['code']}"
    pdf_res = requests.get(pdf_url, headers=headers)
    
    try:
        pdf_data = pdf_res.json()
        composition_list = pdf_data.get('result', {}).get('etfAssetCompositionList', [])
        
        for asset in composition_list:
            stock_name = asset.get('item_name', '').strip()
            if stock_name and not any(k in stock_name for k in ['현금', '예치금', '원화', 'USD', '종합계']):
                all_real_components.append(stock_name)
    except:
        continue

# =========================================================================
# 3단계: 이번 주 데이터 최종 TOP 5 교집합 연산 및 텔레그램 발송
# =========================================================================
print("\n📊 3단계: 이번 주 누적 패시브 수급 겹치기 연산 및 알림 기동...")

if not all_real_components:
    message = "⚠️ [수급 폭격기 알림]\n현재 장외 시간이거나 주말이라 데이터 통로가 닫혀있습니다. 평일 장중에 가동되면 대장주 실시간 데이터가 쏟아집니다!"
else:
    stock_series = pd.Series(all_real_components)
    result_counts = stock_series.value_counts()

    final_top5 = pd.DataFrame({
        '종목명': result_counts.index,
        '겹치는수': result_counts.values
    }).head(5)

    message = "🚨 이번 주 신규 ETF 공통 분모 [최종 TOP 5] 🚨\n"
    message += "==================================\n"
    for idx, row in final_top5.iterrows():
        message += f"🔥 {row['종목명']} ({row['겹치는수']}개 ETF 중복 편입)\n"
    message += "==================================\n"
    message += "💡 이번 주에 자산운용사들이 동시에 대량 편입한 수급 대장주입니다."

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
response = requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": message})

if response.status_code == 200:
    print("\n✅ 성국님 스마트폰 텔레그램으로 리포트가 전송되었습니다!")
else:
    print("\n❌ 텔레그램 발송 실패")
