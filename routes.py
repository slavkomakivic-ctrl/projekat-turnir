from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database import kursor, konekcija
from models import Korisnik
from auth import hesuj_lozinku, provjeri_lozinku, napravi_token
from auth_dependency import trenutni_korisnik

router = APIRouter()

@router.post("/registracija")
def registruj_korisnika(korisnik: Korisnik):
    hash_lozinke = hesuj_lozinku(korisnik.lozinka)
    kursor.execute(
        "INSERT INTO korisnici (korisnicko_ime, lozinka_hash) VALUES (?, ?)",
        (korisnik.korisnicko_ime, hash_lozinke)
    )
    konekcija.commit()
    return {"poruka": f"Registrovan korisnik: {korisnik.korisnicko_ime}"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    kursor.execute(
        "SELECT lozinka_hash FROM korisnici WHERE korisnicko_ime = ?",
        (form_data.username,)
    )
    red = kursor.fetchone()

    if red is None:
        raise HTTPException(status_code=401, detail="Pogresno korisnicko ime ili lozinka")

    hash_iz_baze = red[0]

    if not provjeri_lozinku(form_data.password, hash_iz_baze):
        raise HTTPException(status_code=401, detail="Pogresno korisnicko ime ili lozinka")

    token = napravi_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}