# ProfitLens Frontend — Upgraded Build

This package preserves the upgraded UI we built during the current ProfitLens work:

- Upgraded Overview dashboard
- Product Analysis V2
- Customer Analysis with data-availability states
- Logistics Analysis with TAT/P90 views
- Expanded Ask ProfitLens analyst workspace
- Scenario Lab V2
- Dynamic reporting periods
- Partial-month handling
- Existing FastAPI backend integration

## Backend expected

Run from repository root:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run build
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.
