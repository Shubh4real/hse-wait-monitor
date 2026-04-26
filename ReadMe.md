# 🏥 HSE Ireland — Wait Time Monitor

An AI-powered dashboard tracking public hospital waiting lists across Ireland using NTPF open data and Groq AI.

🔗 **Live App:** https://shubh4real-hse-wait-monitor.streamlit.app

---

## 📊 What It Does

- Tracks real waiting list data across all public hospitals in Ireland
- Shows which hospitals and specialties have the longest waits
- Breaks down wait times by band — 0–6, 6–12, 12–18, and 18+ months
- Hospital deep dive — select any hospital and see its wait band breakdown
- Search by specialty across all hospitals
- Monthly trend chart showing how waiting lists change over time
- AI executive summary powered by Groq (Llama 3.3 70B) — plain English insight from the data
- Natural language Q&A — ask questions about the data and get instant answers
- Download raw data as CSV

---

## 🤖 AI Features

Powered by **Groq API** (free tier) running **Llama 3.3 70B**:

- **AI Executive Summary** — automatically generates a concise analysis of the current waiting list situation
- **Ask the Data** — type any question and get a specific, data-driven answer
  - "Which hospital has the worst Cardiology wait?"
  - "How many patients have waited over 18 months?"
  - "What specialty needs the most urgent attention?"

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit |
| Data processing | Pandas |
| Visualisation | Plotly |
| AI insights | Groq API — Llama 3.3 70B (free) |
| Data source | NTPF Open Data (CSV) |
| Deployment | Streamlit Cloud (free) |

---

## 📁 Project Structure
