from sqlmodel import SQLModel, Field
from datetime import datetime

class HiredEmployee(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str | None
    datetime: datetime | None
    department_id: int | None
    job_id: int | None

class Department(SQLModel, table=True):
    id: int = Field(primary_key=True)
    department: str | None

class Job(SQLModel, table=True):
    id: int = Field(primary_key=True)
    job: str | None