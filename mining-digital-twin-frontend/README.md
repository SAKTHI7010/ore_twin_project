# Ore Beneficiation Digital Twin — Frontend

Streamlit frontend for the **Ore Beneficiation Plant Digital Twin**.

## Tech Stack
- **Streamlit** — multi-page app
- **Plotly** — charts (pie, bar, waterfall, Sankey, gauge, trends)
- **Three.js** — 3D interactive plant visualization
- **Requests** — backend API calls via `services/api_client.py`

## Pages

| Page | Description |
|------|-------------|
| 🏠 Home | Plant overview, KPIs, 2D flowsheet, alarms |
| 🌐 3D Digital Twin | Three.js 3D visualization with live equipment states |
| ⚙️ Equipment Details | Per-equipment status, parameters, I/O streams |
| 🌊 Streams | Stream mass flows, water flows, solids % |
| 🔬 Simulation | Input controls, run simulation, Sankey mass balance |
| 📈 Analytics | Trends, mass balance waterfall, water balance |
| 🎯 Optimization | Advisory recommendations (clearly labeled DEMO) |
| 📡 Data Quality | Quality gauge, stream freshness |
| 📖 About | Architecture, process topology, assumptions |

## Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env
# Edit: BACKEND_BASE_URL=http://localhost:8000

# 4. Start backend first (separate terminal)
# cd ../mining-digital-twin-backend && uvicorn app.main:app --port 8000

# 5. Run Streamlit
streamlit run Home.py
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `BACKEND_BASE_URL` | FastAPI backend URL (e.g. `https://your-backend.onrender.com`) |
| `APP_ENV` | `development` / `production` |
| `MOCK_MODE` | `false` (use backend) / `true` (offline fallback) |

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repository: `mining-digital-twin-frontend`
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → **New App**
3. Select your GitHub repo, branch, and main file: `Home.py`
4. Add **Secrets** in Streamlit Cloud settings:
   ```toml
   BACKEND_BASE_URL = "https://your-backend.onrender.com"
   ```
5. Deploy

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Cannot connect to backend" | Verify `BACKEND_BASE_URL` in `.env` or Streamlit secrets |
| Backend returning 500 | Check Render logs; ensure `ALLOWED_ORIGINS` includes your Streamlit URL |
| 3D Twin blank | Browser must support WebGL; check console for errors |
| Render cold start | First request may take 30-60s on free tier; retry |
| CORS error | Add frontend URL to backend `ALLOWED_ORIGINS` env var |

## Repository Structure

```
mining-digital-twin-frontend/
├── Home.py                  # Main entry point (Plant Overview)
├── pages/
│   ├── 1_3D_Digital_Twin.py
│   ├── 2_Equipment_Details.py
│   ├── 3_Streams.py
│   ├── 4_Simulation.py
│   ├── 5_Analytics.py
│   ├── 6_Optimization.py
│   ├── 7_Data_Quality.py
│   └── 8_About.py
├── services/
│   └── api_client.py        # All backend calls go here
├── components/
│   └── ui_helpers.py        # Shared UI utilities
├── threejs/
│   └── twin3d.html          # Three.js 3D visualization
├── .streamlit/
│   └── config.toml          # Dark theme config
├── requirements.txt
├── .env.example
└── README.md
```
