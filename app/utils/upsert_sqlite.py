import pandas as pd
from sqlmodel import Session

def upsert_dataframe(df: pd.DataFrame, model, batch_size: int = 1000, engine=None):
    with Session(engine) as session:
        for record in df.to_dict(orient="records"):
            session.merge(model(**record))
        session.commit()