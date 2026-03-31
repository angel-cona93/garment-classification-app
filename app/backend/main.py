import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes.images import router as images_router
from routes.filters import router as filters_router
from routes.search import router as search_router
from routes.annotations import router as annotations_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Fashion AI started")
    yield


app = FastAPI(title="Fashion AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images_router)
app.include_router(filters_router)
app.include_router(search_router)
app.include_router(annotations_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
