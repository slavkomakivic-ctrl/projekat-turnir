import psycopg2
from psycopg2 import Error
from fastapi import APIRouter, HTTPException, Depends
from database import kursor, konekcija
from models import Setovi, Broj_seta
from auth_dependency import trenutni_korisnik

router = APIRouter()

@router.put("/setovi/{id}")
def azuriraj_set(id: int, set_podaci: Setovi, korisnik: str = Depends(trenutni_korisnik)):
    try:
        kursor.execute(
            "UPDATE setovi SET poeni_ekipa1 = %s, poeni_ekipa2 = %s, zavrsen_set = %s WHERE id = %s",
            (set_podaci.poeni_ekipa1, set_podaci.poeni_ekipa2, set_podaci.zavrsen_set, id)
        )
        konekcija.commit()
        
        kursor.execute("SELECT mec_id FROM setovi WHERE id = %s", (id,))
        mec_id = kursor.fetchone()[0]

        kursor.execute("UPDATE mecevi SET status = 'U_toku' WHERE id = %s ", (mec_id,))
        if set_podaci.poen_ekipa in [1, 2]:
            kursor.execute(
                "UPDATE mecevi SET servirajuca_ekipa = %s WHERE id = %s",
                (set_podaci.poen_ekipa, mec_id)
            )
        elif set_podaci.servirajuca_ekipa in [1, 2]:
            kursor.execute(
                "UPDATE mecevi SET servirajuca_ekipa = %s WHERE id = %s",
                (set_podaci.servirajuca_ekipa, mec_id)
            )
        konekcija.commit()
        
        kursor.execute("""
            SELECT poeni_ekipa1, poeni_ekipa2 FROM setovi 
            WHERE mec_id = %s AND zavrsen_set = TRUE
        """, (mec_id,))
        zavrseni_setovi = kursor.fetchall()
        
        pobjede_ekipa1 = sum(1 for s in zavrseni_setovi if s[0] > s[1])
        pobjede_ekipa2 = sum(1 for s in zavrseni_setovi if s[1] > s[0])
        
        if pobjede_ekipa1 == 2 or pobjede_ekipa2 == 2:
            kursor.execute("SELECT ekipa1_id, ekipa2_id FROM mecevi WHERE id = %s", (mec_id,))
            ekipa1, ekipa2 = kursor.fetchone()
            pobjednik = ekipa1 if pobjede_ekipa1 == 2 else ekipa2
            
            kursor.execute(
                "UPDATE mecevi SET pobjednik = %s, status = 'Zavrsen' WHERE id = %s",
                (pobjednik, mec_id)
            )
            konekcija.commit()
        
        kursor.execute("SELECT status FROM mecevi WHERE id = %s", (mec_id,))
        status_meca = kursor.fetchone()[0]
        return {"poruka": "Set azuriran", "status_meca": status_meca}
    except Error:
            konekcija.rollback()
            raise HTTPException(status_code=400, detail=f"Greska")

@router.get("/setovi")
def prikazi_setove():
    kursor.execute("SELECT * FROM setovi")
    prikaz = kursor.fetchall()
    return {"setovi": prikaz}
