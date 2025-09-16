import pandas as pd
from sqlmodel import Session
from sqlalchemy.dialects.postgresql import insert

def upsert_dataframe(df: pd.DataFrame, model, batch_size: int = 1000, engine=None):
    table = model.__table__
    with Session(engine) as session:
        records = df.to_dict(orient="records")
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            stmt = insert(table).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={c.name: stmt.excluded[c.name] for c in table.columns if c.name != "id"}
            )
            session.exec(stmt)
        session.commit()