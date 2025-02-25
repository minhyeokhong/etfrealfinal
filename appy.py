import streamlit as st
import pandas as pd
import numpy as np

# KRX ETF 정보 데이터 불러오기
def load_krx_etf_data():
    url = "http://data.krx.co.kr/comm/fileDn/downloadExcel.do?key=etf_bydd_trd"  # 실제 KRX API 또는 데이터 파일 URL 입력
    df = pd.read_excel(url)
    return df

def get_etf_info_from_krx(df, etf_name):
    """
    KRX 데이터에서 특정 ETF 정보를 검색하는 함수
    """
    etf_data = df[df["ETF명"].str.contains(etf_name, na=False)]
    if etf_data.empty:
        return None
    return etf_data.iloc[0]

def calculate_nav(total_assets, total_shares):
    return total_assets / total_shares

def calculate_premium_discount(etf_price, nav):
    return ((etf_price - nav) / nav) * 100

def calculate_tracking_error(etf_returns, benchmark_returns):
    differences = np.array(etf_returns) - np.array(benchmark_returns)
    return np.std(differences)

# Streamlit UI
st.title("ETF 정보 비교 검색기")

etf_names = []
for i in range(3):
    etf_name = st.text_input(f"ETF {i+1} 이름을 입력하세요:")
    etf_names.append(etf_name)

total_assets = st.number_input("총 자산 (원)", min_value=0.0, format="%f")
total_shares = st.number_input("총 발행 주식 수", min_value=1, format="%d")
etf_price = st.number_input("ETF 시장 가격 (원)", min_value=0.0, format="%f")

etf_returns = st.text_area("ETF 수익률 목록 (쉼표로 구분)")
benchmark_returns = st.text_area("벤치마크 수익률 목록 (쉼표로 구분)")

if st.button("검색"):
    with st.spinner("ETF 정보를 불러오는 중..."):
        df = load_krx_etf_data()
        comparison_data = []
        
        for etf_name in etf_names:
            if etf_name:
                etf_info = get_etf_info_from_krx(df, etf_name)
                if etf_info is not None:
                    data = {
                        "ETF명": etf_info["ETF명"],
                        "유형": etf_info["유형"],
                        "펀드보수": f"{etf_info['펀드보수']}%",
                        "자산운용사": etf_info["자산운용사"],
                        "PDF 링크": etf_info.get("PDF 링크", "없음")
                    }
                    
                    if total_assets and total_shares:
                        nav = calculate_nav(total_assets, total_shares)
                        data["NAV"] = f"{nav:.2f} 원"
                        
                        if etf_price:
                            premium_discount = calculate_premium_discount(etf_price, nav)
                            data["괴리율"] = f"{premium_discount:.2f}%"
                    
                    if etf_returns and benchmark_returns:
                        try:
                            etf_returns_list = list(map(float, etf_returns.split(',')))
                            benchmark_returns_list = list(map(float, benchmark_returns.split(',')))
                            
                            if len(etf_returns_list) == len(benchmark_returns_list):
                                tracking_error = calculate_tracking_error(etf_returns_list, benchmark_returns_list)
                                data["추적 오차율"] = f"{tracking_error:.4f}"
                            else:
                                st.warning("ETF 수익률과 벤치마크 수익률의 개수가 일치해야 합니다.")
                        except ValueError:
                            st.warning("올바른 숫자 형식으로 입력하세요.")
                    
                    comparison_data.append(data)
                else:
                    st.warning(f"ETF 정보를 찾을 수 없습니다: {etf_name}")
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.write("### ETF 비교 결과")
            st.dataframe(df_comparison)
