import random
from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .models import MuseumObject


DEMO_OBJECTS = [
    {
        "name": "Blue Bus Ticket",
        "story": "The last paper ticket from a route I took every morning during my first month in the city.",
        "room": "Desk drawer",
        "material": "Paper",
        "mood": "Nostalgic",
        "color": "Blue",
        "acquired_year": 2019,
        "estimated_age": 7,
        "significance": 4,
        "favorite": True,
    },
    {
        "name": "Bent Teaspoon",
        "story": "It was accidentally bent while opening a stubborn jar, then became the dedicated spoon for late-night tea.",
        "room": "Kitchen",
        "material": "Steel",
        "mood": "Comforting",
        "color": "Silver",
        "acquired_year": 2014,
        "estimated_age": 12,
        "significance": 3,
        "favorite": False,
    },
    {
        "name": "Pocket-Sized Stone",
        "story": "Found beside a river after a difficult conversation. Its smooth edge became a small reminder to slow down.",
        "room": "Coat pocket",
        "material": "Stone",
        "mood": "Grounding",
        "color": "Charcoal",
        "acquired_year": 2022,
        "estimated_age": 600,
        "significance": 5,
        "favorite": True,
    },
    {
        "name": "First Apartment Key",
        "story": "The lock was replaced, but the key stayed as proof that independence once fit in the palm of a hand.",
        "room": "Memory box",
        "material": "Brass",
        "mood": "Proud",
        "color": "Gold",
        "acquired_year": 2017,
        "estimated_age": 9,
        "significance": 5,
        "favorite": True,
    },
    {
        "name": "Cracked Plant Pot",
        "story": "A repaired clay pot that survived three moves and still holds a plant grown from a cutting.",
        "room": "Window sill",
        "material": "Clay",
        "mood": "Hopeful",
        "color": "Terracotta",
        "acquired_year": 2020,
        "estimated_age": 6,
        "significance": 4,
        "favorite": False,
    },
    {
        "name": "Tiny Hotel Pencil",
        "story": "Used to sketch an impossible floor plan during a rainy evening in an unfamiliar town.",
        "room": "Sketchbook",
        "material": "Wood",
        "mood": "Curious",
        "color": "Natural",
        "acquired_year": 2018,
        "estimated_age": 8,
        "significance": 2,
        "favorite": False,
    },
]


def list_objects(
    db: Session,
    q: str | None,
    room: str | None,
    material: str | None,
    mood: str | None,
    favorite: bool | None,
    sort: str,
):
    statement = select(MuseumObject)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                MuseumObject.name.ilike(pattern),
                MuseumObject.story.ilike(pattern),
                MuseumObject.room.ilike(pattern),
                MuseumObject.material.ilike(pattern),
                MuseumObject.mood.ilike(pattern),
            )
        )
    if room:
        statement = statement.where(MuseumObject.room == room)
    if material:
        statement = statement.where(MuseumObject.material == material)
    if mood:
        statement = statement.where(MuseumObject.mood == mood)
    if favorite is not None:
        statement = statement.where(MuseumObject.favorite == favorite)
    sort_map = {
        "newest": MuseumObject.created_at.desc(),
        "oldest": MuseumObject.created_at.asc(),
        "name": MuseumObject.name.asc(),
        "significance": MuseumObject.significance.desc(),
        "age": MuseumObject.estimated_age.desc().nullslast(),
    }
    statement = statement.order_by(sort_map.get(sort, sort_map["newest"]))
    return list(db.scalars(statement).all())


def get_stats(db: Session):
    objects = list(db.scalars(select(MuseumObject)).all())
    total = len(objects)
    threshold = datetime.now(timezone.utc) - timedelta(days=30)
    created_values = []
    for item in objects:
        value = item.created_at
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        created_values.append(value)
    return {
        "total": total,
        "favorites": sum(1 for item in objects if item.favorite),
        "average_significance": round(
            sum(item.significance for item in objects) / total, 1
        )
        if total
        else 0.0,
        "oldest_acquired_year": min(
            (item.acquired_year for item in objects if item.acquired_year),
            default=None,
        ),
        "recent_count": sum(1 for value in created_values if value >= threshold),
        "by_room": dict(Counter(item.room for item in objects)),
        "by_material": dict(Counter(item.material for item in objects)),
        "by_mood": dict(Counter(item.mood for item in objects)),
    }


def generate_exhibit(db: Session, theme: str | None, count: int):
    objects = list(db.scalars(select(MuseumObject)).all())
    if not objects:
        return {
            "title": "The Empty Gallery",
            "curatorial_note": "Every collection begins with one object and one story.",
            "objects": [],
        }
    clean_theme = theme.strip() if theme else ""
    selected = objects
    if clean_theme:
        words = [word.lower() for word in clean_theme.split() if word]

        def score(item):
            searchable = " ".join(
                [item.name, item.story, item.room, item.material, item.mood, item.color]
            ).lower()
            return sum(searchable.count(word) for word in words)

        ranked = sorted(objects, key=lambda item: (score(item), random.random()), reverse=True)
        selected = [item for item in ranked if score(item) > 0]
        if len(selected) < count:
            remaining = [item for item in ranked if item not in selected]
            selected.extend(remaining)
    random.shuffle(selected)
    chosen = selected[: min(count, len(selected))]
    dominant_mood = Counter(item.mood for item in chosen).most_common(1)[0][0]
    dominant_material = Counter(item.material for item in chosen).most_common(1)[0][0]
    title = clean_theme.title() if clean_theme else f"A Cabinet of {dominant_mood} Things"
    note = (
        f"This exhibit connects {len(chosen)} everyday objects through {dominant_mood.lower()} memory, "
        f"with {dominant_material.lower()} appearing as a recurring physical thread."
    )
    return {"title": title, "curatorial_note": note, "objects": chosen}


def seed_demo(db: Session):
    existing = db.scalar(select(MuseumObject.id).limit(1))
    if existing:
        return 0
    for payload in DEMO_OBJECTS:
        db.add(MuseumObject(**payload))
    db.commit()
    return len(DEMO_OBJECTS)
