import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 사이트 기본 설정
st.set_page_config(page_title="완성형 주식 분석기", layout="wide")
st.title("📊 완성형 주식 분석 대시보드")

# 2. 사이드바 설정 (사용자 입력)
st.sidebar.header("설정")
ticker = st.sidebar.text_input("종목 코드 (예: 005930.KS, AAPL)", "005930.KS")
buy_price = st.sidebar.number_input("매수 단가 (원/달러)", min_value=0.0, value=0.0)

# 3. 데이터 로드 (캐싱을 통해 속도 향상)
@st.cache_data
def get_stock_data(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(period="1y")
    return stock, df

if ticker:
    try:
        stock, df = get_stock_data(ticker)
        info = stock.info

        # 4. 재무 지표 표시
        st.subheader("기업 핵심 지표")
        col1, col2, col3 = st.columns(3)
        col1.metric("현재가", f"{info.get('currentPrice', 'N/A')}")
        col2.metric("PER", f"{info.get('trailingPE', 'N/A')}")
        
        market_cap = info.get('marketCap', 0)
        col3.metric("시가총액", f"{market_cap / 1e12:.2f} 조원" if market_cap else "N/A")

        # 5. 수익률 계산
        if buy_price > 0:
            current_price = info.get('currentPrice', 0)
            if current_price:
                roi = ((current_price - buy_price) / buy_price) * 100
                st.info(f"### 💰 매수 단가 대비 수익률: {roi:.2f}%")
            else:
                st.warning("현재가를 불러올 수 없어 수익률을 계산할 수 없습니다.")

        # 6. 차트 시각화
        if not df.empty:
            st.subheader("주가 차트")
            fig = go.Figure(data=[go.Candlestick(x=df.index, 
                            open=df['Open'], 
                            high=df['High'], 
                            low=df['Low'], 
                            close=df['Close'])])
            fig.update_layout(title=f"{ticker} 최근 1년 주가 흐름", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("차트 데이터를 불러올 수 없습니다.")
            
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
