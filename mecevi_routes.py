import psycopg2
import random
from fastapi import APIRouter, HTTPException, Depends, Body
from database import kursor, konekcija
from models import Ekipa, StatusMeca, Mec
from auth_dependency import trenutni_korisnik

router = APIRouter()

def napravi_prazne_setove(mec_id):
    for broj in [1, 2, 3]:
        kursor.execute(
            "INSERT INTO setovi (mec_id, broj_seta, poeni_ekipa1, poeni_ekipa2, zavrsen_set) VALUES (%s, %s, 0, 0, FALSE)",
            (mec_id, broj)
        )

def napravi_parove_i_mecevi(lista_id_ekipa, runda):
    random.shuffle(lista_id_ekipa)
    mecevi_kreirani = []
    
    for i in range(0, len(lista_id_ekipa) - 1, 2):
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, runda, faza) VALUES (%s, %s, %s, %s, 'nokaut') RETURNING id",
            (lista_id_ekipa[i], lista_id_ekipa[i+1], "Ceka", runda)
        )
        mec_id = kursor.fetchone()[0]
        napravi_prazne_setove(mec_id)
        mecevi_kreirani.append((lista_id_ekipa[i], lista_id_ekipa[i+1]))
    
    if len(lista_id_ekipa) % 2 == 1:
        bye_ekipa = lista_id_ekipa[-1]
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, pobjednik, runda, faza) VALUES (%s, %s, 'Zavrsen', %s, %s, 'nokaut') RETURNING id",
            (bye_ekipa, None, bye_ekipa, runda)
        )
        mec_id = kursor.fetchone()[0]
        mecevi_kreirani.append((bye_ekipa, "BYE"))
    
    return mecevi_kreirani

@router.post("/zrijeb")
def napravi_zrijeb(korisnik: str = Depends(trenutni_korisnik)):
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
def napravi_sledeci_krug(korisnik: str = Depends(trenutni_korisnik)):
    
    kursor.execute("SELECT MAX(runda) FROM mecevi")
    rezultat_runde = kursor.fetchone()[0]
    if rezultat_runde is None:
        raise HTTPException(status_code=400, detail="Turnir ili zrijeb jos uvijek nisu zapoceti")
    trenutna_runda = rezultat_runde
    kursor.execute(
        "SELECT COUNT(*) FROM mecevi WHERE faza='nokaut' AND runda = %s AND status != 'Zavrsen'",
        (trenutna_runda,)
    )
    nezavrseni = kursor.fetchone()[0]
    
    if nezavrseni > 0:
        raise HTTPException(status_code=400, detail="Nisu svi mecevi ove runde zavrseni")
    
    kursor.execute(
        "SELECT pobjednik FROM mecevi WHERE faza='nokaut' AND runda = %s",
        (trenutna_runda,)
    )
    pobjednici = [p[0] for p in kursor.fetchall()]
    
    if len(pobjednici) == 1:
        return {"poruka": f"Turnir zavrsen! Pobjednik: {pobjednici[0]}"}

    nova_runda = trenutna_runda +1
    novi_mecevi = []
    for i in range(0, len(pobjednici) - 1, 2):
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, runda, faza) VALUES (%s, %s, %s, %s, 'nokaut') RETURNING id",
            (pobjednici[i], pobjednici[i+1], "Ceka", nova_runda)
        )
        mec_id = kursor.fetchone()[0]
        napravi_prazne_setove(mec_id)
        novi_mecevi.append((pobjednici[i], pobjednici[i+1]))
    
    konekcija.commit()
    return {"poruka": f"Runda {nova_runda} kreirana", "mecevi": novi_mecevi}

@router.put("/mecevi/{id}/pocni")
def pocni_mec(
    id: int,
    servirajuca_ekipa: int | None = Body(default=None, embed=True),
    korisnik: str = Depends(trenutni_korisnik)
):
    kursor.execute("SELECT status FROM mecevi WHERE id = %s", (id,))
    red = kursor.fetchone()
    
    if red is None:
        raise HTTPException(status_code=404, detail="Mec ne postoji")

    if servirajuca_ekipa is not None and servirajuca_ekipa not in [1, 2]:
        raise HTTPException(status_code=400, detail="Prvi servis mora biti ekipa 1 ili ekipa 2")
    
    if red[0] == "Zavrsen":
        raise HTTPException(status_code=400, detail="Mec je vec zavrsen")

    kursor.execute("SELECT broj_terena FROM turnir WHERE id = 1")
    konfiguracija = kursor.fetchone()
    if konfiguracija is None:
        raise HTTPException(status_code=400, detail="Turnir jos nije podesen")

    broj_terena = konfiguracija[0]
    kursor.execute("SELECT COUNT(*) FROM mecevi WHERE status = 'U_toku'")
    mecevi_u_toku = kursor.fetchone()[0]
    if red[0] == "Ceka" and mecevi_u_toku >= broj_terena:
        raise HTTPException(status_code=400, detail="Svi tereni su trenutno zauzeti")

    kursor.execute("SELECT teren FROM raspored WHERE mec_id = %s", (id,))
    raspored = kursor.fetchone()
    if raspored is not None:
        teren = raspored[0]
        kursor.execute("""
            SELECT COUNT(*)
            FROM mecevi m
            JOIN raspored r ON r.mec_id = m.id
            WHERE m.status = 'U_toku' AND r.teren = %s
        """, (teren,))
        if kursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail=f"Teren {teren} je trenutno zauzet")
    
    if servirajuca_ekipa is None:
        kursor.execute("UPDATE mecevi SET status = 'U_toku' WHERE id = %s", (id,))
    else:
        kursor.execute(
            "UPDATE mecevi SET status = 'U_toku', servirajuca_ekipa = %s WHERE id = %s",
            (servirajuca_ekipa, id)
        )
    konekcija.commit()
    return {"poruka": "Mec zapocet", "servirajuca_ekipa": servirajuca_ekipa}