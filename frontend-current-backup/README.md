# ProfitLens Frontend

Ready-to-use React + Vite frontend for the ProfitLens FastAPI backend.

## Expected backend endpoints

- `GET /health`
- `GET /dashboard/{month}`
- `GET /analytics/reporting-periods`
- `GET /analytics/products/{month}`
- `GET /analytics/customers`
- `GET /analytics/logistics/{month}`
- `POST /analytics/business-question`
- `POST /analytics/scenario`

## Codespaces setup

Keep the backend running from the repository root:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Then in another terminal:

```bash
cd frontend
npm install
npm run build
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.
