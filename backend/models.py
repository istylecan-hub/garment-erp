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
