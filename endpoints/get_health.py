# encoding: utf-8
import hashlib
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from dbsession import async_session
from models.Transaction import Transaction
from server import app, kobrad_client


class KobradResponse(BaseModel):
    kobradHost: str = ""
    serverVersion: str = "1.0.4"
    isUtxoIndexed: bool = True
    isSynced: bool = True
    p2pId: str = "1231312"


class HealthResponse(BaseModel):
    kobradServers: List[KobradResponse]


@app.get("/info/health", response_model=HealthResponse, tags=["Kobra network info"])
async def health_state():
    """
    Returns the current hashrate for Kobra network in TH/s.
    """
    await kobrad_client.initialize_all()

    kobrads = []

    async with async_session() as s:
        last_block_time = (await s.execute(select(Transaction.block_time)
                                           .limit(1)
                                           .order_by(Transaction.block_time.desc()))).scalar()

    time_diff = datetime.now() - datetime.fromtimestamp(last_block_time / 1000)

    if time_diff > timedelta(minutes=10):
        raise HTTPException(status_code=500, detail="Transactions not up to date")

    for i, kobrad_info in enumerate(kobrad_client.kobrads):
        kobrads.append({
            "isSynced": kobrad_info.is_synced,
            "isUtxoIndexed": kobrad_info.is_utxo_indexed,
            "p2pId": hashlib.sha256(kobrad_info.p2p_id.encode()).hexdigest(),
            "kobradHost": f"KOBRAD_HOST_{i + 1}",
            "serverVersion": kobrad_info.server_version
        })

    return {
        "kobradServers": kobrads
    }
