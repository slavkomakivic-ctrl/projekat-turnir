from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hesuj_lozinku(lozinka):
    return pwd_context.hash(lozinka)

def provjeri_lozinku(lozinka, hash_iz_baze):
    return pwd_context.verify(lozinka, hash_iz_baze)

TAJNI_KLJUC = os.getenv("TAJNI_KLJUC")
ALGORITAM = "HS256"

def napravi_token(korisnicko_ime):
    podaci = {
        "sub": korisnicko_ime,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(podaci, TAJNI_KLJUC, algorithm=ALGORITAM)
    return token