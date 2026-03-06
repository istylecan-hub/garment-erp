from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Style(Base):
    __tablename__ = "styles"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Color(Base):
    __tablename__ = "colors"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Size(Base):
    __tablename__ = "sizes"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    machine_no = Column(String)

class FabricReceive(Base):
    __tablename__ = "fabric_receive"
    id = Column(Integer, primary_key=True)
    fabric_type = Column(String)
    color = Column(String)
    roll_no = Column(String)
    meters = Column(Numeric)
    supplier = Column(String)
    received_at = Column(TIMESTAMP, server_default=func.now())


class CuttingOrder(Base):
    __tablename__ = "cutting_orders"
    id = Column(Integer, primary_key=True)
    style = Column(String)
    color = Column(String)
    size = Column(String)
    qty = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Bundle(Base):
    __tablename__ = "bundles"
    id = Column(Integer, primary_key=True)
    bundle_code = Column(String)
    style = Column(String)
    color = Column(String)
    size = Column(String)
    qty = Column(Integer)
    cut_by = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class BundleIssue(Base):
    __tablename__ = "bundle_issue"
    id = Column(Integer, primary_key=True)
    bundle_code = Column(String)
    worker_machine = Column(String)
    issued_at = Column(TIMESTAMP, server_default=func.now())


class ProductionReceive(Base):
    __tablename__ = "production_receive"
    id = Column(Integer, primary_key=True)
    bundle_no = Column(String)
    worker_machine = Column(String)
    produced_qty = Column(Integer)
    received_at = Column(TIMESTAMP, server_default=func.now())


class ProductionSubmitDB(Base):
    __tablename__ = "production_receive"
    id = Column(Integer, primary_key=True)
    bundle_code = Column(String)
    produced_qty = Column(Integer)
    submitted_at = Column(TIMESTAMP, server_default=func.now())
