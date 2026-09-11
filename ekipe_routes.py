import sqlite3
from fastapi import APIRouter, HTTPException
from database import kursor, konekcija
from models import Ucesnik, Ekipa

router = APIRouter()

@router.post("/prijava_ekipe")
def prijava_ekipe(podaci: Ekipa):
    try:
        kursor.execute(
            "INSERT INTO ekipa (naziv, grad, kontakt) VALUES (?, ?, ?)",
            (podaci.naziv, podaci.grad, podaci.kontakt)
        )
        ekipa_id = kursor.lastrowid

        for clan in podaci.clanovi:
            kursor.execute(
                "INSERT INTO imena_ucesnika (ekipa_id, ime) VALUES (?, ?)",
                (ekipa_id, clan.ime)
            )

        konekcija.commit()

        broj_clanova = len(podaci.clanovi)
        if broj_clanova == 5:
            poruka = "clanova"
        else:
            poruka = "clana"
        return {"poruka": f"Ekipa {podaci.naziv} je prijavljena sa {broj_clanova} {poruka}."}
    except sqlite3.IntegrityError as e:
        konekcija.rollback()
        raise HTTPException(status_code=400, detail=f"Greska pri registraciji: {str(e)}")

@router.get("/prikazi_ekipe")
def prikazi_ekipe():
    kursor.execute("SELECT * FROM ekipa")
    ekipe = kursor.fetchall()
    return {"ekipe": ekipe}