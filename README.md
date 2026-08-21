# ProfitLens

ProfitLens is a deterministic-first AI business analytics platform for D2C brands.

The core principle is simple:

- Python/Pandas calculate business truth.
- The AI layer interprets already-calculated results.
- Missing metrics remain unavailable instead of being fabricated.

Current functionality includes:

- Revenue analysis
- Order analysis
- AOV analysis
- Product analytics
- Customer-data quality analysis
- Logistics and fulfilment analysis
- Scenario / what-if analysis
- Natural-language business questions
- Deterministic fallback when the AI service is unavailable


## Project Structure

```text
ai-business-analyst/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── exceptions.py
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── types/
│   ├── package.json
│   └── .env.example
│
├── data/
├── tests/
├── pytest.ini
├── requirements.txt
└── README.md