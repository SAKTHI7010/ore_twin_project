# Ore Beneficiation Digital Twin — Backend

FastAPI backend for the **Ore Beneficiation Plant Digital Twin**.

## Tech Stack
- **FastAPI** + **Uvicorn** (ASGI)
- **Pydantic v2** schemas
- **NumPy / Pandas / SciPy** scientific stack
- Deterministic simulation engine with fixed seed
- **CORS** configured for frontend origin

## Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env
# Edit .env → set ALLOWED_ORIGINS to your frontend URL

# 4. Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Verify
curl http://localhost:8000/health
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/v1/plant/overview` | GET | Plant KPIs & status |
| `/api/v1/equipment` | GET | All equipment |
| `/api/v1/equipment/{id}` | GET | Equipment detail |
| `/api/v1/streams` | GET | All streams |
| `/api/v1/streams/{id}` | GET | Stream detail |
| `/api/v1/simulation/state` | GET | Current simulation state |
| `/api/v1/simulation/run` | POST | Run simulation step |
| `/api/v1/analytics/mass-balance` | GET | Mass balance |
| `/api/v1/analytics/trends` | GET | Trend data |
| `/api/v1/optimization/run` | POST | Advisory optimization |
| `/api/v1/data-quality` | GET | Data quality status |

Interactive docs: http://localhost:8000/docs

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `APP_ENV` | `development` | Runtime environment |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `http://localhost:8501` | CORS origins (comma-separated) |
| `MODEL_VERSION` | `1.0.0` | API version |
| `DEMO_MODE` | `true` | Enable demo/simulation data |
| `DATA_SOURCE_URL` | *(empty)* | Future live data source |

## Deploy to Render

1. Push this folder to a GitHub repository: `mining-digital-twin-backend`
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
5. Add Environment Variables from the table above
6. Set `ALLOWED_ORIGINS` to your Streamlit frontend URL
7. Deploy and note your public URL: `https://your-backend.onrender.com`

## Run Tests

```bash
pytest tests/ -v
```

## Repository Structure

```
mining-digital-twin-backend/
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── core/
│   │   └── config.py        # Settings (pydantic-settings)
│   ├── schemas/
│   │   └── domain.py        # All Pydantic schemas
│   ├── api/routes/
│   │   ├── plant.py         # /health + /plant/overview
│   │   ├── equipment.py     # /equipment
│   │   ├── streams.py       # /streams
│   │   ├── simulation.py    # /simulation
│   │   ├── analytics.py     # /analytics
│   │   └── optimization.py  # /optimization + /data-quality
│   └── mock/
│       └── seed_data.py     # Deterministic DEMO data (seed=42)
├── tests/
│   └── test_api.py
├── requirements.txt
├── .env.example
├── render.yaml
├── start.sh
└── README.md
```

## Notes

- All demo data uses **fixed seed (42)** for reproducibility
- Mass balance closure checks performed at each simulation run
- Ready for PostgreSQL/TimescaleDB replacement via repository interface
- CORS origins must include your deployed frontend URL
