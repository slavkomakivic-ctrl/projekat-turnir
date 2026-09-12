import sqlite3
import random
from fastapi import APIRouter, HTTPException, Depends
from database import kursor, konekcija
from models import Turnir
from mecevi_routes import napravi_parove_i_mecevi

router = APIRouter()

def preporuci_format(broj_ekipa, broj_terena, trajanje_meca, pocetak_min=660, kraj_min=1200):
    if broj_ekipa < 12:
        return {"moguce": False, "poruka": "Potrebno je minimum 12 ekipa za turnir"}

    dostupno_minuta = kraj_min - pocetak_min
    max_meceva = (dostupno_minuta // trajanje_meca) * broj_terena

    najbolja_opcija = None
    for broj_grupa in [2, 4, 8, 16]:
        if broj_grupa > broj_ekipa // 2:
            continue
        osnovna = broj_ekipa // broj_grupa
        ostatak = broj_ekipa % broj_grupa
        if osnovna < 3:
            continue

        velicine = [osnovna + 1 if i < ostatak else osnovna for i in range(broj_grupa)]
        grupni_mecevi = sum(v * (v - 1) // 2 for v in velicine)
        kvalifikovani = broj_grupa * 2
        nokaut_mecevi = kvalifikovani - 1 if kvalifikovani >= 2 else 0
        ukupno = grupni_mecevi + nokaut_mecevi

        if ukupno <= max_meceva:
            if najbolja_opcija is None or broj_grupa > najbolja_opcija["broj_grupa"]:
                najbolja_opcija = {
                    "broj_grupa": broj_grupa,
                    "velicine_grupa": velicine,
                    "kvalifikovani": kvalifikovani,
                    "ukupno_meceva": ukupno,
                }

    if najbolja_opcija is None:
        return {"moguce": False, "poruka": "Previse ekipa za raspolozivo vrijeme/terene"}

    return {
        "moguce": True,
        **najbolja_opcija,
        "potrebno_minuta": najbolja_opcija["ukupno_meceva"] * trajanje_meca / broj_terena,
        "dostupno_minuta": dostupno_minuta
    }


@router.get("/preporuka_formata")
def preporuka():
    kursor.execute("SELECT broj_terena, trajanje_meca FROM turnir WHERE id = 1")
    red = kursor.fetchone()
    
    if red is None:
        raise HTTPException(status_code=400, detail="Turnir jos nije podesen")
    
    broj_terena, trajanje_meca = red
    
    kursor.execute("SELECT COUNT(*) FROM ekipa")
    broj_ekipa = kursor.fetchone()[0]
    
    return preporuci_format(broj_ekipa, broj_terena, trajanje_meca)


@router.post("/napravi_grupe")
def napravi_grupe():
    kursor.execute("SELECT broj_terena, trajanje_meca FROM turnir WHERE id = 1")
    red = kursor.fetchone()
    
    if red is None:
        raise HTTPException(status_code=400, detail="Turnir jos nije podesen")
    
    broj_terena, trajanje_meca = red
    
    kursor.execute("SELECT COUNT(*) FROM grupe")
    if kursor.fetchone()[0] > 0:
        raise HTTPException(status_code=400, detail="Grupe su vec napravljene")

    kursor.execute("SELECT id FROM ekipa")
    id_ekipa = [e[0] for e in kursor.fetchall()]
    broj_ekipa = len(id_ekipa)

    format_ = preporuci_format(broj_ekipa, broj_terena, trajanje_meca)
    if not format_["moguce"]:
        raise HTTPException(status_code=400, detail=format_.get("poruka", "Format nije moguc"))

    random.shuffle(id_ekipa)
    velicine = format_["velicine_grupa"]

    pokazivac = 0
    for i, velicina in enumerate(velicine):
        naziv_grupe = f"Grupa {chr(65 + i)}"  # A, B, C...
        kursor.execute("INSERT INTO grupe (naziv) VALUES (?)", (naziv_grupe,))
        grupa_id = kursor.lastrowid

        ekipe_u_grupi = id_ekipa[pokazivac: pokazivac + velicina]
        pokazivac += velicina

        for ekipa_id in ekipe_u_grupi:
            kursor.execute("UPDATE ekipa SET grupa_id = ? WHERE id = ?", (grupa_id, ekipa_id))

    konekcija.commit()
    return {"poruka": "Grupe napravljene", "detalji": format_}


@router.get("/prikazi_grupe")
def prikazi_grupe():
    kursor.execute("""
        SELECT grupe.naziv, ekipa.naziv, ekipa.id
        FROM grupe
        JOIN ekipa ON ekipa.grupa_id = grupe.id
        ORDER BY grupe.naziv
    """)
    return {"grupe": kursor.fetchall()}

def napravi_prazne_setove(mec_id):
    for broj in [1, 2, 3]:
        kursor.execute(
            "INSERT INTO setovi (mec_id, broj_seta, poeni_ekipa1, poeni_ekipa2, zavrsen_set) VALUES (?, ?, ?, ?, ?)",
            (mec_id, broj, 0, 0, False)
        )
def round_robin_rasporedi(ekipe):
    ekipe = ekipe[:]
    if len(ekipe) % 2 == 1:
        ekipe.append(None)  # "bye" u okviru kola, ne cijelog turnira
    n = len(ekipe)
    kola = []
    for _ in range(n - 1):
        parovi = []
        for i in range(n // 2):
            t1, t2 = ekipe[i], ekipe[n - 1 - i]
            if t1 is not None and t2 is not None:
                parovi.append((t1, t2))
        kola.append(parovi)
        ekipe = [ekipe[0]] + [ekipe[-1]] + ekipe[1:-1]
    return kola

@router.post("/napravi_meceve_grupa")
def napravi_meceve_grupa():
    kursor.execute("SELECT COUNT(*) FROM mecevi WHERE faza='grupna'")
    if kursor.fetchone()[0] > 0:
        raise HTTPException(status_code=400, detail="Grupni mecevi su vec napravljeni")

    kursor.execute("SELECT id FROM grupe ORDER BY id")
    grupe = [g[0] for g in kursor.fetchall()]

    kola_po_grupi = {}
    max_kola = 0
    for grupa_id in grupe:
        kursor.execute("SELECT id FROM ekipa WHERE grupa_id = ?", (grupa_id,))
        ekipe = [e[0] for e in kursor.fetchall()]
        kola = round_robin_rasporedi(ekipe)
        kola_po_grupi[grupa_id] = kola
        max_kola = max(max_kola, len(kola))

    for kolo_broj in range(max_kola):
        for grupa_id in grupe:
            kola = kola_po_grupi[grupa_id]
            if kolo_broj < len(kola):
                for ekipa1, ekipa2 in kola[kolo_broj]:
                    kursor.execute(
                        "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, faza, grupa_id, kolo) VALUES (?, ?, ?, ?, ?, ?)",
                        (ekipa1, ekipa2, "Ceka", "grupna", grupa_id, kolo_broj + 1)
                    )
                    napravi_prazne_setove(kursor.lastrowid)

    konekcija.commit()
    return {"poruka": "Grupni mecevi napravljeni po kolima"}

def napravi_seeded_osminu(prvi_mjesto, drugo_mjesto):
    n = len(prvi_mjesto)
    parovi = []
    for i in range(n):
        protivnik_drugog = drugo_mjesto[n - 1 - i]  # A1 protiv H2, B1 protiv G2...
        parovi.append((prvi_mjesto[i], protivnik_drugog))
    return parovi

def izracunaj_tabelu_grupe(grupa_id):
    kursor.execute("SELECT id FROM ekipa WHERE grupa_id = ?", (grupa_id,))
    ekipe = [e[0] for e in kursor.fetchall()]

    tabela = {e: {"pobjede": 0, "setovi_izgubljeni": 0, "poena_primljeno": 0} for e in ekipe}

    kursor.execute(
        "SELECT id, ekipa1_id, ekipa2_id, pobjednik FROM mecevi WHERE faza='grupna' AND grupa_id=? AND status='Zavrsen'",
        (grupa_id,)
    )
    for mec_id, e1, e2, pobjednik in kursor.fetchall():
        if pobjednik in tabela:
            tabela[pobjednik]["pobjede"] += 1

        kursor.execute(
            "SELECT poeni_ekipa1, poeni_ekipa2 FROM setovi WHERE mec_id=? AND zavrsen_set=1",
            (mec_id,)
        )
        for p1, p2 in kursor.fetchall():
            if p1 > p2:
                tabela[e2]["setovi_izgubljeni"] += 1
            else:
                tabela[e1]["setovi_izgubljeni"] += 1
            tabela[e1]["poena_primljeno"] += p2
            tabela[e2]["poena_primljeno"] += p1

    poredak = sorted(
        tabela.items(),
        key=lambda x: (-x[1]["pobjede"], x[1]["setovi_izgubljeni"], x[1]["poena_primljeno"])
    )
    return poredak

@router.get("/tabela_grupe/{grupa_id}")
def tabela_grupe(grupa_id: int):
    return {"tabela": izracunaj_tabelu_grupe(grupa_id)}

@router.post("/napravi_nokaut_iz_grupa")
def napravi_nokaut_iz_grupa():
    kursor.execute("SELECT id FROM grupe")
    grupe = [g[0] for g in kursor.fetchall()]

    prvi_mjesto = []
    drugo_mjesto = []
    for grupa_id in sorted(grupe):
        poredak = izracunaj_tabelu_grupe(grupa_id)   # <- I DALJE poziva istu funkciju
        prvi_mjesto.append(poredak[0][0])
        drugo_mjesto.append(poredak[1][0])

    parovi = napravi_seeded_osminu(prvi_mjesto, drugo_mjesto)

    novi_mecevi = []
    for ekipa1, ekipa2 in parovi:
        kursor.execute(
            "INSERT INTO mecevi (ekipa1_id, ekipa2_id, status, runda, faza) VALUES (?, ?, ?, ?, ?)",
            (ekipa1, ekipa2, "Ceka", 1, "nokaut")
        )
        mec_id = kursor.lastrowid
        napravi_prazne_setove(mec_id)
        novi_mecevi.append((ekipa1, ekipa2))
    konekcija.commit()
    return {"poruka": "Nokaut faza kreirana", "mecevi": novi_mecevi}

@router.post("/generisi_raspored")
def generisi_raspored():
    kursor.execute("SELECT broj_terena, trajanje_meca, dan_turnira FROM turnir WHERE id=1")
    broj_terena, trajanje, dan = kursor.fetchone()

    kursor.execute("SELECT id FROM mecevi WHERE faza='grupna' ORDER BY kolo, id")
    mecevi = [m[0] for m in kursor.fetchall()]

    pocetak_min = 11 * 60  # 11:00, prilagodi po potrebi
    for slot, mec_id in enumerate(mecevi):
        teren = (slot % broj_terena) + 1
        vrijeme_min = pocetak_min + (slot // broj_terena) * trajanje
        vrijeme = f"{vrijeme_min // 60:02d}:{vrijeme_min % 60:02d}"
        kursor.execute(
            "INSERT INTO raspored (mec_id, teren, vrijeme_pocetka) VALUES (?, ?, ?)",
            (mec_id, teren, vrijeme)
        )
    konekcija.commit()
    return {"poruka": "Raspored generisan"}

@router.get("/prikazi_raspored_grupa")
def prikazi_raspored_grupa():
    kursor.execute("""
    SELECT 
        m.id AS mec_id,
        e1.naziv AS ekipa1_naziv,
        e2.naziv AS ekipa2_naziv,
        r.teren,
        r.vrijeme_pocetka AS vrijeme
    FROM mecevi m
    JOIN raspored r ON m.id = r.mec_id
    JOIN ekipa e1 ON m.ekipa1_id = e1.id
    JOIN ekipa e2 ON m.ekipa2_id = e2.id;
    """)
    raspored = kursor.fetchall()
    return {"raspored": raspored}