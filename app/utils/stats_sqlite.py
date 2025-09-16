from sqlmodel import Session, select
from sqlalchemy import func, case
from app.models import HiredEmployee, Department, Job

def get_hired_employees_stats(year: int, session: Session):
    """
    SQLite-compatible rewrite of main.get_hired_employees_stats.
    Uses strftime('%Y', ...) and strftime('%m', ...) + CASE() for quarters.
    """
    hiredemployee_descriptions = (
        select(
            Department.department.label("department_id"),
            Job.job.label("job_id"),
            HiredEmployee.datetime,
            HiredEmployee.id
        )
        .join(Department, Department.id == HiredEmployee.department_id)
        .join(Job, Job.id == HiredEmployee.job_id)
        .filter(func.strftime("%Y", HiredEmployee.datetime) == str(year))
        .cte("hiredemployee_descriptions")
    )

    month_str = func.substr(hiredemployee_descriptions.c.datetime, 6, 2)

    quarter_expr = case(
        (month_str.in_(["01", "02", "03"]), 1),
        (month_str.in_(["04", "05", "06"]), 2),
        (month_str.in_(["07", "08", "09"]), 3),
        else_=4,
    ).label("quarter")

    hiredemployee_aggregates = (
        select(
            hiredemployee_descriptions.c.department_id,
            hiredemployee_descriptions.c.job_id,
            quarter_expr,
            func.count(hiredemployee_descriptions.c.id).label("counted"),
        )
        .group_by(
            hiredemployee_descriptions.c.department_id,
            hiredemployee_descriptions.c.job_id,
            quarter_expr,
        )
        .cte("hiredemployee_aggregates")
    )

    query = (
        select(
            hiredemployee_aggregates.c.department_id.label("department"),
            hiredemployee_aggregates.c.job_id.label("job"),
            func.sum(case((hiredemployee_aggregates.c.quarter == 1, hiredemployee_aggregates.c.counted), else_=0)).label("Q1"),
            func.sum(case((hiredemployee_aggregates.c.quarter == 2, hiredemployee_aggregates.c.counted), else_=0)).label("Q2"),
            func.sum(case((hiredemployee_aggregates.c.quarter == 3, hiredemployee_aggregates.c.counted), else_=0)).label("Q3"),
            func.sum(case((hiredemployee_aggregates.c.quarter == 4, hiredemployee_aggregates.c.counted), else_=0)).label("Q4"),
        )
        .group_by(
            hiredemployee_aggregates.c.department_id,
            hiredemployee_aggregates.c.job_id,
        )
        .order_by(
            hiredemployee_aggregates.c.department_id,
            hiredemployee_aggregates.c.job_id,
        )
    )

    results = session.exec(query)

    return [
        {"department": r.department, "job": r.job, "Q1": r.Q1, "Q2": r.Q2, "Q3": r.Q3, "Q4": r.Q4}
        for r in results
    ]

def get_top_departments(year: int, session: Session):
    """
    SQLite-compatible rewrite of main.get_top_departments.
    Uses strftime('%Y', ...) to filter the year.
    """
    base_query = (
        select(
            Department.id,
            Department.department,
            func.count(HiredEmployee.id).label("hired"),
        )
        .join(Department, Department.id == HiredEmployee.department_id)
        .filter(func.strftime("%Y", HiredEmployee.datetime) == str(year))
        .group_by(Department.id, Department.department)
        .cte("base_query")
    )

    avg_query = select(func.avg(base_query.c.hired))
    mean_value = avg_query.scalar_subquery()

    query = (
        select(base_query.c.id, base_query.c.department, base_query.c.hired)
        .filter(base_query.c.hired > mean_value)
        .order_by(base_query.c.hired.desc())
    )

    results = session.exec(query)
    return [{"id": r.id, "department": r.department, "hired": r.hired} for r in results]

def get_hired_employees(session: Session):
    results = session.exec(select(HiredEmployee).limit(5))
    return [
        {"id": r.id, "name": r.name, "datetime": r.datetime, "department_id": r.department_id, "job_id": r.job_id}
        for r in results
    ]