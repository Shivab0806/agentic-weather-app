from fastapi import FastAPI
from backend.api.routes import router
app=FastAPI(title="Agentic Weather AI")
app.include_router(router,prefix="/weather")
