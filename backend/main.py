from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

class FabricReceive(BaseModel):
    fabric_type: str
    color: str
    roll_no: str
    meters: float
    supplier: str


@app.post("/fabric/receive")
def receive_fabric(data: FabricReceive):

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO fabric_receive
        (fabric_type, color, roll_no, meters, supplier)
        VALUES (%s,%s,%s,%s,%s)
        """,
        (
            data.fabric_type,
            data.color,
            data.roll_no,
            data.meters,
            data.supplier,
        ),
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Fabric received successfully"}
