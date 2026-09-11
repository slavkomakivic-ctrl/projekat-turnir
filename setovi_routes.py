import sqlite3
import random
from fastapi import APIRouter, HTTPException, Depends
from database import kursor, konekcija
from models import Setovi, Broj_seta, Mec

router = APIRouter()

@router.put("/setovi/{id}")
def azuriraj_set(id: int, set_podaci: Setovi):
    try:
        kursor.execute(
            "UPDATE setovi SET poeni_ekipa1 = ?, poeni_ekipa2 = ?, zavrsen_set = ? WHERE id = ?",
            (set_podaci.poeni_ekipa1, set_podaci.poeni_ekipa2, set_podaci.zavrsen_set, id)
        )
        konekcija.commit()
        
        kursor.execute("SELECT mec_id FROM setovi WHERE id = ?", (id,))
        mec_id = kursor.fetchone()[0]

        kursor.execute("UPDATE mecevi SET status = 'U_toku' WHERE id = ? ", (mec_id,))
        konekcija.commit()
        
        kursor.execute("""
            SELECT poeni_ekipa1, poeni_ekipa2 FROM setovi 
            WHERE mec_id = ? AND zavrsen_set = 1
        """, (mec_id,))
        zavrseni_setovi = kursor.fetchall()
        
        pobjede_ekipa1 = sum(1 for s in zavrseni_setovi if s[0] > s[1])
        pobjede_ekipa2 = sum(1 for s in zavrseni_setovi if s[1] > s[0])
        
        if pobjede_ekipa1 == 2 or pobjede_ekipa2 == 2:
            kursor.execute("SELECT ekipa1_id, ekipa2_id FROM mecevi WHERE id = ?", (mec_id,))
            ekipa1, ekipa2 = kursor.fetchone()
            pobjednik = ekipa1 if pobjede_ekipa1 == 2 else ekipa2
            
            kursor.execute(
                "UPDATE mecevi SET pobjednik = ?, status = 'Zavrsen' WHERE id = ?",
                (pobjednik, mec_id)
            )
            konekcija.commit()
        
        return {"poruka": "Set azuriran"}
    except sqlite3.IntegrityError as e:
            konekcija.rollback()
            raise HTTPException(status_code=400, detail=f"Greska: {str(e)}")

@router.get("/setovi")
def prikazi_setove():
    kursor.execute("SELECT * FROM setovi")
    prikaz = kursor.fetchall()
    return {"setovi": prikaz}
