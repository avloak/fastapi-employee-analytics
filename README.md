# FastAPI Employee Analytics API

A FastAPI application for uploading and analyzing employee hiring data.

## Features

- CSV upload for employees, departments, and jobs
- Analytics endpoints for hiring statistics
- PostgreSQL database integration
- Docker containerization

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env.{dev|prod}` and configure your database settings
3. Run with Docker: `docker compose -f docker-compose.{dev|prod}.yml up --build -d`

## API Endpoints

- `POST /upload/{hired_employees|departments|jobs}` - Upload CSV data
- `GET /stats/hired_employees/{year}` - Quarterly hiring stats
- `GET /stats/top_departments/{year}` - Departments above average hiring

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Run locally
fastapi dev app/main.py 