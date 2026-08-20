# ProfitLens Frontend

Clean React + Vite + TypeScript frontend rebuilt from the Claude prototype's visual language, but connected to the real deterministic ProfitLens backend.

## Pages

- Overview → `GET /dashboard/{month}`
- Product Analysis → `GET /analytics/products/{month}`
- Customer Analysis → `GET /analytics/customers`
- Logistics → `GET /analytics/logistics/{month}`
- Ask ProfitLens → `POST /analytics/business-question`
- Scenario Lab → `POST /analytics/scenario`

Unsupported metrics such as true profit, CAC, ROAS, RTO and contribution margin are intentionally not faked.

## Codespaces local development

Run the backend on port 8000:

```bash
uvicorn backend.app.main:app --reload
```

Run the frontend on port 5173 from this folder:

```bash
npm install
npm run dev
```

Vite proxies `/api/*` to `http://127.0.0.1:8000`, so no CORS change is needed for local Codespaces development.

## Production API URL

Copy `.env.example` to `.env` and set:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

When this variable is set, the browser calls that backend directly. Configure CORS on FastAPI for the deployed frontend origin.
