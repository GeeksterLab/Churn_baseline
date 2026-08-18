"""
POST /health → simple health check endpoint.
"""

# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝
from core.settings import settings

# ╔════════════════════════════════════════════════════════════╗
# ║ 🌐 API
# ╚════════════════════════════════════════════════════════════╝
from fastapi import FastAPI
from contextlib import asynccontextmanager
import joblib


# ═════════════════════ MODEL LOADING ═════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(settings.BASELINE_PATH)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ╔════════════════════════════════════════════════════════════╗
# ║ 🥷 MIDDLEWARES
# ╚════════════════════════════════════════════════════════════╝
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ╔════════════════════════════════════════════════════════════╗
# ║ 🛣️ ROUTERS
# ╚════════════════════════════════════════════════════════════╝
from api.model import model_predict, model_predict_batch, model_info, model_upload
from api.auth import user_login, refresh_token

app.include_router(model_predict)
app.include_router(model_predict_batch)
app.include_router(model_upload)
app.include_router(model_info)
app.include_router(user_login)
app.include_router(refresh_token)


# ╔════════════════════════════════════════════════════════════╗
# ║ ⛑️ HEALTH CHECK
# ╚════════════════════════════════════════════════════════════╝
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "demo_mode": settings.DEMO_MODE,
    }
