# Tiny Museum

Tiny Museum is a full-stack personal archive for ordinary objects with extraordinary stories. It lets people catalog keepsakes, search and filter a collection, mark favorites, inspect collection statistics, export records, and generate themed temporary exhibits.

## Features

- Responsive single-page interface
- Create, read, update, and delete collection records
- SQLite persistence
- Search, room and mood filters, favorites, and sorting
- Collection statistics and mood pulse
- Curator-generated exhibits based on a theme
- CSV export
- Demo collection seeding
- OpenAPI documentation
- Docker health check and persistent volume
- API tests

## Stack

- FastAPI
- SQLAlchemy
- SQLite
- Vanilla HTML, CSS, and JavaScript
- Docker and Docker Compose

## Run with Docker Compose

```bash
docker compose up --build
```

Open:

- Application: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/api/health`

The SQLite database is stored in the `tiny_museum_data` Docker volume.

## Run with Docker

```bash
docker build -t tiny-museum .
docker run --rm -p 8000:8000 -v tiny-museum-data:/app/data -e DATABASE_URL=sqlite:////app/data/tiny_museum.db tiny-museum
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Tests

```bash
pytest
```

## API routes

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health |
| GET | `/api/objects` | List and filter objects |
| POST | `/api/objects` | Create an object |
| GET | `/api/objects/{id}` | Read an object |
| PUT | `/api/objects/{id}` | Update an object |
| PATCH | `/api/objects/{id}/favorite` | Change favorite status |
| DELETE | `/api/objects/{id}` | Delete an object |
| GET | `/api/stats` | Collection statistics |
| POST | `/api/exhibitions/generate` | Generate a themed exhibit |
| POST | `/api/demo/seed` | Seed demo records when empty |
| GET | `/api/export.csv` | Export the collection |

## Data model

Each object stores a name, story, room, material, mood, color, acquired year, estimated age, significance score, favorite status, and creation timestamp.

## Repository structure

```text
tiny-museum/
├── app/
│   ├── static/
│   │   ├── app.js
│   │   ├── icon.svg
│   │   ├── index.html
│   │   ├── manifest.webmanifest
│   │   └── styles.css
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
├── data/
│   └── .gitkeep
├── tests/
│   └── test_api.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements-dev.txt
├── requirements.txt
└── README.md
```
