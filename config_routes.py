import psycopg2
from psycopg2 import Error
from fastapi import APIRouter, HTTPException, Depends
from database import kursor, konekcija
from models import Turnir
from auth_dependency import trenutni_korisnik

router = APIRouter()

@router.post("/config")
def konfiguracija_turnira(turnir: Turnir, korisnik: str = Depends(trenutni_korisnik)):
    try:    
        kursor.execute("SELECT COUNT(*) FROM turnir")
        if kursor.fetchone()[0] > 0:
            kursor.execute(
                "UPDATE turnir SET naziv=%s, broj_terena=%s, dan_turnira=%s, trajanje_meca=%s WHERE id=1",
                (turnir.naziv, turnir.broj_terena, turnir.dan_turnira, turnir.trajanje_meca)
            )
        else:
            kursor.execute(
                "INSERT INTO turnir (naziv, broj_terena, dan_turnira, trajanje_meca) VALUES (%s, %s, %s, %s)",
                (turnir.naziv, turnir.broj_terena, turnir.dan_turnira, turnir.trajanje_meca)
            )
        konekcija.commit()
        return {"poruka": "Konfiguracija sacuvana"}
    except Error as e:
        konekcija.rollback()
        raise HTTPException(status_code=400, detail=f"Greska: {str(e)}")

@router.get("/turnir_config")
def prikazi_konfiguracije():
    try:    
        kursor.execute(
            "SELECT * FROM turnir"
        )
        konfiguracije = kursor.fetchall()
        return {"konfiguracije": konfiguracije}
    except Error as e:
        konekcija.rollback()
        raise HTTPException(status_code=400, detail=f"Greska: {str(e)}")