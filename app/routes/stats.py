from fastapi import APIRouter, Request, Depends
from sqlmodel import Session

router = APIRouter()

# Dependency to fetch the stats implementation (set in app.state by create_app)
def get_stats_function(request: Request):
    return request.app.state.stats_function

# Dependency to fetch a database session (sessionmaker is set in app.state by create_app)
def get_session(request: Request):
    return request.app.state.sessionmaker()

@router.get("/hired_employees/{year}")
def get_hired_employees_stats(
    year: int,
    stats_function=Depends(get_stats_function),
    session: Session = Depends(get_session),
):
    # Call the injected implementation
    return stats_function.get_hired_employees_stats(year, session)


@router.get("/top_departments/{year}")
def get_top_departments(
    year: int,
    stats_function=Depends(get_stats_function),
    session: Session = Depends(get_session),
):
    # Call the injected implementation
    return stats_function.get_top_departments(year, session)

@router.get("/inspect_hired_employees")
def get_hired_employees(
    stats_function=Depends(get_stats_function),
    session: Session = Depends(get_session),
):
    # Call the injected implementation
    return stats_function.get_hired_employees(session)