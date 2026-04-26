"""
app.py
HSE Ireland Wait Time Monitor
AI-powered dashboard using NTPF open data + Groq AI
Built by Shubham Ravi
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import (
    load_data, get_summary, get_worst_hospitals,
    get_worst_specialties, get_hospital_breakdown,
    get_wait_band_totals, get_specialty_hospital_pivot,
    get_trend_data,
)
from ai_insights import get_ai_insight, ask_question, build_data_summary

st.set_page_config(
    page_title="HSE Wait Time Monitor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1d2e, #212435);
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stSidebar"] {
        background-color: #13151f;
        border-right: 1px solid #2e3250;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #7eb8f7;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 1.5rem 0 0.5rem 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #2e3250;
    }
    .ai-box {
        background: linear-gradient(135deg, #0d1f3c, #112040);
        border: 1px solid #1e4080;
        border-left: 4px solid #4a9eff;
        border-radius: 10px;
        padding: 20px 24px;
        color: #c8deff;
        font-size: 0.97rem;
        line-height: 1.7;
        margin: 1rem 0;
    }
    .chat-user {
        background: #1e2d4a;
        border-radius: 12px 12px 4px 12px;
        padding: 10px 16px;
        margin: 8px 0;
        color: #d0e8ff;
        font-size: 0.9rem;
        text-align: right;
    }
    .chat-ai {
        background: #1a1f30;
        border: 1px solid #2e3250;
        border-radius: 12px 12px 12px 4px;
        padding: 10px 16px;
        margin: 8px 0;
        color: #b8cce8;
        font-size: 0.9rem;
    }
    .stat-pill {
        display: inline-block;
        background: #1a2640;
        border: 1px solid #2a4070;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: #7eb8f7;
        margin: 2px 0 12px 0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🏥 HSE Wait Monitor")
    st.caption("Powered by NTPF Open Data + Groq AI")
    st.divider()
    groq_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        placeholder="Paste your Groq API key",
        help="Get a free key at console.groq.com"
    )
    st.divider()
    list_type = st.radio(
        "📋 Waiting List Type",
        ["outpatient", "inpatient"],
        format_func=lambda x: "🏠 Outpatient" if x == "outpatient" else "🛏️ Inpatient/Day Case"
    )
    top_n = st.slider("Top N results", 5, 20, 10)
    st.divider()
    st.caption("Data: NTPF Ireland · Updated monthly")
    st.caption("Built by Shubham Ravi")

# ── HEADER ──
st.markdown("""
<div style='padding: 1rem 0 0.5rem 0;'>
    <h1 style='color:#7eb8f7; font-size:2rem; margin:0;'>
        🏥 HSE Ireland — Waiting List Monitor
    </h1>
    <p style='color:#6b7a9e; margin:0.3rem 0 0 0; font-size:0.95rem;'>
        Real-time tracking of public hospital waiting lists · Data: NTPF Open Data
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── LOAD DATA ──
with st.spinner("⏳ Loading latest NTPF data..."):
    df = load_data(list_type)

if df is None or df.empty:
    st.error("❌ Could not load data. Check your data folder and file names.")
    st.stop()

summary           = get_summary(df)
worst_hospitals   = get_worst_hospitals(df, top_n)
worst_specialties = get_worst_specialties(df, top_n)
wait_bands        = get_wait_band_totals(df)
data_summary      = build_data_summary(summary, worst_hospitals, worst_specialties)

# ── METRICS ──
c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Total Waiting",      f"{summary['total_waiting']:,}")
c2.metric("🏨 Hospitals",          summary['hospitals'])
c3.metric("🔬 Specialties",        summary['specialties'])
c4.metric("⏰ Waiting 18+ Months", f"{summary['over_18_months']:,}")

st.divider()

# ── AI SUMMARY ──
st.markdown('<div class="section-header">🤖 AI Executive Summary</div>', unsafe_allow_html=True)
if groq_key:
    with st.spinner("Generating AI insight..."):
        insight = get_ai_insight(data_summary, groq_key)
    st.markdown(f'<div class="ai-box">{insight}</div>', unsafe_allow_html=True)
else:
    st.info("💡 Add your free Groq API key in the sidebar to enable AI insights. Get one at console.groq.com")

st.divider()

# ── HOSPITALS + WAIT BANDS ──
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="section-header">🏨 Hospitals with Longest Waiting Lists</div>', unsafe_allow_html=True)
    if not worst_hospitals.empty:
        fig = px.bar(
            worst_hospitals, x="Total", y="Hospital", orientation="h",
            color="Total", color_continuous_scale="Blues",
            labels={"Total": "Patients Waiting", "Hospital": ""}
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#a0aec0", coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis={"categoryorder": "total ascending"},
            xaxis=dict(gridcolor="#2e3250")
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown('<div class="section-header">⏱️ Wait Time Bands</div>', unsafe_allow_html=True)
    if not wait_bands.empty:
        colors = ["#4a9eff", "#f6ad55", "#fc8181", "#e53e3e"]
        fig2 = go.Figure(go.Pie(
            labels=wait_bands["Wait Band"],
            values=wait_bands["Patients"],
            hole=0.55,
            marker_colors=colors[:len(wait_bands)],
            textinfo="label+percent",
            textfont_color="#a0aec0",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#a0aec0", showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            annotations=[dict(
                text=f"{summary['total_waiting']:,}<br>total",
                x=0.5, y=0.5, font_size=13,
                font_color="#7eb8f7", showarrow=False
            )]
        )
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── SPECIALTIES ──
st.markdown('<div class="section-header">🔬 Specialties with Longest Waiting Lists</div>', unsafe_allow_html=True)
if not worst_specialties.empty:
    fig3 = px.bar(
        worst_specialties, x="Specialty", y="Total",
        color="Total", color_continuous_scale="Reds",
        labels={"Total": "Patients Waiting", "Specialty": ""}
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#a0aec0", coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(tickangle=-30),
        yaxis=dict(gridcolor="#2e3250")
    )
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No specialty data available for this list type.")

