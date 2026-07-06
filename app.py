import streamlit as st
import pandas as pd
from google import genai

st.set_page_config(page_title="AQI Decision Assistant", layout="wide")

@st.cache_data
def load_data():
    hist = pd.read_csv("aqi_clean.csv", parse_dates=["datetime_ist"])
    fc = pd.read_csv("forecast_24h.csv", parse_dates=["datetime_ist"])
    return hist, fc

hist, fc = load_data()

@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_client()

CATEGORY_COLORS = {
    "Good": "#4CAF50", "Satisfactory": "#8BC34A", "Moderate": "#FFC107",
    "Poor": "#FF9800", "Very Poor": "#F44336", "Severe": "#7B1FA2"
}

st.title("🌤️ AQI Decision Assistant")
st.caption("Should you go outside? A 24-hour PM2.5 forecast and advisory for 5 Indian cities.")

cities = sorted(fc["city"].unique())
city = st.sidebar.selectbox("Choose a city", cities)

city_fc = fc[fc["city"] == city].sort_values("datetime_ist")
city_hist = hist[hist["city"] == city].sort_values("datetime_ist").tail(48)

current = city_fc.iloc[0]
color = CATEGORY_COLORS.get(current["category"], "#999")

col1, col2 = st.columns([1, 2])
with col1:
    st.markdown(f"### Right now in {city}")
    st.markdown(f"<h1 style='color:{color}'>{current['pm25_forecast']:.0f} µg/m³</h1>", unsafe_allow_html=True)
    st.markdown(f"**{current['category']}**")
    st.write(current["advice"])

with col2:
    chart_hist = city_hist[["datetime_ist", "pm25"]].rename(columns={"pm25": "Actual (past)"})
    chart_fc = city_fc[["datetime_ist", "pm25_forecast"]].rename(columns={"pm25_forecast": "Forecast (next 24h)"})
    merged = pd.merge(chart_hist, chart_fc, on="datetime_ist", how="outer").sort_values("datetime_ist")
    st.line_chart(merged.set_index("datetime_ist"))

st.divider()
st.subheader("📊 City ranking right now")
ranking = fc.sort_values("datetime_ist").groupby("city").first().reset_index().sort_values("pm25_forecast")
ranking_display = ranking[["city", "pm25_forecast", "category"]].rename(
    columns={"city": "City", "pm25_forecast": "PM2.5 (µg/m³)", "category": "Category"}
)
st.dataframe(ranking_display, hide_index=True, use_container_width=True)

st.divider()
st.subheader("💬 Ask the assistant")
question = st.text_input("Ask a question, e.g. 'Is it safe for a morning run in 2 hours?'")
if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        data_summary = city_fc.head(12)[["datetime_ist", "pm25_forecast", "category"]].to_string(index=False)
        prompt = f"""You are an air quality advisor for Indian cities. Answer using ONLY this forecast data — do not invent numbers.

City: {city}
Forecast (PM2.5 µg/m³, IST):
{data_summary}

CPCB categories: Good (0-30), Satisfactory (30-60), Moderate (60-90), Poor (90-120), Very Poor (120-250), Severe (250+).

Question: {question}

Answer in 2-4 sentences, citing specific values/times, with a clear go/wait/avoid recommendation."""
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        st.write(response.text)