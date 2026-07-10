import csv
import io
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import MuseumObject
from .schemas import (
    ExhibitRequest,
    ExhibitResponse,
    FavoriteUpdate,
    ObjectCreate,
    ObjectRead,
    ObjectUpdate,
    StatsResponse,
)
from .services import generate_exhibit, get_stats, list_objects, seed_demo


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Tiny Museum API",
    version="1.0.0",
    description="A personal museum for the stories hidden inside ordinary objects.",
    lifespan=lifespan,
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "tiny-museum"}


@app.get("/api/objects", response_model=list[ObjectRead])
def objects_index(
    q: str | None = Query(default=None, max_length=120),
    room: str | None = Query(default=None, max_length=80),
    material: str | None = Query(default=None, max_length=80),
    mood: str | None = Query(default=None, max_length=80),
    favorite: bool | None = None,
    sort: str = Query(default="newest", pattern="^(newest|oldest|name|significance|age)$"),
    db: Session = Depends(get_db),
):
    return list_objects(db, q, room, material, mood, favorite, sort)


@app.post("/api/objects", response_model=ObjectRead, status_code=status.HTTP_201_CREATED)
def objects_create(payload: ObjectCreate, db: Session = Depends(get_db)):
    item = MuseumObject(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/objects/{object_id}", response_model=ObjectRead)
def objects_show(object_id: int, db: Session = Depends(get_db)):
    item = db.get(MuseumObject, object_id)
    if not item:
        raise HTTPException(status_code=404, detail="Object not found")
    return item


@app.put("/api/objects/{object_id}", response_model=ObjectRead)
def objects_update(object_id: int, payload: ObjectUpdate, db: Session = Depends(get_db)):
    item = db.get(MuseumObject, object_id)
    if not item:
        raise HTTPException(status_code=404, detail="Object not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.patch("/api/objects/{object_id}/favorite", response_model=ObjectRead)
def objects_favorite(
    object_id: int, payload: FavoriteUpdate, db: Session = Depends(get_db)
):
    item = db.get(MuseumObject, object_id)
    if not item:
        raise HTTPException(status_code=404, detail="Object not found")
    item.favorite = payload.favorite
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/objects/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
def objects_delete(object_id: int, db: Session = Depends(get_db)):
    item = db.get(MuseumObject, object_id)
    if not item:
        raise HTTPException(status_code=404, detail="Object not found")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    return get_stats(db)


@app.post("/api/exhibitions/generate", response_model=ExhibitResponse)
def exhibitions_generate(payload: ExhibitRequest, db: Session = Depends(get_db)):
    return generate_exhibit(db, payload.theme, payload.count)


@app.post("/api/demo/seed")
def demo_seed(db: Session = Depends(get_db)):
    added = seed_demo(db)
    return {"added": added}


@app.get("/api/export.csv")
def export_csv(db: Session = Depends(get_db)):
    items = list_objects(db, None, None, None, None, None, "newest")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "name",
            "story",
            "room",
            "material",
            "mood",
            "color",
            "acquired_year",
            "estimated_age",
            "significance",
            "favorite",
            "created_at",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item.id,
                item.name,
                item.story,
                item.room,
                item.material,
                item.mood,
                item.color,
                item.acquired_year or "",
                item.estimated_age or "",
                item.significance,
                item.favorite,
                item.created_at.isoformat(),
            ]
        )
    headers = {"Content-Disposition": "attachment; filename=tiny-museum.csv"}
    return StreamingResponse(
        iter([output.getvalue()]), media_type="text/csv; charset=utf-8", headers=headers
    )


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{path:path}")
def frontend_fallback(path: str):
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Route not found")
    candidate = STATIC_DIR / path
    if candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(STATIC_DIR / "index.html")