st.divider()

# ── HOSPITAL DEEP DIVE ──
st.markdown('<div class="section-header">🔍 Hospital Deep Dive</div>', unsafe_allow_html=True)
if "Hospital" in df.columns:
    hosp_only = df[df["_source"] == "hospital"] if "_source" in df.columns else df
    hospitals = sorted(hosp_only["Hospital"].dropna().unique().tolist())
    selected_hospital = st.selectbox("Select a hospital", hospitals)
    breakdown = get_hospital_breakdown(df, selected_hospital)

    if not breakdown.empty:
        total_row = hosp_only[hosp_only["Hospital"] == selected_hospital]["Total"].sum()
        st.markdown(
            f'<span class="stat-pill">Total waiting: {int(total_row):,}</span>',
            unsafe_allow_html=True
        )
        fig4 = px.bar(
            breakdown, x="Patients", y="Wait Band", orientation="h",
            color="Patients", color_continuous_scale="Greens",
            labels={"Patients": "Patients Waiting", "Wait Band": ""}
        )
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#a0aec0", coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis={"categoryorder": "total ascending"},
            xaxis=dict(gridcolor="#2e3250")
        )
        fig4.update_traces(marker_line_width=0)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No breakdown data available for this hospital.")

st.divider()

# ── SPECIALTY SEARCH ──
# ── SPECIALTY SEARCH ──
st.markdown('<div class="section-header">🔎 Search by Specialty</div>', unsafe_allow_html=True)
specialty_query = st.text_input(
    "Type a specialty (e.g. Cardiology, Dermatology, Orthopaedics)"
)
if specialty_query:
    result = get_specialty_hospital_pivot(df, specialty_query)
    if not result.empty:
        # Check what columns we got back
        y_col = "Category" if "Category" in result.columns else "Hospital"
        x_col = "Total" if "Total" in result.columns else "Patients"

        total_val = int(result[x_col].sum())
        st.markdown(
            f'<span class="stat-pill">National total for {specialty_query}: {total_val:,} patients</span>',
            unsafe_allow_html=True
        )
        fig5 = px.bar(
            result, x=x_col, y=y_col, orientation="h",
            color=x_col, color_continuous_scale="Purples",
            labels={x_col: "Patients Waiting", y_col: ""}
        )
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#a0aec0", coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis={"categoryorder": "total ascending"},
            xaxis=dict(gridcolor="#2e3250"),
        )
        fig5.update_traces(marker_line_width=0)
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning(f"No results found for '{specialty_query}' — try Cardio-Thoracic Surgery, Dermatology, or Orthopaedics")

# ── MONTHLY TREND ──
st.markdown('<div class="section-header">📈 Monthly Trend</div>', unsafe_allow_html=True)
trend = get_trend_data(list_type)
if not trend.empty and len(trend) > 1:
    fig6 = px.line(
        trend, x="ArchiveDate", y="Total",
        labels={"ArchiveDate": "Month", "Total": "Total Patients Waiting"},
        markers=True,
        color_discrete_sequence=["#4a9eff"]
    )
    fig6.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#a0aec0",
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor="#2e3250"),
        yaxis=dict(gridcolor="#2e3250"),
    )
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("📊 Add more monthly CSV files to the data folder to see trends over time.")

st.divider()

# ── AI Q&A CHAT ──
st.markdown('<div class="section-header">💬 Ask the Data</div>', unsafe_allow_html=True)
if groq_key:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for turn in st.session_state.chat_history:
        st.markdown(f'<div class="chat-user">🧑 {turn["q"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai">🤖 {turn["a"]}</div>', unsafe_allow_html=True)
    user_q = st.text_input(
        "Ask anything about the data",
        placeholder="e.g. Which hospital has the worst Dermatology wait?",
        key="chat_input"
    )
    col_ask, col_clear = st.columns([5, 1])
    with col_ask:
        if st.button("Ask →", use_container_width=True) and user_q:
            with st.spinner("Thinking..."):
                answer = ask_question(data_summary, user_q, groq_key)
            st.session_state.chat_history.append({"q": user_q, "a": answer})
            st.rerun()
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
else:
    st.info("💡 Add your Groq API key in the sidebar to enable Q&A chat.")

st.divider()

# ── RAW DATA ──
with st.expander("📄 View Raw Data"):
    st.dataframe(df, use_container_width=True, height=400)
    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️ Download CSV", data=csv,
        file_name=f"ntpf_{list_type}_waiting_list.csv",
        mime="text/csv"
    )

# ── FOOTER ──
st.markdown("""
<div style='text-align:center; color:#3a4a6a; font-size:0.8rem; padding: 2rem 0 1rem 0;'>
    Built by <strong style='color:#4a6a9e'>Shubham Ravi</strong> ·
    Data: <a href='https://www.ntpf.ie' style='color:#4a6a9e'>NTPF Ireland</a> ·
    <a href='https://github.com/Shubh4real' style='color:#4a6a9e'>GitHub</a>
</div>
""", unsafe_allow_html=True)