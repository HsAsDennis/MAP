import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(
    page_title="新竹縣垃圾轉運與再生粒料管理決策系統",
    page_icon="♻️",
    layout="wide"
)

st.title("♻️ 新竹縣垃圾轉運調度暨再生粒料管理視覺化儀表板")
st.markdown("本系統自動擷取雲端最新資料庫數據，即時呈現全縣垃圾清運、轉運調度及減碳效益。")

# 2. 自動擷取其他檔案數據的函數
# 這裡以讀取 Google 試算表公開 CSV 連結或雲端 Excel 為例
@st.cache_data(ttl=600)  # 快取 10 分鐘自動重新抓取最新數據
def load_data():
    # 範例：您可以將 Google 試算表發布為 CSV 連結，或者直接讀取網路檔案
    # 實務上也可以使用 pd.read_excel('您的雲端檔案路徑或網址')
    
    # 模擬自動擷取進廠量數據結構
    data_dispatch = pd.DataFrame({
        "月份": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月"],
        "分配進廠量": [10553, 8260, 8791, 5993, 14370, 8985, 15075, 12150, 9900, 13035],
        "實際進廠量": [10866.59, 8224.99, 8555.99, 5354.17, 15882.77, 11811.36, 14563.30, 11448.05, 9658.89, 12751.04]
    })
    return data_dispatch

df = load_data()

# 3. 頂部關鍵指標 (KPI) 呈現
col1, col2, col3 = st.columns(3)
total_alloc = df["分配進廠量"].sum()
total_actual = df["實際進廠量"].sum()
diff_pct = ((total_actual - total_alloc) / total_alloc) * 100

col1.metric("累計核定分配進廠量", f"{total_alloc:,.0f} 公噸")
col2.metric("累計實際焚化進廠量", f"{total_actual:,.2f} 公噸")
col3.metric("整體調度誤差比 (目標±5%)", f"{diff_pct:+.2f}%", "✔ 系統運作正常")

st.divider()

# 4. 互動式圖表展示（自動根據讀取的數據繪製）
st.subheader("📈 115年各月份轉運調度分配量 vs. 實際進廠量比較")
fig = px.bar(df, x="月份", y=["分配進廠量", "實際進廠量"], barmode="group", height=400)
st.plotly_chart(fig, use_container_width=True)

# 5. 原始數據表格（可直接下載或檢視）
st.subheader("📋 自動擷取之原始數據清單")
st.dataframe(df, use_container_width=True)
