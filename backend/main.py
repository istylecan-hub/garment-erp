from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
import psycopg2
import os
from sqlalchemy import create_engine
from models import Base

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")


@app.on_event("startup")
def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)


def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


class FabricReceive(BaseModel):
    fabric_type: str = Field(..., min_length=1)
    color: str = Field(..., min_length=1)
    roll_no: str = Field(..., min_length=1)
    meters: float
    supplier: str = Field(..., min_length=1)


class CuttingOrder(BaseModel):
    style: str = Field(..., min_length=1)
    color: str = Field(..., min_length=1)
    size: str = Field(..., min_length=1)
    qty: int = Field(..., ge=1)


class Bundle(BaseModel):
    bundle_code: str = Field(..., min_length=1)
    style: str = Field(..., min_length=1)
    color: str = Field(..., min_length=1)
    size: str = Field(..., min_length=1)
    qty: int = Field(..., ge=1)
    cut_by: str = Field(..., min_length=1)


class BundleIssue(BaseModel):
    bundle_code: str = Field(..., min_length=1)
    worker_machine: str = Field(..., min_length=1)


class ProductionReceive(BaseModel):
    bundle_no: str
    worker_machine: str
    produced_qty: int


def insert_and_commit(conn, query, params, error_detail):
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        )
    finally:
        cur.close()


@app.post("/fabric/receive", status_code=status.HTTP_201_CREATED)
def receive_fabric(data: FabricReceive, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO fabric_receive
        (fabric_type, color, roll_no, meters, supplier)
        VALUES (%s,%s,%s,%s,%s)
        """,
        (data.fabric_type, data.color, data.roll_no, data.meters, data.supplier),
        "could not record fabric reception",
    )
    return {"message": "Fabric received successfully"}


@app.post("/cutting/order", status_code=status.HTTP_201_CREATED)
def create_cutting_order(data: CuttingOrder, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO cutting_orders
        (style, color, size, qty)
        VALUES (%s,%s,%s,%s)
        """,
        (data.style, data.color, data.size, data.qty),
        "could not create cutting order",
    )
    return {"message": "Cutting order created"}


@app.post("/bundle/create", status_code=status.HTTP_201_CREATED)
def create_bundle(data: Bundle, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO bundles
        (bundle_code, style, color, size, qty, cut_by)
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            data.bundle_code,
            data.style,
            data.color,
            data.size,
            data.qty,
            data.cut_by,
        ),
        "could not create bundle",
    )
    return {"message": "Bundle created"}


@app.post("/bundle/issue", status_code=status.HTTP_201_CREATED)
def issue_bundle(data: BundleIssue, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO bundle_issue
        (bundle_code, worker_machine)
        VALUES (%s,%s)
        """,
        (data.bundle_code, data.worker_machine),
        "could not issue bundle",
    )
    return {"message": "Bundle issued to worker"}


@app.post("/production/receive", status_code=status.HTTP_201_CREATED)
def receive_production(data: ProductionReceive, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO production_receive
        (bundle_no, worker_machine, produced_qty)
        VALUES (%s,%s,%s)
        """,
        (data.bundle_no, data.worker_machine, data.produced_qty),
        "could not record production reception",
    )
    return {"message": "Production received successfully"}
