# Aevorex Backend

FastAPI backend for the Aevorex FinanceHub platform.

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env.local` file in the backend root:

```bash
ENV=local
API_TITLE=Aevorex Backend
API_VERSION=0.1.0
CORS_ORIGINS=http://localhost:3000,https://aevorex.com
```

### 3. Run Development Server

```bash
# Load environment variables
export $(cat .env.local | xargs) 2>/dev/null || true

# Start server
uvicorn main:app --reload --port 8000
```

### 4. Test Endpoints

- Health: `GET http://localhost:8000/health`
- Version: `GET http://localhost:8000/version`
- Core Ping: `GET http://localhost:8000/api/core/ping`

## Project Structure

```
aevorex-backend/
├── api/
│   └── core/
│       ├── models/      # Pydantic models
│       ├── services/    # Business logic
│       ├── utils/       # Utilities
│       └── router.py    # Core API routes
├── tests/               # Test files
├── main.py             # FastAPI application
├── requirements.txt    # Python dependencies
└── Dockerfile         # Container configuration
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .
```

## Docker

```bash
# Build image
docker build -t aevorex-backend .

# Run container
docker run -p 8000:8000 aevorex-backend
```
