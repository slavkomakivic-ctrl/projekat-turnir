import sqlite3
import random
from fastapi import APIRouter, HTTPException, Depends
from database import kursor, konekcija
from models import Ekipa, StatusMeca, Mec

router = APIRouter()

def napravi_prazne_setove(mec_id):
    for broj in [1, 2, 3]:
        kursor.execute(
            "INSERT INTO setovi (mec_id, broj_seta, poeni_ekipa1, poeni_ekipa2, zavrsen_set) VALUES (?, ?, ?, ?, ?)",
            (mec_id, broj, 0, 0, False)
        )

def napravi_parove_i_mecevi(lista_id_ekipa, runda):
    random.shuffle(lista_id_ekipa)
    mecevi_kreirani = []
    
    for i in range(0, len(lista_id_ekipa) - 1, 2):
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, runda) VALUES (?, ?, ?, ?)",
            (lista_id_ekipa[i], lista_id_ekipa[i+1], "Ceka", runda)
        )
        mec_id = kursor.lastrowid
        napravi_prazne_setove(mec_id)
        mecevi_kreirani.append((lista_id_ekipa[i], lista_id_ekipa[i+1]))
    
    if len(lista_id_ekipa) % 2 == 1:
        bye_ekipa = lista_id_ekipa[-1]
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, pobjednik, runda) VALUES (?, ?, ?, ?, ?)",
            (bye_ekipa, None, "Zavrsen", bye_ekipa, runda)
        )
        mecevi_kreirani.append((bye_ekipa, "BYE"))
    
    return mecevi_kreirani

@router.post("/zrijeb")
def napravi_zrijeb():
    kursor.execute("SELECT COUNT(*) FROM mecevi")
    broj_meceva = kursor.fetchone()[0]
    
    if broj_meceva > 0:
        raise HTTPException(status_code=400, detail="Zrijeb je vec izvrsen!")

    kursor.execute("SELECT id FROM ekipa")
    ekipe = kursor.fetchall()
    id_ekipa = [e[0] for e in ekipe]
    
    if len(id_ekipa) < 2:
        raise HTTPException(status_code=400, detail="Potrebno je bar 2 ekipe za zrijeb")
    
    mecevi_kreirani = napravi_parove_i_mecevi(id_ekipa, 1)
    konekcija.commit()

    return {"poruka": "Zrijeb izvrsen", "mecevi": mecevi_kreirani}

@router.get("/prikazi_zrijeb")
def prikazi_zrijeb():
    kursor.execute("SELECT * FROM mecevi")
    parovi = kursor.fetchall()
    return {"parovi": parovi}

@router.post("/sledeci_krug")
def napravi_sledeci_krug():
    
    kursor.execute("SELECT MAX(runda) FROM mecevi WHERE faza='nokaut'")
    trenutna_runda = kursor.fetchone()[0]
    
    kursor.execute(
        "SELECT COUNT(*) FROM mecevi WHERE faza='nokaut' AND runda = ? AND status != 'Zavrsen'",
        (trenutna_runda,)
    )
    nezavrseni = kursor.fetchone()[0]
    
    if nezavrseni > 0:
        raise HTTPException(status_code=400, detail="Nisu svi mecevi ove runde zavrseni")
    
    kursor.execute(
        "SELECT pobjednik FROM mecevi WHERE faza='nokaut' AND runda = ?",
        (trenutna_runda,)
    )
    pobjednici = [p[0] for p in kursor.fetchall()]
    
    if len(pobjednici) == 1:
        return {"poruka": f"Turnir zavrsen! Pobjednik: {pobjednici[0]}"}

    nova_runda = trenutna_runda +1
    novi_mecevi = []
    for i in range(0, len(pobjednici) - 1, 2):
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, runda, faza) VALUES (?, ?, ?, ?, ?)",
            (pobjednici[i], pobjednici[i+1], "Ceka", nova_runda, "nokaut")
        )
        mec_id = kursor.lastrowid
        napravi_prazne_setove(mec_id)
        novi_mecevi.append((pobjednici[i], pobjednici[i+1]))
    
    konekcija.commit()
    return {"poruka": f"Runda {nova_runda} kreirana", "mecevi": novi_mecevi}