# encoding: utf-8

from pydantic import BaseModel

from helper import get_kas_price
from server import app, kobrad_client


class MarketCapResponse(BaseModel):
    marketcap: int = 12000132


@app.get("/info/marketcap", response_model=MarketCapResponse | str, tags=["Kobra network info"])
async def get_marketcap(stringOnly: bool = False):
    """
    Get $KOBRA price and market cap. Price info is from coingecko.com
    """
    kas_price = await get_kas_price()
    resp = await kobrad_client.request("getCoinSupplyRequest")
    mcap = round(float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 100000000 * kas_price)

    if not stringOnly:
        return {
            "marketcap": mcap
        }
    else:
        if mcap < 1000000000:
            return f"{round(mcap / 1000000, 1)}M"
        else:
            return f"{round(mcap / 1000000000, 1)}B"
