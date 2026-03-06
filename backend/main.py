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


class BundleCreate(BaseModel):
    style: str
    color: str
    size: str
    qty: int


class BundleScan(BaseModel):
    bundle_code: str
    machine_no: str


class ProductionSubmit(BaseModel):
    bundle_code: str
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


@app.post("/bundle/scan", status_code=status.HTTP_201_CREATED)
def scan_bundle(data: BundleScan, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO bundle_scan
        (bundle_code, machine_no)
        VALUES (%s,%s)
        """,
        (data.bundle_code, data.machine_no),
        "could not scan bundle",
    )
    return {"message": "Bundle scanned successfully"}


@app.post("/production/submit", status_code=status.HTTP_201_CREATED)
def submit_production(data: ProductionSubmit, conn=Depends(get_conn)):
    insert_and_commit(
        conn,
        """
        INSERT INTO production_submit
        (bundle_code, produced_qty)
        VALUES (%s,%s)
        """,
        (data.bundle_code, data.produced_qty),
        "could not submit production",
    )
    return {"message": "Production submitted successfully"}


@app.get("/worker/performance")
def worker_performance():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT worker_machine, SUM(produced_qty)
        FROM production_receive
        GROUP BY worker_machine
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Return as a list of dicts for better API response
    return [{"worker_machine": row[0], "total_produced_qty": row[1]} for row in rows]


@app.get("/dashboard/summary")
def dashboard_summary():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT SUM(produced_qty)
        FROM production_receive
        WHERE DATE(received_at) = CURRENT_DATE
    """)
    today_production = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT worker_machine,
        SUM(produced_qty) as total
        FROM production_receive
        GROUP BY worker_machine
        ORDER BY total DESC
        LIMIT 1
    """)
    top_worker_row = cur.fetchone()
    top_worker = {
        "worker_machine": top_worker_row[0],
        "total_produced_qty": top_worker_row[1]
    } if top_worker_row else None

    cur.execute("""
        SELECT COUNT(*)
        FROM bundle_issue
        WHERE DATE(issued_at) = CURRENT_DATE
    """)
    bundles_in_progress = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "today_production": today_production,
        "top_worker": top_worker,
        "bundles_in_progress": bundles_in_progress
    }


@app.get("/ai/production-plan")
def ai_production_plan():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # total production today
    cur.execute("""
        SELECT SUM(produced_qty)
        FROM production_receive
        WHERE DATE(received_at) = CURRENT_DATE
    """)
    today_production = cur.fetchone()[0] or 0

    # worker efficiency
    cur.execute("""
        SELECT worker_machine,
        SUM(produced_qty) as total
        FROM production_receive
        GROUP BY worker_machine
        ORDER BY total DESC
    """)
    workers = cur.fetchall()

    # bundles issued today
    cur.execute("""
        SELECT COUNT(*)
        FROM bundle_issue
        WHERE DATE(issued_at) = CURRENT_DATE
    """)
    bundles_today = cur.fetchone()[0]

    cur.close()
    conn.close()

    # simple planning logic
    avg_worker_output = 0
    if len(workers) > 0:
        avg_worker_output = today_production / len(workers)

    return {
        "today_production": today_production,
        "workers_active": len(workers),
        "bundles_issued_today": bundles_today,
        "avg_worker_output": round(avg_worker_output, 2)
    }
