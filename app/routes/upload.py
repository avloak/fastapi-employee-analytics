from fastapi import APIRouter, UploadFile, HTTPException, Request
import pandas as pd
import numpy as np
from app.models import HiredEmployee, Department, Job

router = APIRouter()

@router.post("/hired_employees")
async def upload_hired_employees(file: UploadFile, request: Request):
    try:
        df = pd.read_csv(file.file)
        expected_cols = {"id", "name", "datetime", "department_id", "job_id"}
        if not expected_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Invalid schema for hired_employees.csv")

        try:
            df["datetime"] = pd.to_datetime(df["datetime"], errors="raise", utc=False).replace({pd.NaT: None})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")
        
        try:
            df.replace({np.nan: None}, inplace=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid integer: {e}")

        request.app.state.upsert_dataframe(df, HiredEmployee)
        return {"message": "hired_employees uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/departments")
async def upload_departments(file: UploadFile, request: Request):
    try:
        df = pd.read_csv(file.file)
        expected_cols = {"id", "department"}
        if not expected_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Invalid schema for departments.csv")
        request.app.state.upsert_dataframe(df, Department)
        return {"message": "departments uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs")
async def upload_jobs(file: UploadFile, request: Request):
    try:
        df = pd.read_csv(file.file)
        expected_cols = {"id", "job"}
        if not expected_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Invalid schema for jobs.csv")
        request.app.state.upsert_dataframe(df, Job)
        return {"message": "jobs uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))