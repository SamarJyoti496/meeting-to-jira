from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from app.config import settings
from app.utils.logger import logger
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
     logger.info("Starting Meeting-to-Jira System")
     os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

     yield

     logger.info("Shutting down Meeting-to-Jira System")


app = FastAPI(
     title=settings.APP_NAME,
     version=settings.VERSION,
     description="Automatically convert meeting recordingd to Jira tickets",
     lifespan=lifespan
)

app.add_middleware(
     CORSMiddleware,
     allow_origins=["http://localhost:3000", "http://localhost"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if __name__=="__main__":
     uvicorn.run(
          "app.main:app",
          host="0.0.0.0",
          port=8000,
          reload=settings.DEBUG,
          log_level="debug" if settings.DEBUG else "info"
     )