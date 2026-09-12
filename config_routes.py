import sqlite3
import random
from fastapi import APIRouter, HTTPException, Depends
from database import kursor, konekcija
from models import Turnir

router = APIRouter()

@router.post("/config")
def konfiguracija_turnira(turnir: Turnir):
    kursor.execute(
        "INSERT INTO turnir (naziv, broj_terena, dan_turnira, trajanje_meca) VALUES (?, ?, ?, ?)",
        (turnir.naziv, turnir.broj_terena, turnir.dan_turnira, turnir.trajanje_meca)
    )
    konekcija.commit()

@router.get("/turnir_config")
def prikazi_konfiguracije():
    kursor.execute(
        "SELECT * FROM turnir"
    )
    konfiguracije = kursor.fetchall()
    return {"konfiguracije": konfiguracije}
