# encoding: utf-8

from fastapi import Path, HTTPException
from pydantic import BaseModel

from server import app, kobrad_client


class BalanceResponse(BaseModel):
    address: str = "kobra:qrvwazapajffhp5mmc65uwh8d887yckdhheu3hayqrzhf5mt3h7cxad0zuyzh"
    balance: int = 1524000


@app.get("/addresses/{kobraAddress}/balance", response_model=BalanceResponse, tags=["Kobra addresses"])
async def get_balance_from_kobra_address(
        kobraAddress: str = Path(
            description="Kobra address as string e.g. kobra:qrvwazapajffhp5mmc65uwh8d887yckdhheu3hayqrzhf5mt3h7cxad0zuyzh",
            regex="^kobra\:[a-z0-9]{61,63}$")):
    """
    Get balance for a given kobra address
    """
    resp = await kobrad_client.request("getBalanceByAddressRequest",
                                       params={
                                           "address": kobraAddress
                                       })

    try:
        resp = resp["getBalanceByAddressResponse"]
    except KeyError:
        if "getUtxosByAddressesResponse" in resp and "error" in resp["getUtxosByAddressesResponse"]:
            raise HTTPException(status_code=400, detail=resp["getUtxosByAddressesResponse"]["error"])
        else:
            raise

    try:
        balance = int(resp["balance"])

    # return 0 if address is ok, but no utxos there
    except KeyError:
        balance = 0

    return {
        "address": kobraAddress,
        "balance": balance
    }
