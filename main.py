from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
from routes import router as auth_router
from ekipe_routes import router as ekipe_router
from mecevi_routes import router as mecevi_router
from setovi_routes import router as setovi_router
from grupe_routes import router as grupe_router
from config_routes import router as config_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ekipe_router)
app.include_router(mecevi_router)
app.include_router(setovi_router)
app.include_router(grupe_router)
app.include_router(config_router)