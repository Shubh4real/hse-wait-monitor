"""
ai_insights.py
Groq AI layer — free, fast inference.
Built by Shubham Ravi
"""

import requests

GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # free, fast, high quality


def _build_prompt(data_summary, question=None):
    if question:
        return f"""You are a healthcare data analyst for Ireland's HSE waiting list system.
Answer the following question based on the data provided.
Be specific, cite numbers, and keep the answer under 80 words.

Data:
{data_summary}

Question: {question}"""

    return f"""You are a senior healthcare data analyst reviewing Ireland's HSE hospital waiting list data.

Write a concise executive summary (4-5 sentences, under 120 words) that:
- States the overall scale of the waiting list crisis
- Highlights the most concerning hospital or specialty
- Mentions how many patients have waited over 18 months
- Gives one clear, actionable observation for policymakers

Be direct, factual, and neutral. No bullet points. No headings.

Data:
{data_summary}"""


def _call_groq(prompt, api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    response = requests.post(
        GROQ_URL,
        headers=headers,
        json=body,
        timeout=30
    )
    if response.status_code == 401:
        return "⚠️ Invalid API key — check your Groq API key at console.groq.com."
    if response.status_code == 429:
        return "⏳ Rate limit reached — please wait a moment and try again."
    if response.status_code == 400:
        error_detail = response.json().get("error", {}).get("message", "Unknown error")
        return f"⚠️ Bad request: {error_detail}"
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def get_ai_insight(data_summary, api_key):
    try:
        prompt = _build_prompt(data_summary)
        return _call_groq(prompt, api_key)
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out — please try again."
    except Exception as e:
        return f"⚠️ AI insight unavailable: {str(e)}"


def ask_question(data_summary, question, api_key):
    try:
        prompt = _build_prompt(data_summary, question)
        return _call_groq(prompt, api_key)
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out — please try again."
    except Exception as e:
        return f"⚠️ Could not get answer: {str(e)}"


def build_data_summary(summary, worst_hospitals, worst_specialties):
    lines = [
        f"Total patients waiting: {summary.get('total_waiting', 0):,}",
        f"Hospitals tracked: {summary.get('hospitals', 0)}",
        f"Specialties tracked: {summary.get('specialties', 0)}",
        f"Patients waiting over 18 months: {summary.get('over_18_months', 0):,}",
        "",
        "Top 5 hospitals by waiting list size:",
    ]
    if not worst_hospitals.empty:
        for _, row in worst_hospitals.head(5).iterrows():
            lines.append(f"  - {row['Hospital']}: {int(row['Total']):,} patients")
    lines.append("")
    lines.append("Top 5 specialties by waiting list size:")
    if not worst_specialties.empty:
        for _, row in worst_specialties.head(5).iterrows():
            lines.append(f"  - {row['Specialty']}: {int(row['Total']):,} patients")
    return "\n".join(lines)