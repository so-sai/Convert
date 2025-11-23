# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from .security.kms import KMS
from .storage.adapter import StorageAdapter

logging.basicConfig(level=logging.INFO)
app = FastAPI()
DB_PATH = Path("data/mds.db")
kms = KMS(DB_PATH)
adapter = StorageAdapter(DB_PATH, kms)

class UnlockRequest(BaseModel):
    passkey: str

class EventRequest(BaseModel):
    type: str
    id: str
    payload: dict

@app.post("/vault/init")
async def init(req: UnlockRequest):
    await kms.initialize_vault(req.passkey)
    return {"status": "ok"}

@app.post("/vault/unlock")
async def unlock(req: UnlockRequest):
    if await kms.unlock_vault(req.passkey): return {"status": "unlocked"}
    raise HTTPException(401)

@app.post("/events")
async def save(req: EventRequest):
    try:
        eid = await adapter.save_event(req.type, req.id, req.payload)
        return {"id": eid}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/events")
async def get():
    return await adapter.get_events()
