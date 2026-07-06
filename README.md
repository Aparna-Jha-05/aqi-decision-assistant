# AQI Decision Assistant

**Should you go outside?** A 24-hour PM2.5 forecast and plain-language air quality advisory for 5 major Indian cities.

Built for the **Gen AI Academy (APAC Edition)** hackathon — problem statement: *AI for Better Living and Smarter Communities*.

**Live app:** https://aqi-decision-assistant.streamlit.app/ 
**Demo video:** https://drive.google.com/file/d/1xHNDFitgHrleDw1bHnf9WYOpZREDVK5m/view?usp=sharing 

---

## The problem

Millions of people in Indian cities check an air quality number every day, but a raw number does not help anyone make a decision. Is 57 bad? Can my child play outside? Should I run now or wait?

People do not need more data. They need a decision.

## What it does

The AQI Decision Assistant turns live air quality data into a clear **go / wait / avoid** recommendation. For 5 cities (Jaipur, Delhi, Mumbai, Bengaluru, Kolkata), it:

- Shows the **current PM2.5 level**, its CPCB health category, and plain advice on outdoor activity
- Forecasts the **next 24 hours** using a trained machine-learning model
- Plots the **past 48 hours of actual data alongside the forecast** in one chart
- **Ranks all 5 cities** live so you can compare at a glance
- Answers **plain-language questions** ("Is it safe for an evening walk?") with a grounded, data-backed reply powered by Gemini

## Who it is for

Parents deciding whether to send a child outside, runners planning a workout, people with asthma or other respiratory conditions, and city stakeholders comparing area-wise risk.

---

## How it works

```
OpenAQ API  ->  Clean (pandas)  ->  Store (BigQuery)  ->  Forecast (Random Forest)
            ->  Classify (CPCB categories)  ->  Explain (Gemini)  ->  Serve (Streamlit)
```

1. **Ingest** — Live and historical PM2.5 data is pulled from the OpenAQ API for one active government monitoring station per city.
2. **Clean** — Data is deduplicated, validated, converted to IST, and gap-checked in pandas.
3. **Store** — The cleaned history and the forecast are loaded into Google BigQuery for scalable storage and fast SQL analytics.
4. **Forecast** — A Random Forest model uses cyclical time features (hour, day-of-week) and lag features (1h, 24h, 6h rolling mean) to predict PM2.5. Forecasts run recursively to project 24 hours ahead.
5. **Classify** — Each value is mapped to an official CPCB health category (Good / Satisfactory / Moderate / Poor / Very Poor / Severe) with activity-specific advice.
6. **Explain** — The Gemini API answers natural-language questions, grounded strictly in the real forecast numbers so it does not hallucinate.
7. **Serve** — A Streamlit app presents the dashboard, chart, ranking, and assistant, deployed on Streamlit Community Cloud.

## Model performance

The forecast model achieves a **test MAE of 7.2 µg/m³** on a chronological (time-based) hold-out split, evaluated on roughly 1,400 held-out hourly points.

---

## Tech stack

| Layer | Technology |
|---|---|
| Data source | OpenAQ API (live + historical PM2.5) |
| Storage & analytics | Google BigQuery |
| Forecasting | scikit-learn (Random Forest) |
| Natural language | Google Gemini API |
| App & deployment | Streamlit / Streamlit Community Cloud |
| Pipeline | Python, pandas, Google Colab |

**Google Cloud services used:** BigQuery and Gemini API.

---

## Repository structure

```
.
├── app.py                 # Streamlit app (dashboard, chart, ranking, assistant)
├── requirements.txt       # Python dependencies
├── aqi_clean.csv          # Cleaned historical PM2.5 data (served by the app)
├── forecast_24h.csv       # 24-hour forecast per city (served by the app)
├── aqi_decision_assistant.ipynb   # Full pipeline: ingest, clean, BigQuery load, model, forecast
└── README.md
```

The app serves from the cached CSV snapshots for speed and reliability. The notebook is the full reproducible pipeline, including the BigQuery load and model training.

---

## Running locally

```bash
git clone https://github.com/<YOUR_USERNAME>/aqi-decision-assistant.git
cd aqi-decision-assistant
pip install -r requirements.txt
streamlit run app.py
```

The app needs a Gemini API key. Locally, add it to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_key_here"
```

To regenerate the data and forecasts, open `aqi_decision_assistant.ipynb` in Google Colab and add `OPENAQ_API_KEY` and `GEMINI_API_KEY` as Colab secrets, then run all cells.

---

## Data & disclaimer

Air quality data is sourced from [OpenAQ](https://openaq.org), which aggregates readings from public government monitoring stations. Coverage per station is real and can be uneven (short reporting gaps are normal). Forecasts are model estimates for informational purposes and are not a substitute for official government air quality advisories or medical advice.

---

## Acknowledgements

Built for the Gen AI Academy (APAC Edition) hackathon. Air quality data by OpenAQ. Health categories based on the Central Pollution Control Board (CPCB) National Air Quality Index standard.
