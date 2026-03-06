from sqlalchemy import create_engine, MetaData
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

def drop_duplicate_tables():
    # List of table names to drop (add any duplicates you want to remove)
    tables_to_drop = [
        # Example: "production_receive_old",
        # Add table names as needed
    ]
    with engine.connect() as conn:
        for table in tables_to_drop:
            if table in metadata.tables:
                print(f"Dropping table: {table}")
                metadata.tables[table].drop(bind=engine, checkfirst=True)
            else:
                print(f"Table not found: {table}")

if __name__ == "__main__":
    drop_duplicate_tables()
    print("Cleanup complete.")
