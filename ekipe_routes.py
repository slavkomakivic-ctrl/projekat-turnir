import psycopg2
from fastapi import APIRouter, HTTPException
from database import kursor, konekcija
from models import Ucesnik, Ekipa
from psycopg2.errors import UniqueViolation

router = APIRouter()

@router.post("/prijava_ekipe")
def prijava_ekipe(podaci: Ekipa):
    try:
        kursor.execute(
            "INSERT INTO ekipa (naziv, grad, kontakt) VALUES (%s, %s, %s) RETURNING id",
            (podaci.naziv, podaci.grad, podaci.kontakt)
        )
        ekipa_id = kursor.fetchone()[0]

        for clan in podaci.clanovi:
            kursor.execute(
                "INSERT INTO imena_ucesnika (ekipa_id, ime) VALUES (%s, %s)",
                (ekipa_id, clan.ime)
            )

        konekcija.commit()

        broj_clanova = len(podaci.clanovi)
        if broj_clanova == 5:
            poruka = "clanova"
        else:
            poruka = "clana"
        return {"poruka": f"Ekipa {podaci.naziv} je prijavljena sa {broj_clanova} {poruka}."}
    except UniqueViolation:
        konekcija.rollback()
        raise HTTPException(status_code=400, detail=f"Greska pri registraciji: Ekipa sa tim nazivom ili kontaktom vec postoji")
    except Exception:
       konekcija.rollback()
       raise

@router.get("/prikazi_ekipe")
def prikazi_ekipe():
    kursor.execute("SELECT * FROM ekipa")
    ekipe = kursor.fetchall()
    return {"ekipe": ekipe}