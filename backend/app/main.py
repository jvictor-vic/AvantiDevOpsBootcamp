from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers import auth, condominio, morador, ocorrencia, rivalidade, ws
from app.services.ws_manager import manager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await manager.shutdown()


app = FastAPI(
    title="CondoCombat API",
    description="ERP satírico para gerenciar fofocas, rixas e tretas de condomínio",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(condominio.router)
app.include_router(morador.router)
app.include_router(ocorrencia.router)
app.include_router(rivalidade.router)
app.include_router(ws.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "CondoCombat API", "version": "0.1.0"}
