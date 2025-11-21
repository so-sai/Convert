import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import setup_logging
from src.core.services.dashboard import MDSDashboardService
from src.core.schemas.events import SystemHealth, SystemStats, RecentNote

setup_logging()
logger = logging.getLogger("CORE.API")
mds_service = MDSDashboardService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mds_service.initialize()
    logger.info("MDS v3.1 Dashboard API started")
    yield
    if mds_service.db_manager:
        await mds_service.db_manager.close()

app = FastAPI(title="Project Convert MDS v3.1", version="3.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health", response_model=SystemHealth)
async def health_check():
    return await mds_service.get_system_health()

@app.get("/stats", response_model=SystemStats)
async def get_stats():
    return await mds_service.get_system_stats()

@app.get("/notes/recent", response_model=list[RecentNote])
async def get_recent_notes(limit: int = 5):
    return await mds_service.get_recent_notes(limit)

@app.post("/shutdown")
async def shutdown():
    await asyncio.sleep(0.1)
    return {"status": "shutting_down"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)