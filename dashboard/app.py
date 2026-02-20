import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
import uuid

# ---------------------------------------------------------
# 1. SAYFA VE STİL AYARLARI (ULTIMATE DARK MODE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DAG Command Center",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS STİLLERİ ---
st.markdown("""
    <style>
        .stApp { background-color: #050505; }

        /* Kartlar */
        div[data-testid="stMetric"] {
            background-color: #111;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
        }

        /* Tablo Başlıkları */
        thead tr th:first-child {display:none}
        tbody th {display:none}

        h1, h2, h3 { font-family: 'Courier New', monospace; color: #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. VERİ ÇEKME İŞLEMLERİ
# ---------------------------------------------------------
API_URL = "http://web:8000/api/v1/logs/"


def fetch_data():
    try:
        response = requests.get(API_URL, params={"limit": 100})
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


# ---------------------------------------------------------
# 3. GRAFİK OLUŞTURUCULAR
# ---------------------------------------------------------

def create_gauge_chart(value, title, color, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 20, 'color': color}},
        number={'font': {'color': "white"}},
        gauge={
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#333"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "#111",
            'borderwidth': 0,
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 1, 'value': max_val * 0.9}
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=200,
                      margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_radar_chart(cpu, mem, anomaly_score):
    score_scaled = min(abs(anomaly_score) * 100, 100)
    categories = ['CPU', 'RAM', 'Risk', 'IO', 'Net']
    values = [cpu, mem, score_scaled, (cpu + mem) / 2, (cpu + 20) % 100]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself', fillcolor='rgba(0, 212, 255, 0.2)',
        line_color='#00d4ff', marker=dict(size=5)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], linecolor="#333", gridcolor="#222"),
                   bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=300, margin=dict(l=40, r=40, t=20, b=20),
        showlegend=False
    )
    return fig


# ---------------------------------------------------------
# 4. ANA DÖNGÜ
# ---------------------------------------------------------
st.title("🌌 DAG MERKEZİ İZLEME SİSTEMİ")
placeholder = st.empty()

while True:
    uid = str(uuid.uuid4())[:8]
    raw_data = fetch_data()
    df = pd.DataFrame(raw_data)

    with placeholder.container():
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            last_log = df.iloc[0]

            # --- DURUM BAR ---
            status_color = "#ff0000" if last_log['is_anomaly'] or last_log['level'] == "ERROR" else "#00ff00"
            status_text = "KRİTİK UYARI" if status_color == "#ff0000" else "SİSTEM NORMAL"

            st.markdown(f"""
            <div style="background-color: {status_color}22; padding: 10px; border-left: 5px solid {status_color}; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="margin:0; color: {status_color};">DURUM: {status_text} | HOST: {last_log['host']} | SERVİS: {last_log['service']}</h3>
            </div>
            """, unsafe_allow_html=True)

            # --- ROW 1: METRİKLER ---
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
            with col1:
                st.plotly_chart(create_gauge_chart(last_log['cpu_usage'], "CPU", "#00d4ff"), use_container_width=True,
                                key=f"g1_{uid}")
            with col2:
                st.plotly_chart(create_gauge_chart(last_log['memory_usage'], "RAM", "#d900ff"),
                                use_container_width=True, key=f"g2_{uid}")
            with col3:
                st.plotly_chart(create_gauge_chart(abs(last_log['anomaly_score']) * 100, "RİSK", "#ff2b2b"),
                                use_container_width=True, key=f"g3_{uid}")
            with col4:
                st.plotly_chart(
                    create_radar_chart(last_log['cpu_usage'], last_log['memory_usage'], last_log['anomaly_score']),
                    use_container_width=True, key=f"radar_{uid}")

            st.markdown("---")

            # --- ROW 2: GRAFİKLER ---
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("#### 📉 KAYNAK TÜKETİMİ")
                fig_area = px.area(df, x='timestamp', y=['cpu_usage', 'memory_usage'],
                                   color_discrete_map={'cpu_usage': '#00d4ff', 'memory_usage': '#d900ff'},
                                   template="plotly_dark")
                fig_area.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
                st.plotly_chart(fig_area, use_container_width=True, key=f"area_{uid}")

            with c2:
                st.markdown("#### 🔴 ANOMALİ HARİTASI")
                df['size'] = df['is_anomaly'].map({True: 20, False: 6})
                fig_scatter = px.scatter(df, x='cpu_usage', y='memory_usage', color='is_anomaly',
                                         color_discrete_map={True: 'red', False: '#0044ff'}, size='size',
                                         template="plotly_dark")
                fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
                st.plotly_chart(fig_scatter, use_container_width=True, key=f"sc_{uid}")

            # --- ROW 3: GELİŞMİŞ TABLO (Burayı Güzelleştirdik) ---
            st.markdown("#### 📝 CANLI LOG AKIŞI")

            # 1. Veriyi Güzelleştirme
            display_df = df.copy()
            # Tarihi sadeleştir (Sadece Saat)
            display_df['Zaman'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
            # Anomaliyi İkona Çevir
            display_df['Durum'] = display_df['is_anomaly'].apply(lambda x: "🚨 ANOMALİ" if x else "🟢 NORMAL")

            # Sadece istediğimiz sütunları alalım ve yeniden isimlendirelim
            display_df = display_df[
                ['Zaman', 'host', 'service', 'level', 'message', 'cpu_usage', 'Durum', 'is_anomaly']]


            # Renklendirme Fonksiyonu
            def style_table(row):
                if row['is_anomaly']:  # Gerçek mantıksal değer
                    return ['background-color: rgba(255, 0, 0, 0.25); color: #ffcccc'] * len(row)
                if row['level'] == 'ERROR':
                    return ['background-color: rgba(255, 165, 0, 0.25); color: #ffebcc'] * len(row)
                return ['color: #e0e0e0'] * len(row)


            # Streamlit Column Config ile Profesyonel Görünüm
            st.dataframe(
                display_df.style.apply(style_table, axis=1),
                column_config={
                    "Zaman": st.column_config.TextColumn("Saat", width="small"),
                    "host": st.column_config.TextColumn("Sunucu", width="medium"),
                    "service": st.column_config.TextColumn("Servis", width="medium"),
                    "level": st.column_config.TextColumn("Seviye", width="small"),
                    "message": st.column_config.TextColumn("Log Mesajı", width="large"),
                    "cpu_usage": st.column_config.ProgressColumn(
                        "İşlemci (%)",
                        format="%.1f%%",  # Virgülden sonra 1 basamak
                        min_value=0,
                        max_value=100,
                    ),
                    "Durum": st.column_config.TextColumn("Analiz Sonucu", width="medium"),
                    "is_anomaly": None  # Bu sütunu gizle (sadece renklendirme için kullandık)
                },
                use_container_width=True,
                height=400,
                key=f"tab_{uid}",
                hide_index=True  # Sol baştaki 0,1,2 indeksini gizle
            )

        else:
            st.warning("📡 Sinyal Bekleniyor... (Log Shipper'ı kontrol edin)")

    time.sleep(1)