from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- API Models ---

class ProtocolReview(BaseModel):
    name: str
    tvl_usd: Decimal
    apy_7d: Optional[Decimal]
    status: str 

    model_config = {
        "from_attributes": True
    }

class ProtocolSnapshotResponse(BaseModel):
    timestamp: datetime
    tvl_usd: Decimal
    apy_7d: Optional[Decimal]

    model_config = {
        "from_attributes": True
    }

class AlertResponse(BaseModel):
    id: int
    protocol_name: str
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
