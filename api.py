from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn

from database import SessionLocal, ProtocolSnapshot, ProtocolAlert
from models import ProtocolSnapshotResponse, AlertResponse, ProtocolReview

app = FastAPI(title="Protocol Monitor API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/protocols", response_model=List[ProtocolReview])
def get_protocols(db: Session = Depends(get_db)):
    """
    Returns the latest health status for all tracked protocols.
    """
    protocol_names = db.query(ProtocolSnapshot.protocol_name).distinct().all()
    protocol_names = [p[0] for p in protocol_names]
    
    results = []
    for name in protocol_names:
        latest = db.query(ProtocolSnapshot).filter(
            ProtocolSnapshot.protocol_name == name
        ).order_by(ProtocolSnapshot.timestamp.desc()).first()
        
        if not latest:
            continue
            
        active_alerts = db.query(ProtocolAlert).filter(
            ProtocolAlert.protocol_name == name,
            ProtocolAlert.resolved_at == None
        ).all()
        
        status = "healthy"
        for alert in active_alerts:
            if alert.severity == 'critical':
                status = "critical"
                break
            elif alert.severity == 'warning' and status != 'critical':
                status = "warning"
                
        results.append({
            "name": name,
            "tvl_usd": latest.tvl_usd,
            "apy_7d": latest.apy_7d,
            "status": status
        })
        
    return results

@app.get("/protocols/{name}/history", response_model=List[ProtocolSnapshotResponse])
def get_protocol_history(
    name: str, 
    days: int = Query(30, gt=0, le=365), 
    db: Session = Depends(get_db)
):
    """
    Returns historical data for a specific protocol.
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    history = db.query(ProtocolSnapshot).filter(
        ProtocolSnapshot.protocol_name == name,
        ProtocolSnapshot.timestamp >= cutoff_date
    ).order_by(ProtocolSnapshot.timestamp.asc()).all()
    
    return history

@app.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status: 'open' or 'resolved'"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of alerts, optionally filtered by status.
    """
    query = db.query(ProtocolAlert)
    
    if status == 'open':
        query = query.filter(ProtocolAlert.resolved_at == None)
    elif status == 'resolved':
        query = query.filter(ProtocolAlert.resolved_at != None)
        
    return query.order_by(ProtocolAlert.triggered_at.desc()).all()

if __name__ == "__main__":
    print("Starting Protocol Monitor API on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
