from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

# This sets up a local "file" database nicely called "protocol_monitor.db"
# It's much easier than installing a big database server.
DATABASE_URL = "sqlite:///./protocol_monitor.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Defines the Tables (The Schema) ---

class ProtocolSnapshot(Base):
    """
    Stores the health metrics of a protocol at a specific time.
    """
    __tablename__ = "protocol_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    protocol_name = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    tvl_usd = Column(DECIMAL(20, 2))
    apy_7d = Column(DECIMAL(8, 4))
    utilization_rate = Column(DECIMAL(5, 4), nullable=True) # Only for lending protocols

    # Ensures we don't have duplicate data for the same time
    __table_args__ = (
        UniqueConstraint('protocol_name', 'timestamp', name='uix_protocol_timestamp'),
    )

class ProtocolAlert(Base):
    """
    Stores any problems we find (Anomalies).
    """
    __tablename__ = "protocol_alerts"

    id = Column(Integer, primary_key=True, index=True)
    protocol_name = Column(String(50), nullable=False)
    alert_type = Column(String(50)) # e.g., 'tvl_drop', 'apy_spike'
    severity = Column(String(10))   # 'critical', 'warning', 'info'
    message = Column(String)
    triggered_at = Column(DateTime(timezone=True), default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

# Create the tables in the database file
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Tables created successfully!")
