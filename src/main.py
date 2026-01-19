from fastapi import FastAPI
from src.database import engine
from src.account.models import BaseModel
import uvicorn
from src.account.views import user_admin
from src.restoran.views import router as restoran_router
app = FastAPI()
app.include_router(prefix="/users", router=user_admin)
app.include_router(restoran_router, prefix="/restoran", tags=["restoran"])



# Создание таблиц при старте
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("manage:app", host="127.0.0.1", port=8000, reload=True)
