from fastapi import FastAPI
from app.config import settings
from app.routers.vehicles import router as vehicles_router
from app.routers.payments import router as payments_router
from app.infrastructure.db import engine
from app.domain.models import Base

app = FastAPI(title=settings.app_name)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(vehicles_router, prefix="/vehicles", tags=["vehicles"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])

@app.on_event("startup")
def on_startup():
    # Em produção, prefira Alembic. Para simplicidade, criamos o schema se não existir.
    Base.metadata.create_all(bind=engine)
