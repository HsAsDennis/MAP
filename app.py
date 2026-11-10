import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 頁面基本設定
st.set_page_config(
    page_title="新竹縣垃圾轉運調度暨再生粒料管理決策系統",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { font-size: 16px; font-weight: bold; color: #047857; margin-top: 10px; }
    div[data-testid="stMetric"] { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# 2. 載入計畫完整數據模型
@st.cache_data
def load_all_data():
    # 轉運調度月度表
    df_dispatch = pd.DataFrame({
        "月份": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月"],
        "新竹縣焚化廠_分配": [10553, 8260, 8791, 5993, 8797, 5600, 9000, 6800, 4700, 8745],
        "新竹縣焚化廠_實際": [10833.79, 8224.99, 9115.85, 6287.42, 9115.05, 5658.68, 8786.91, 6617.00, 4530.64, 8457.10],
        "新竹市焚化廠_分配": [0, 0, 0, 0, 3700, 3000, 5000, 4000, 3700, 3000],
        "新竹市焚化廠_實際": [0.0, 0.0, 0.0, 0.0, 3447.70, 2989.81, 4740.30, 3644.53, 3686.69, 3007.43],
        "苗栗縣焚化廠_分配": [0, 0, 0, 0, 1873, 385, 1075, 1350, 1500, 1290],
        "苗栗縣焚化廠_實際": [0.0, 0.0, 0.0, 0.0, 1826.91, 393.36, 1036.09, 1186.52, 1441.56, 1286.51],
    })
    df_dispatch["總分配量"] = df_dispatch["新竹縣焚化廠_分配"] + df_dispatch["新竹市焚化廠_分配"] + df_dispatch["苗栗縣焚化廠_分配"]
    df_dispatch["總實際量"] = df_dispatch["新竹縣焚化廠_實際"] + df_dispatch["新竹市焚化廠_實際"] + df_dispatch["苗栗縣焚化廠_實際"]
    df_dispatch["差異量"] = df_dispatch["總實際量"] - df_dispatch["總分配量"]
    df_dispatch["差異百分比(%)"] = (df_dispatch["差異量"] / df_dispatch["總分配量"] * 100).round(2)

    # 13鄉鎮市暫置與清運量
    df_township = pd.DataFrame({
        "鄉鎮市": ["竹北市", "新豐鄉", "竹東鎮", "湖口鄉", "新埔鎮", "關西鎮", "橫山鄉", "峨眉鄉", "尖石鄉", "芎林鄉", "寶山鄉", "北埔鄉", "五峰鄉", "環保局"],
        "每日清運量(公噸)": [121.86, 37.45, 57.08, 51.17, 17.94, 13.00, 5.68, 2.42, 3.70, 11.23, 5.59, 4.61, 0.73, 0.71],
        "累積暫置量(公噸)": [176624, 53394, 0, 1972, 0, 0, 1364, 4380, 0, 0, 0, 0, 0, 0],
        "清除優先順位": ["第六順位", "第六順位", "第三順位", "第三順位", "第四順位", "第二順位", "第五順位", "第五順位", "第二順位", "第一順位", "第一順位", "第一順位", "第一順位", "第一順位"]
    })

    # 再生粒料歷史與減碳
    df_agg = pd.DataFrame({
        "年度": ["111年", "112年", "113年", "114年", "115年(1-10月)"],
        "使用量(公噸)": [9255.0, 12861.0, 12485.0, 9203.0, 11351.63],
        "減碳量(公噸CO2e)": [126.8, 176.2, 171.0, 126.1, 155.52]
    })

    # 底渣飛灰回運
    df_ash = pd.DataFrame({
        "焚化廠": ["新竹縣焚化廠", "新竹市焚化廠", "苗栗竹南焚化廠"],
        "底渣已回運": [2440.53, 982.12, 0.0],
        "底渣未回運": [3448.67, 2584.32, 0.0],
        "飛灰已回運": [1901.52, 587.22, 298.92],
        "飛灰未回運": [0.0, 559.44, 131.71]
    })

    return df_dispatch, df_township, df_agg, df_ash

df_dispatch, df_township, df_agg, df_ash = load_all_data()

# ==========================================
# 側邊欄導航
# ==========================================
with st.sidebar:
    st.markdown("### ♻️ 新竹縣環保局決策中心")
    st.caption("116年度新竹縣垃圾轉運及焚化底渣監督稽查暨效能評估計畫")
    st.divider()
    
    selected_tab = st.radio(
        "選擇功能模組：",
        [
            "📊 1. 垃圾轉運調度與 ±5% 誤差監控",
            "🗺️ 2. 各鄉鎮暫置量能與排班試算模擬",
            "🏗️ 3. 底渣再生粒料流向與淨零減碳效益",
            "🔍 4. 垃圾分類查核與 4+16 次性質分析"
        ]
    )
    st.divider()
    st.info("💡 **系統特色**：\n串接雲端數據與即時圖表，支援手機與電腦跨裝置瀏覽。")
    st.caption("執行單位：富聯工程顧問股份有限公司")

# ==========================================
# 頂部全域 KPI 指標 (四大核心)
# ==========================================
st.markdown('<div class="main-header">♻️ 新竹縣垃圾轉運調度暨再生粒料管理決策儀表板</div>', unsafe_allow_html=True)
st.caption("統計基準：115年1月至10月實績數據同步更新")

k1, k2, k3, k4, k5, k6 = st.columns(6)
total_alloc = df_dispatch["總分配量"].sum()
total_actual = df_dispatch["總實際量"].sum()
overall_diff = ((total_actual - total_alloc) / total_alloc) * 100

k1.metric("累計分配進廠量", f"{total_alloc:,.0f} 噸", "三廠合計配額")
k2.metric("累計實際進廠量", f"{total_actual:,.2f} 噸", f"{total_actual - total_alloc:+,.2f} 噸")
k3.metric("整體調度誤差比", f"{overall_diff:+.2f}%", "✔ 符合 ±5% 控管")
k4.metric("全縣累積暫置量", "237,734 噸", "▼ 已去化 13,421 噸")
k5.metric("115年再生粒料", "11,351.63 噸", "核發 5 件工程管編")
k6.metric("累計減碳貢獻", "755.63 噸", "111-115年總計")

st.divider()

# ==========================================
# 模組 1：垃圾轉運調度與誤差監控
# ==========================================
if "📊 1" in selected_tab:
    st.markdown('<div class="sub-header">📊 1. 垃圾轉運調度與 ±5% 誤差即時監控中心</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("📈 三座焚化廠每月分配量 vs. 實際進廠量堆疊圖")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_dispatch["月份"], y=df_dispatch["新竹縣焚化廠_實際"], name="新竹縣焚化廠(實際)", marker_color="#2563EB"))
        fig_bar.add_trace(go.Bar(x=df_dispatch["月份"], y=df_dispatch["新竹市焚化廠_實際"], name="新竹市焚化廠(實際)", marker_color="#10B981"))
        fig_bar.add_trace(go.Bar(x=df_dispatch["月份"], y=df_dispatch["苗栗縣焚化廠_實際"], name="苗栗縣焚化廠(實際)", marker_color="#F59E0B"))
        fig_bar.add_trace(go.Scatter(x=df_dispatch["月份"], y=df_dispatch["總分配量"], name="核定總分配量(目標線)", mode="lines+markers", line=dict(color="#DC2626", width=3, dash="dash")))
        fig_bar.update_layout(barmode="stack", height=380, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🎯 月度調度誤差率控管圖 (±5% 警戒線)")
        colors = ["#EF4444" if abs(v) > 5.0 else "#10B981" for v in df_dispatch["差異百分比(%)"]]
        fig_err = go.Figure(data=[go.Bar(x=df_dispatch["月份"], y=df_dispatch["差異百分比(%)"], marker_color=colors, text=[f"{v:+.2f}%" for v in df_dispatch["差異百分比(%)"]], textposition="outside")])
        fig_err.add_hline(y=5.0, line_dash="dot", line_color="red", annotation_text="+5% 上限")
        fig_err.add_hline(y=-5.0, line_dash="dot", line_color="red", annotation_text="-5% 下限")
        fig_err.update_layout(height=380, yaxis_range=[-12, 10], margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_err, use_container_width=True)

    st.subheader("📋 115年度轉運調度進廠量差異彙整總表 (表 3.1-3)")
    st.dataframe(df_dispatch, use_container_width=True)

# ==========================================
# 模組 2：各鄉鎮暫置量能與排班試算模擬
# ==========================================
elif "🗺️ 2" in selected_tab:
    st.markdown('<div class="sub-header">🗺️ 2. 13鄉鎮市垃圾清運量、暫置負荷與每週四排班模擬器</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("🚛 各鄉鎮市每日平均垃圾清運量占比 (總計 333.17 公噸/日)")
        fig_pie = px.pie(df_township, values="每日清運量(公噸)", names="鄉鎮市", hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("⛰️ 轄內暫置場累積堆置量分布 (總計 237,734 公噸)")
        df_stored = df_township[df_township["累積暫置量(公噸)"] > 0]
        fig_store = px.bar(df_stored, x="鄉鎮市", y="累積暫置量(公噸)", color="清除優先順位", text_auto=",.0f", color_discrete_sequence=["#DC2626", "#F59E0B", "#2563EB"])
        fig_store.update_layout(height=360, yaxis_type="log", yaxis_title="累積暫置量 (公噸 - 對數尺度)", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_store, use_container_width=True)

    st.divider()
    st.subheader("⚙️ 每週四排班配額動態試算模擬器 (歲修應變決策)")
    sc1, sc2, sc3 = st.columns(3)
    q_hc = sc1.slider("新竹縣焚化廠下週配額 (公噸/週)", 1000, 2500, 1800, 50)
    q_ml = sc2.slider("苗栗竹南焚化廠下週配額 (公噸/週)", 0, 600, 300, 25)
    q_em = sc3.slider("緊急委外轉運配額 (公噸/週)", 0, 1000, 200, 50)

    total_q = q_hc + q_ml + q_em
    gen_weekly = 333.17 * 6
    net_dep = total_q - gen_weekly

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("下週可用焚化總額度", f"{total_q:,.0f} 公噸")
    mc2.metric("預估全縣新產出清運量", f"{gen_weekly:,.2f} 公噸", "保障第一順位 5 鄉鎮優先")
    if net_dep >= 0:
        mc3.metric("預計淨去化暫置垃圾", f"+{net_dep:,.2f} 公噸/週", "✔ 達成當週暫置當週清運", delta_color="normal")
    else:
        mc3.metric("預估本週需緊急暫置量", f"{net_dep:,.2f} 公噸/週", "⚠️ 建議啟動表3.1-5緊急互助", delta_color="inverse")

# ==========================================
# 模組 3：底渣再生粒料流向與淨零減碳效益
# ==========================================
elif "🏗️ 3" in selected_tab:
    st.markdown('<div class="sub-header">🏗️ 3. 焚化再生粒料流向管理暨淨零減碳效益追蹤</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.subheader("🌱 111~115年再生粒料去化量與減碳雙軸趨勢 (圖 3.10-1)")
        fig_agg = go.Figure()
        fig_agg.add_trace(go.Bar(x=df_agg["年度"], y=df_agg["使用量(公噸)"], name="再生粒料使用量(公噸)", marker_color="#10B981", text=df_agg["使用量(公噸)"], textposition="auto"))
        fig_agg.add_trace(go.Scatter(x=df_agg["年度"], y=df_agg["減碳量(公噸CO2e)"], name="減碳量(公噸CO2e)", yaxis="y2", mode="lines+markers+text", text=[f"{v}噸" for v in df_agg["減碳量(公噸CO2e)"]], textposition="top center", line=dict(color="#1D4ED8", width=3)))
        fig_agg.update_layout(height=380, yaxis=dict(title="使用量 (公噸)"), yaxis2=dict(title="減碳量 (公噸 CO2e)", overlaying="y", side="right", range=[0, 220]), legend=dict(orientation="h", y=1.12), margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_agg, use_container_width=True)

    with col_b:
        st.subheader("🔄 三座焚化廠底渣與飛灰回運進度 (表 3.7-6~7)")
        fig_ash = go.Figure(data=[
            go.Bar(name='底渣已回運', x=df_ash["焚化廠"], y=df_ash["底渣已回運"], marker_color='#2563EB'),
            go.Bar(name='底渣未回運', x=df_ash["焚化廠"], y=df_ash["底渣未回運"], marker_color='#93C5FD'),
            go.Bar(name='飛灰已回運', x=df_ash["焚化廠"], y=df_ash["飛灰已回運"], marker_color='#D97706'),
            go.Bar(name='飛灰未回運', x=df_ash["焚化廠"], y=df_ash["飛灰未回運"], marker_color='#FDE68A')
        ])
        fig_ash.update_layout(barmode='group', height=380, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig_ash, use_container_width=True)

# ==========================================
# 模組 4：分類查核與性質分析
# ==========================================
elif "🔍 4" in selected_tab:
    st.markdown('<div class="sub-header">🔍 4. 垃圾分類落地檢查與 4+16次性質組成分析監控</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("♻️ 焚化廠末端落地檢查夾雜資收物占比 (451件)")
        df_rec = pd.DataFrame({
            "資收物類別": ["紙容器", "其他塑膠", "寶特瓶", "鋁箔包", "廚餘", "鋁類", "軟塑膠", "鐵類", "玻璃類"],
            "件數": [161, 87, 50, 39, 24, 23, 22, 19, 18]
        })
        fig_rec = px.bar(df_rec, x="件數", y="資收物類別", orientation="h", text_auto=True, color_discrete_sequence=["#0D9488"])
        fig_rec.update_layout(height=360, yaxis={'categoryorder':'total ascending'}, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_rec, use_container_width=True)

    with c2:
        st.subheader("🧪 本縣垃圾性質分析與全國平均對比")
        df_comp = pd.DataFrame({
            "組成項目": ["紙類 (%)", "塑膠類 (%)", "廚餘類 (%)"],
            "新竹縣115年前三季": [36.04, 22.47, 26.45],
            "全國114年平均": [40.85, 26.52, 16.40]
        })
        fig_comp = px.bar(df_comp, x="組成項目", y=["新竹縣115年前三季", "N/A 全國平均"], barmode="group", color_discrete_sequence=["#2563EB", "#94A3B8"])
        fig_comp.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_comp, use_container_width=True)
