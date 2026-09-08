from fastapi import FastAPI
import database
from routes import router

app = FastAPI()
app.include_router(router)