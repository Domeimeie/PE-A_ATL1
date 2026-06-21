# PE-A_ATL1 – „DODOload" 📦

Eine einfache **File-Management-API**, gebaut mit [FastAPI](https://fastapi.tiangolo.com/).
Benutzer können sich registrieren und anmelden, Dateien hoch- und herunterladen,
diese mit eigenen **Tags** organisieren und ihren Account inklusive aller Daten
wieder löschen. Jeder Benutzer sieht und verwaltet ausschliesslich seine **eigenen**
Dateien und Tags.

Das Projekt wurde im Rahmen des Modules PE-A in der HF-ICT als Anwendungs- und Transferleistung erarbeitet.

---

## ✨ Funktionsumfang

- **Authentifizierung** über JWT (Bearer-Token).
- **Datei-Upload / -Download** mit Speicherung der Bytes auf der Festplatte und
  der Metadaten in der Datenbank.
- **Tags** auf Benutzerbasis – Dateien können beim Upload mit 0 oder mehr Tags
  versehen werden; Dateien lassen sich nach Tag abfragen.
- **Strikte Eigentümer-Prüfung** – fremde Dateien/Tags liefern `404`.
- **Account-Löschung**, die alle Dateien (Festplatte + Datenbank) und Tags des
  Benutzers mitentfernt.

---

## 🧱 Technologie-Überblick

| Bereich        | Verwendet                                  |
| -------------- | ------------------------------------------ |
| Sprache        | Python 3.14                                |
| Framework      | FastAPI                                    |
| Datenbank      | SQLite über SQLModel                       |
| Auth           | JWT (PyJWT)                                 |
| Paketmanager   | [uv](https://github.com/astral-sh/uv)      |
| Tests          | pytest / pytest-cov                        |
| Deployment     | Docker → Google Cloud Build → Cloud Run    |

---

## 🚀 Installation & Start

Das Projekt lässt sich auf drei Arten betreiben: lokal mit **uv**, als **Docker**-Container
oder vollautomatisch über die **Google-Cloud-Pipeline**. Nach einem lokalen Start
(uv oder Docker) ist die API erreichbar unter:

```text
http://127.0.0.1:8000
```

> 💡 **Interaktive Dokumentation:** FastAPI stellt automatisch eine Swagger-UI
> unter `http://127.0.0.1:8000/docs` bereit. Dort lassen sich alle Endpunkte
> direkt ausprobieren.

### 🧰 Lokal mit uv

Voraussetzung: [uv](https://github.com/astral-sh/uv) ist installiert.

```bash
# 1. Abhängigkeiten installieren (aus uv.lock, reproduzierbar)
uv sync

# 2. Entwicklungsserver starten (mit Auto-Reload)
uv run fastapi dev app/main.py
```

### 🐳 Build & Start mit Docker

Das mitgelieferte [Dockerfile](Dockerfile) erstellt ein schlankes Image in zwei
Stufen (Build der Abhängigkeiten → schlankes Laufzeit-Image).

```bash
# Image bauen
docker build -t pe-a-atl1 .

# Container starten (Port 8000 nach aussen mappen)
docker run -p 8000:8000 pe-a-atl1
```

Im Container wird die App mit `fastapi run main.py --host=0.0.0.0` auf Port `8000`
gestartet.

### ☁️ Automatisches Deployment (Google Cloud)

Die Datei [cloudbuild.yaml](cloudbuild.yaml) beschreibt eine **Cloud-Build-Pipeline**,
die bei jedem Push folgende Schritte durchläuft und die Anwendung anschliessend
auf **Google Cloud Run** (Region `europe-west6`) deployt:

| Schritt    | Beschreibung                                              |
| ---------- | -------------------------------------------------------- |
| `Install`  | `uv sync --frozen` – Abhängigkeiten reproduzierbar laden |
| `Test`     | `uv run pytest` – Build bricht ab, wenn Tests scheitern  |
| `Build`    | Docker-Image mit Commit-SHA als Tag bauen                |
| `Push`     | Image in die Artifact Registry pushen                    |
| `Deploy`   | Neue Cloud-Run-Revision ausrollen                        |

#### Persistente Speicherung

Cloud Run hat ein **flüchtiges Dateisystem**. Damit Uploads und die SQLite-Datenbank
einen Neustart überleben, wird ein **Google-Cloud-Storage-Bucket** als Volume
unter `/app/data` eingebunden. Die Pfade werden über Umgebungsvariablen gesteuert:

| Variable        | Zweck                              | Lokaler Standard |
| --------------- | ---------------------------------- | ---------------- |
| `UPLOAD_DIR`    | Ablageort der hochgeladenen Dateien | `uploads`        |
| `DATABASE_FILE` | Pfad der SQLite-Datenbankdatei      | `database.db`    |

---

## 🧪 Tests ausführen

```bash
# Alle Tests
uv run pytest

# Mit Code-Coverage-Bericht
uv run pytest --cov=app --cov-report=term-missing
```

---

## 🗂️ Projektstruktur / Komponenten

```text
app/
├── main.py          # FastAPI-App, bindet alle Router ein
├── database.py      # Datenbank-Engine & Session-Dependency
├── security.py      # JWT-Prüfung (token_auth)
├── models/          # SQLModel-Tabellen (User, File, Tag, FileTagLink)
├── schemas/         # Pydantic-Schemas für Requests/Responses
├── routers/         # HTTP-Endpunkte (users, files, tags, auth)
└── services/        # Geschäftslogik (von den Routern aufgerufen)
test/                # pytest-Tests + gemeinsame Fixtures (conftest.py)
```

**Schichten-Prinzip:** Die **Router** lesen das Token und reichen die `user_id`
an die **Services** weiter. Die Services enthalten die eigentliche Logik und die
Eigentümer-Prüfung und bleiben dadurch frei von HTTP-/JWT-Details.

---

## 📖 API-Dokumentation

Basis-URL lokal: `http://127.0.0.1:8000`

### Authentifizierung

Geschützte Endpunkte erwarten einen Bearer-Token im Header:

```text
Authorization: Bearer <access_token>
```

Das Token erhält man über `POST /auth/login`.

#### Typischer Ablauf

```bash
# 1. Benutzer anlegen
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "homer@ithaca.gr", "password": "odyssey"}'

# 2. Anmelden und Token erhalten
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "homer@ithaca.gr", "password": "odyssey"}'
# -> { "access_token": "eyJhbGciOi..." }

# 3. Datei mit Token hochladen (optional mit Tags)
curl -X POST http://127.0.0.1:8000/files/ \
  -H "Authorization: Bearer <access_token>" \
  -F "upload=@./bild.png" \
  -F "tag_ids=1"
```

### Auth

| Methode | Pfad          | Auth | Beschreibung                                  |
| ------- | ------------- | ---- | --------------------------------------------- |
| `POST`  | `/auth/login` | –    | Anmelden, liefert `{ "access_token": "..." }` |

### Users

| Methode  | Pfad           | Auth | Beschreibung                                            |
| -------- | -------------- | ---- | ------------------------------------------------------- |
| `POST`   | `/users`       | –    | Benutzer registrieren (`{ email, password }`)           |
| `GET`    | `/users`       | ✅   | Liste der Benutzer                                       |
| `GET`    | `/users/{id}`  | –    | Einzelnen Benutzer abrufen                              |
| `DELETE` | `/users/me`    | ✅   | **Eigenen** Account inkl. aller Dateien & Tags löschen   |

### Files

| Methode  | Pfad               | Auth | Beschreibung                                                       |
| -------- | ------------------ | ---- | ----------------------------------------------------------------- |
| `POST`   | `/files/`          | ✅   | Datei hochladen (`multipart/form-data`: `upload`, optional `tag_ids`) |
| `GET`    | `/files/`          | ✅   | Eigene Dateien auflisten (Metadaten als JSON)                     |
| `GET`    | `/files/{id}`      | ✅   | Datei-Bytes herunterladen                                         |
| `DELETE` | `/files/{id}`      | ✅   | Eigene Datei löschen (Festplatte + Datenbank)                    |

> `tag_ids` akzeptiert sowohl wiederholte Felder (`tag_ids=1&tag_ids=2`) als auch
> eine kommagetrennte Liste (`tag_ids=1,2`) – Letzteres insbesondere für die Swagger-UI.

### Tags

| Methode  | Pfad                  | Auth | Beschreibung                               |
| -------- | --------------------- | ---- | ------------------------------------------ |
| `POST`   | `/tags/`              | ✅   | Tag anlegen (`{ "name": "..." }`)          |
| `GET`    | `/tags/`              | ✅   | Eigene Tags auflisten                      |
| `GET`    | `/tags/{id}`          | ✅   | Einzelnen Tag abrufen                      |
| `GET`    | `/tags/{id}/files`    | ✅   | Alle Dateien mit diesem Tag abrufen        |
| `DELETE` | `/tags/{id}`          | ✅   | Tag löschen (wird von allen Dateien entfernt) |

---

## 📦 Abhängigkeiten (Auszug)

- `fastapi[standard]` – Web-Framework inkl. Server (uvicorn) und CLI
- `sqlmodel` – ORM + Pydantic-Modelle für die Datenbank
- `pyjwt` – Erstellen/Prüfen der JWT-Token
- `python-multipart` – nötig, damit FastAPI `multipart/form-data`-Uploads verarbeiten kann
- `pytest` / `pytest-cov` *(dev)* – Tests und Coverage

---

## 💭 Überlegungen

### Identität aus dem Token statt vom Client

Beim Hochladen oder Löschen wird die `user_id` aus dem authentifizierten JWT
gelesen und nicht als Parameter akzeptiert. So kann niemand im Namen anderer
handeln, indem er einfach eine fremde ID mitschickt.

### 404 statt 403 bei fremden Ressourcen

Greift jemand auf eine fremde Datei oder einen fremden Tag zu, wird `404 Not Found`
(statt `403 Forbidden`) zurückgegeben. So wird nicht verraten, dass die Ressource
überhaupt existiert. -> Yay für Security!

### Dateien: Bytes auf Disk, Metadaten in der Datenbank

Die eigentlichen Datei-Bytes liegen im Dateisystem, während Name, Typ, Grösse und
Besitzer in der Datenbank gespeichert werden. Der Dateiname auf der Festplatte wird
mit einer UUID versehen. Das verhindert Namenskollisionen und Path-Traversal.

### Tags als Many-to-many-Verknüpfung

Tags werden über eine eigene Verknüpfungstabelle mit Dateien verbunden, statt sie
z. B. als kommaseparierten String an der Datei zu speichern. Nur so lassen sich
Dateien sauber nach Tag abfragen und ein gelöschter Tag von allen Dateien entfernen.

---

## ⚙️ Potentielle Änderungen/Verbesserungen

### Wechsel auf Cloud SQL

SQLite auf einem GCS-Volume ist nur bedingt für Cloud Run geeignet: Das Locking
funktioniert nicht zuverlässig (Korruptionsrisiko) und die App muss bei
`max-instances=1` bleiben. Ein Wechsel auf **Cloud SQL** (verwaltetes PostgreSQL)
würde dieses Problem lösen und horizontale Skalierung ermöglichen.

### Passwort-Hashing

Passwörter werden aktuell im **Klartext** in der Datenbank gespeichert und
verglichen. Sie sollten stattdessen mit einem etablierten Verfahren (z. B. bcrypt)
**gehasht** werden, damit sie bei einem Datenbank-Leak nicht offen einsehbar sind.