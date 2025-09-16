import io
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, inspect
from sqlalchemy.pool import StaticPool
from app.main import create_app
from app.utils import upsert_sqlite, stats_sqlite


# -------------------------------------------------------------------
# Test Database Setup (SQLite in-memory, isolated from Postgres)
# -------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------

@pytest.fixture(scope="function")
def client():
    # Rebuild schema fresh each test
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

    app = create_app(
        engine_override=test_engine,
        stats_function=stats_sqlite,
        upsert_function=upsert_sqlite
    )
    
    # Debug sanity check
    inspector = inspect(test_engine)
    print("Tables in SQLite test DB:", inspector.get_table_names())

    with TestClient(app) as c:
        yield c

    SQLModel.metadata.drop_all(test_engine)

# -------------------------------------------------------------------
# Upload Tests
# -------------------------------------------------------------------

def test_upload_departments(client):
    csv_content = "id,department\n1,Engineering\n2,HR\n"
    response = client.post(
        "/upload/departments",
        files={"file": ("departments.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert response.status_code == 200, f"Unexpected error: {response.status_code}, {response.text}"
    assert response.json() == {"message": "departments uploaded successfully"}


def test_upload_jobs(client):
    csv_content = "id,job\n1,Developer\n2,Manager\n"
    response = client.post(
        "/upload/jobs",
        files={"file": ("jobs.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert response.status_code == 200, f"Unexpected error: {response.status_code}, {response.text}"
    assert response.json() == {"message": "jobs uploaded successfully"}


def test_upload_hired_employees(client):
    csv_content = (
        "id,name,datetime,department_id,job_id\n"
        "1,Alice,2023-01-15,1,1\n"
        "2,Bob,2023-04-20,2,2\n"
    )
    response = client.post(
        "/upload/hired_employees",
        files={"file": ("hired.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )
    assert response.status_code == 200, f"Unexpected error: {response.status_code}, {response.text}"
    assert response.json() == {"message": "hired_employees uploaded successfully"}

# -------------------------------------------------------------------
# Stats Endpoints Tests
# -------------------------------------------------------------------

def test_get_hired_employees(client):
    csv_content = (
        "id,name,datetime,department_id,job_id\n"
        "1,Alice,2023-01-15,1,1\n"
        "2,Bob,2023-02-20,2,2\n"
        "3,Charlie,2023-03-05,1,1\n"
        "4,Diana,2023-04-10,2,2\n"
        "5,Eve,2023-05-22,1,1\n"
    )
    client.post(
        "/upload/hired_employees",
        files={"file": ("hired.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )

    response = client.get("/stats/inspect_hired_employees")
    assert response.status_code == 200, f"Unexpected error: {response.status_code}, {response.text}"
    rows = response.json()
    assert len(rows) == 5
    names = [r["name"] for r in rows]
    assert names == ["Alice", "Bob", "Charlie", "Diana", "Eve"]    

def test_get_hired_employees_stats(client):
    client.post(
        "/upload/departments",
        files={"file": ("departments.csv", io.BytesIO(b"id,department\n1,Engineering\n"), "text/csv")},
    )
    client.post(
        "/upload/jobs",
        files={"file": ("jobs.csv", io.BytesIO(b"id,job\n1,Developer\n"), "text/csv")},
    )
    client.post(
        "/upload/hired_employees",
        files={"file": ("hired.csv", io.BytesIO(b"id,name,datetime,department_id,job_id\n1,Alice,2023-02-16,1,1\n"), "text/csv")},
    )

    response = client.get("/stats/hired_employees/2023")
    assert response.status_code == 200
    data = response.json()
    assert any(row["Q1"] == 1 and row["department"] == "Engineering" for row in data)


def test_get_top_departments(client):
    client.post(
        "/upload/departments",
        files={"file": ("departments.csv", io.BytesIO(b"id,department\n1,Engineering\n2,HR\n"), "text/csv")},
    )
    client.post(
        "/upload/jobs",
        files={"file": ("jobs.csv", io.BytesIO(b"id,job\n1,Developer\n"), "text/csv")},
    )
    csv_content = (
        "id,name,datetime,department_id,job_id\n"
        "1,Alice,2023-02-10,1,1\n"
        "2,Bob,2023-03-15,1,1\n"
        "3,Charlie,2023-05-01,2,1\n"
    )
    client.post(
        "/upload/hired_employees",
        files={"file": ("hired.csv", io.BytesIO(csv_content.encode()), "text/csv")},
    )

    response = client.get("/stats/top_departments/2023")
    assert response.status_code == 200
    data = response.json()
    assert any(d["department"] == "Engineering" for d in data)
