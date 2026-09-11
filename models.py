from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class Turnir(BaseModel):
    naziv: str = Field(min_length=1, max_length=50)
    broj_terena: int = Field(ge=1, default=1)
    dan_turnira: str
    trajanje_meca: int = Field(ge=10, default=25)

class Korisnik(BaseModel):
    korisnicko_ime: str = Field(min_length=1, max_length=30)
    lozinka: str = Field(min_length=1, max_length=50)

class Ucesnik(BaseModel):
    ime: str = Field(min_length=1, max_length=50)

class Ekipa(BaseModel):
    naziv: str = Field(min_length=1, max_length=50)
    kontakt: str = Field(min_length=9, max_length=15)
    grad: str
    clanovi: List[Ucesnik] = Field(min_length=3, max_length=5)
    
class StatusMeca(str, Enum):
    CEKA = "Ceka"
    U_TOKU = "U_toku"
    ZAVRSEN = "Zavrsen"

class Mec(BaseModel):
    status: StatusMeca = Field(default=StatusMeca.CEKA)
    ekipa1: int 
    ekipa2: int

class Broj_seta(int, Enum):
    PRVI = 1
    DRUGI = 2
    TRECI = 3

class Setovi(BaseModel):
    mec_id: int
    broj_seta: Broj_seta = Field(default=Broj_seta.PRVI)
    poeni_ekipa1: int = Field(default=0)
    poeni_ekipa2: int = Field(default=0)
    zavrsen_set: bool = Field(default=False)