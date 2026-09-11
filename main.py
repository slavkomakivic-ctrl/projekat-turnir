from fastapi import FastAPI
import database
from routes import router as auth_router
from ekipe_routes import router as ekipe_router
from mecevi_routes import router as mecevi_router
from setovi_routes import router as setovi_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(ekipe_router)
app.include_router(mecevi_router)
app.include_router(setovi_router)
