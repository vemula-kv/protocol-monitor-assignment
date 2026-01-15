import logging
import requests
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from database import SessionLocal, ProtocolSnapshot, ProtocolAlert, engine

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for Alerts
CRITICAL_TVL_DROP_PERCENT = Decimal('0.20') # 20%
WARNING_APY_THRESHOLD = Decimal('2.0')      # 2%
WARNING_UTILIZATION_THRESHOLD = Decimal('0.95') # 95%

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MOCKED DATA SOURCES ---
# In a real scenario, these would call actual APIs (e.g., DeFiLlama, RPC nodes)

def fetch_felix_data():
    """
    Mock data for Felix protocol.
    Simulates occasionally high utilization or low APY.
    """
    # Simulate API latency
    time.sleep(0.5)
    
    # Randomly generate values that are mostly healthy but sometimes anomalous
    is_anomaly = random.random() < 0.1 # 10% chance of weird data
    
    tvl = Decimal('10000000.00') + Decimal(random.uniform(-50000, 50000))
    apy = Decimal('12.5') + Decimal(random.uniform(-1.0, 1.0))
    utilization = Decimal('0.80') + Decimal(random.uniform(-0.05, 0.05))

    if is_anomaly:
        # Generate a specific anomaly type 
        anomaly_type = random.choice(['tvl_drop', 'apy_low', 'high_util'])
        if anomaly_type == 'tvl_drop':
            tvl = tvl * Decimal('0.7') # 30% drop (CRITICAL)
        elif anomaly_type == 'apy_low':
            apy = Decimal('1.5') # Low APY (WARNING)
        elif anomaly_type == 'high_util':
            utilization = Decimal('0.98') # High Util (WARNING)
            
    return {
        'protocol_name': 'felix',
        'tvl_usd': tvl,
        'apy_7d': apy,
        'utilization_rate': utilization
    }

def fetch_hlp_data():
    """
    Mock data for HLP protocol.
    """
    time.sleep(0.5)
    
    tvl = Decimal('50000000.00') + Decimal(random.uniform(-100000, 100000))
    apy = Decimal('5.0') + Decimal(random.uniform(-0.5, 0.5))
    
    # 5% chance of severe TVL drop
    if random.random() < 0.05:
        tvl = tvl * Decimal('0.6') 

    return {
        'protocol_name': 'hlp',
        'tvl_usd': tvl,
        'apy_7d': apy,
        'utilization_rate': None # HLP might not be a lending protocol
    }

# --- CORE LOGIC ---

def process_protocol_data(db: Session, data: dict):
    """
    Ingests data, saves snapshot, and checks for anomalies.
    """
    name = data['protocol_name']
    
    # 1. Fetch previous snapshot for comparison (For TVL Drop)
    # We look for the most recent snapshot before THIS one (which isn't saved yet)
    last_snapshot = db.query(ProtocolSnapshot).filter(
        ProtocolSnapshot.protocol_name == name
    ).order_by(ProtocolSnapshot.timestamp.desc()).first()

    # 2. Check for Anomalies
    alerts = []
    
    # TVL Drop Check (Current vs Last Known)
    if last_snapshot and last_snapshot.tvl_usd > 0:
        drop_percent = (last_snapshot.tvl_usd - data['tvl_usd']) / last_snapshot.tvl_usd
        if drop_percent > CRITICAL_TVL_DROP_PERCENT:
            alerts.append({
                'type': 'tvl_drop',
                'severity': 'critical',
                'message': f"TVL dropped by {drop_percent*100:.2f}% (Threshold: 20%)"
            })

    # APY Check
    if data['apy_7d'] < WARNING_APY_THRESHOLD:
        alerts.append({
            'type': 'apy_low',
            'severity': 'warning',
            'message': f"APY is {data['apy_7d']:.2f}% (Threshold: <2%)"
        })

    # Utilization Check
    if data['utilization_rate'] and data['utilization_rate'] > WARNING_UTILIZATION_THRESHOLD:
        alerts.append({
            'type': 'utilization_high',
            'severity': 'warning',
            'message': f"Utilization is {data['utilization_rate']*100:.2f}% (Threshold: >95%)"
        })

    # 3. Persist Snapshot
    new_snapshot = ProtocolSnapshot(
        protocol_name=name,
        tvl_usd=data['tvl_usd'],
        apy_7d=data['apy_7d'],
        utilization_rate=data['utilization_rate']
    )
    db.add(new_snapshot)
    
    # 4. Persist Alerts
    for alert in alerts:
        logger.warning(f"ALERT TRIGGERED for {name}: {alert['message']}")
        new_alert = ProtocolAlert(
            protocol_name=name,
            alert_type=alert['type'],
            severity=alert['severity'],
            message=alert['message']
        )
        db.add(new_alert)

    try:
        db.commit()
        logger.info(f"Successfully processed snapshot for {name}")
    except Exception as e:
        logger.error(f"Failed to commit data for {name}: {e}")
        db.rollback()

def run_ingestion():
    """
    Main function to run one round of data collection.
    """
    logger.info("Starting ingestion cycle...")
    db = SessionLocal()
    
    try:
        # Fetch Felix
        try:
            felix_data = fetch_felix_data()
            process_protocol_data(db, felix_data)
        except Exception as e:
            logger.error(f"Error fetching/processing Felix: {e}")

        # Fetch HLP
        try:
            hlp_data = fetch_hlp_data()
            process_protocol_data(db, hlp_data)
        except Exception as e:
            logger.error(f"Error fetching/processing HLP: {e}")
            
    finally:
        db.close()
        logger.info("Ingestion cycle complete.")

if __name__ == "__main__":
    # If run directly, just do one pass
    run_ingestion()
