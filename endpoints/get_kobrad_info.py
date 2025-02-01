# encoding: utf-8
import hashlib

from pydantic import BaseModel

from server import app, kobrad_client


class KobradInfoResponse(BaseModel):
    mempoolSize: str = "1"
    serverVersion: str = "1.0.4"
    isUtxoIndexed: bool = True
    isSynced: bool = True
    p2pIdHashed : str = "36a17cd8644eef34fc7fe4719655e06dbdf117008900c46975e66c35acd09b01"


@app.get("/info/kobrad", response_model=KobradInfoResponse, tags=["Kobra network info"])
async def get_kobrad_info():
    """
    Get some information for kobrad instance, which is currently connected.
    """
    resp = await kobrad_client.request("getInfoRequest")
    p2p_id = resp["getInfoResponse"].pop("p2pId")
    resp["getInfoResponse"]["p2pIdHashed"] = hashlib.sha256(p2p_id.encode()).hexdigest()
    return resp["getInfoResponse"]
