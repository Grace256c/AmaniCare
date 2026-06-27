# MamaCare AI Backend

AI-powered women's health companion backend for the MamaCare AI hackathon. Built with **FastAPI**, **SQLAlchemy 2.0**, and **Google Gemini**, with Africa's Talking USSD webhook support.

## Features

- User registration and profile management
- AI health advice via Google Gemini (personalized by age, life stage, language)
- Africa's Talking USSD session flow (register + ask health questions)
- Mock SMS reminder scheduler (period, medication, pregnancy, menopause)
- Clean architecture: routes → services → repositories
- Async endpoints, Pydantic v2 validation, Loguru logging
- OpenAPI docs at `/docs`
- Docker-ready deployment

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI + Uvicorn |
| Python | 3.12 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL (production) / SQLite (dev) |
| AI | Google Gemini API (httpx) |
| Logging | Loguru |
| Testing | pytest + pytest-asyncio |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, exception handlers
│   ├── core/                # Config, database, security
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response models
│   ├── api/                 # Route handlers (thin layer)
│   ├── services/            # Business logic
│   ├── repositories/        # Data access
│   └── utils/               # Prompt builder
├── alembic/                 # Database migrations
├── tests/                   # pytest test suite
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Installation

### 1. Clone and enter the backend directory

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL or SQLite connection string |
| `GOOGLE_API_KEY` | Google AI Studio / Gemini API key |
| `AFRICAS_TALKING_USERNAME` | Africa's Talking username |
| `AFRICAS_TALKING_API_KEY` | Africa's Talking API key |
| `SECRET_KEY` | Application secret (change in production) |

## Running Locally

### Development server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database migrations

For PostgreSQL or when you want explicit schema control:

```bash
# Apply migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"
```

SQLite development uses auto-create on startup; Alembic is recommended for production.

## Gemini Configuration

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Set `GOOGLE_API_KEY` in your `.env`
3. Optional: set `GEMINI_MODEL` (default: `gemini-2.0-flash`)

The `GeminiService` sends personalized prompts built from the user profile. It never diagnoses or prescribes — educational guidance only.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/users/register` | Register a user |
| GET | `/api/users/{phone_number}` | Get user profile |
| PUT | `/api/users/{phone_number}` | Update user profile |
| POST | `/api/advice` | Ask AI health question |
| POST | `/api/ussd` | Africa's Talking USSD webhook |
| POST | `/api/reminders` | Schedule mock reminder |
| GET | `/api/reminders/{phone_number}` | List user reminders |

## Sample cURL Commands

### Health check

```bash
curl http://localhost:8000/health
```

### Register a user

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+256700000000",
    "name": "Grace",
    "age": 23,
    "life_stage": "Regular",
    "language": "English"
  }'
```

### Get user

```bash
curl http://localhost:8000/api/users/+256700000000
```

### Ask AI for advice

```bash
curl -X POST http://localhost:8000/api/advice \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+256700000000",
    "question": "I have severe period cramps."
  }'
```

### USSD webhook (simulate Africa's Talking)

```bash
# Welcome menu
curl -X POST http://localhost:8000/api/ussd \
  -d "sessionId=abc123" \
  -d "phoneNumber=+256700000000" \
  -d "text=" \
  -d "serviceCode=*384*123#"

# Start registration
curl -X POST http://localhost:8000/api/ussd \
  -d "sessionId=abc123" \
  -d "phoneNumber=+256700000000" \
  -d "text=1" \
  -d "serviceCode=*384*123#"
```

### Schedule a reminder

```bash
curl -X POST http://localhost:8000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+256700000000",
    "type": "period",
    "next_date": "2026-07-15"
  }'
```

## USSD Flow

```
Dial *384*123#
  │
  ├─ 1 Register
  │    ├─ Enter name
  │    ├─ Enter age
  │    ├─ Choose life stage (1–7)
  │    └─ END: Registration complete
  │
  └─ 2 Ask Health Question
       ├─ Enter question
       └─ END: AI advice
```

Life stages: Teen, Regular, TryingToConceive, Pregnant, Postpartum, Perimenopause, Menopause.

## Testing

```bash
pytest -v
```

Tests cover health check, user registration, advice endpoint (Gemini mocked), USSD flow, and reminders.

## Docker Deployment

```bash
docker build -t mamacare-api .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/mamacare \
  -e GOOGLE_API_KEY=your_key \
  -e SECRET_KEY=your_secret \
  mamacare-api
```

## CORS

The Next.js frontend at `http://localhost:3000` is allowed by default. Configure additional origins via the `cors_origins` setting in `app/core/config.py`.

## Error Format

All errors return consistent JSON:

```json
{
  "success": false,
  "message": "Human-readable error message"
}
```

## License

Hackathon MVP — MamaCare AI.
