from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth import TAJNI_KLJUC, ALGORITAM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def trenutni_korisnik(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, TAJNI_KLJUC, algorithms=[ALGORITAM])
        korisnicko_ime = payload.get("sub")
        if korisnicko_ime is None:
            raise HTTPException(status_code=401, detail="Nevazeci token")
        return korisnicko_ime
    except JWTError:
        raise HTTPException(status_code=401, detail="Nevazeci token")