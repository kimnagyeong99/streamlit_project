import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
from io import BytesIO
import plotly.express as px

st.write('# 무슨 주식을 사야 부자가 될까...')
url = "http://kind.krx.co.kr/corpgeneral/corpList.do" 

# 사이드바에 입력 상자 생성
st.sidebar.title("회사이름과 기간을 입력하세요")
user_input = st.sidebar.text_input("## 회사이름")
start_date = st.sidebar.date_input("시작 날짜", datetime.date(2024, 1, 1))
end_date = st.sidebar.date_input("종료 날짜", datetime.date(2024, 12, 31))
# 메인 화면에 입력한 값을 출력
    
button = st.sidebar.button('주가 데이터 확인')

def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, header=0, encoding='euc-kr')[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

if button:
    st.write(f'## [{user_input}] 주가 데이터')
    if user_input and start_date and end_date:
        ticker_symbol = get_ticker_symbol(user_input)  
        if ticker_symbol:
            df = fdr.DataReader(f'KRX:{ticker_symbol}', start_date, end_date).reset_index().rename(columns={'index': 'date'})
            st.write(df.head(7))
            st.write(px.line(df, x='Date', y='Close'))

            # CSV 및 Excel 다운로드 버튼을 같은 줄에 배치
            col1, col2 = st.columns(2)

            with col1:
                # CSV 다운로드 버튼 추가
                csv = convert_df_to_csv(df)
                st.download_button(
                    label="CSV로 다운로드",
                    data=csv,
                    file_name=f'{user_input}_stock_data.csv',
                    mime='text/csv',
                )

            with col2:
                # Excel 다운로드 버튼 추가
                excel = convert_df_to_excel(df)
                st.download_button(
                    label="Excel로 다운로드",
                    data=excel,
                    file_name=f'{user_input}_stock_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )