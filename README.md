# Projekat Turnir - API za Upravljanje Sportskim Turnirima

FastAPI aplikacija za upravljanje sportskim turnirima, timovima, mečevima i setovima. Aplikacija je kontejnerizirana sa Docker-om i koristi PostgreSQL bazu podataka.

## Karakteristike

- 🔐 **Autentifikacija**: Registracija i login sa JWT tokenom
- 🏆 **Turniri**: Kreiranje i upravljanje turnirima
- 👥 **Timovi**: Registracija timova sa članovima
- ⚽ **Mečevi**: Praćenje mečeva i njihovog statusa
- 🎯 **Setovi**: Unos rezultata po setovima
- 📊 **Grupe**: Organizacija timova u grupe
- 🔒 **Sigurnost**: Zaštita endpointa sa JWT autentifikacijom

## Tehnologije

- **Framework**: FastAPI 0.141.1
- **Baza**: PostgreSQL 16 (Alpine)
- **Autentifikacija**: Python-Jose (JWT), Passlib (bcrypt heširanje)
- **ORM**: SQLAlchemy, SQLModel
- **Testiranje**: Pytest
- **Kontejnerizacija**: Docker, Docker Compose

## Instalacija i Pokretanje

### Preduslovi

- Docker i Docker Compose
- Python 3.12+ (za lokalnu instalaciju)
- PostgreSQL 16+ (ako koristiš lokalnu bazu)

### Sa Docker-om (preporučeno)

1. **Kloniraj projekt**
   ```bash
   git clone https://github.com/slavkomakivic-ctrl/projekat-turnir
   cd projekat-turnir
   ```

2. **Postavi `.env` fajl**
   ```bash
   echo "SIFRA=bradonja" > .env
   echo "TAJNI_KLJUC=ovo-treba-da-bude-mnogo-slozenija-tajna-vrijednost-32-karaktera-ili-vise" >> .env
   ```

3. **Pokreni Docker Compose**
   ```bash
   docker compose up -d
   ```

4. **Provjeri da li je server pokrenut**
   ```bash
   docker logs projekat-turnir-app
   ```

Server će biti dostupan na `http://localhost:8000`

### Lokalno (bez Docker-a)

1. **Kreiraj virtualnu okolinu**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```

2. **Instaliraj zavisnosti**
   ```bash
   pip install -r requirements.txt
   ```

3. **Postavi bazu podataka**
   ```bash
   psql -U postgres -f init.sql
   ```

4. **Postavi `.env` fajl** (kao gore)

5. **Pokreni aplikaciju**
   ```bash
   uvicorn main:app --reload
   ```

## Struktura Projekta

```
projekat-turnir/
├── main.py                 # FastAPI aplikacija
├── auth.py                 # JWT i heširanje lozinki
├── auth_dependency.py      # Zavisnost za autentifikaciju
├── database.py             # Konekcija sa bazom
├── models.py               # Pydantic modeli
├── routes.py               # Endpointi za auth
├── ekipe_routes.py         # Endpointi za timove
├── mecevi_routes.py        # Endpointi za mečeve
├── setovi_routes.py        # Endpointi za setove
├── grupe_routes.py         # Endpointi za grupe
├── config_routes.py        # Endpointi za konfiguraciju
├── init.sql                # SQL skripte za bazu
├── conftest.py             # Pytest fiksture
├── requirements.txt        # Python zavisnosti
├── Dockerfile              # Docker konfiguracija
├── docker-compose.yml      # Docker Compose konfiguracija
├── .env                    # Okružne varijable (nije u Git-u)
└── testovi/                # Testovi
    ├── test_auth.py
    ├── test_config.py
    ├── test_ekipe.py
    ├── test_setovi.py
    └── test_token.py
```

## API Endpointi

### Autentifikacija
- `POST /registracija` - Registruj novog korisnika
- `POST /login` - Prijavi se i dobij JWT token
- `GET /provjeri_prijavu` - Provjeri da li je korisnik prijavljeni (zahtijeva token)

### Turniri
- `POST /turniri` - Kreiraj turnir
- `GET /turniri` - Lista svih turnira

### Timovi
- `POST /ekipe` - Kreiraj tim
- `GET /ekipe` - Lista svih timova
- `GET /ekipe/{ekipa_id}` - Detalji tima

### Mečevi
- `POST /mecevi` - Kreiraj meč
- `GET /mecevi` - Lista mečeva
- `PUT /mecevi/{mec_id}` - Ažuriraj status meča

### Setovi
- `POST /setovi` - Unesi set
- `GET /setovi/{mec_id}` - Lista setova za meč
- `PUT /setovi/{set_id}` - Ažuriraj set

## Okružne Varijable

Postavi u `.env` fajlu:

```env
SIFRA=<postgres_lozinka>
TAJNI_KLJUC=<tajni_kljuc_za_jwt_minimum_32_karaktera>
```

## Testiranje

### Pokreni sve testove
```bash
pytest
```

### Pokreni testove iz specifičnog fajla
```bash
pytest testovi/test_auth.py -v
```

### Pokreni testove sa pokrivanjem koda
```bash
pytest --cov
```

## Razvoj

### Struktura Testova

- `conftest.py` - Zajedničke fiksture za sve testove
  - `cista_baza` - Očisti bazu prije svakog testa
  - `client` - TestClient za API testove
  - `auth_headers` - JWT token za autentificirane testove

### Pristup Bazi u Testovima

```python
from database import kursor, konekcija

def test_nesto(cista_baza):
    kursor.execute("SELECT * FROM korisnici WHERE id = %s", (1,))
    rezultat = kursor.fetchone()
    assert rezultat is not None
    konekcija.commit()
```

## Docker Compose Servisi

### `db` - PostgreSQL
- Verzija: 16-Alpine
- Port: 5432
- Heslcheck je uključen

### `app` - FastAPI Aplikacija
- Port: 8000
- Zavisi od `db` servisa
- Učitava `.env` fajl
- Pokretač: Uvicorn

## Česta Pitanja

### JWT greška: "Expecting a string- or bytes-formatted key"
Provjeri da li je `TAJNI_KLJUC` postavljen u `.env` fajlu i da je prosljeđen u Docker kontejner.

### Greška pri konekciji sa bazom
Provjeri da li je PostgreSQL servis pokrenut i dostupan:
```bash
docker compose ps
```

### Port 8000 je već zauzet
Promijeni port u `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Lokalni port 8001 -> kontejner port 8000
```

## Doprinos

1. Kreiraj feature branch (`git checkout -b feature/nova-opcija`)
2. Commitment promjena (`git commit -m 'Dodaj novu opciju'`)
3. Push na branch (`git push origin feature/nova-opcija`)
4. Otvori Pull Request

## Licenca

MIT

## Kontakt

Za pitanja ili probleme, kontaktiraj autora ili kreiraj Issue u Git repozitoriju.
