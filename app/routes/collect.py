from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.services_APIs import rick_and_morty, tmdb

# dependência para abrir e fechar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/collect")
def collect_data(db: Session = Depends(get_db)):
    # --- Rick and Morty ---
    characters = rick_and_morty.get_characters()
    locations = rick_and_morty.get_locations()

    # --- TMDB: elenco da série Rick and Morty ---
    cast = tmdb.get_show_cast(tv_id=60625)

    saved = {"characters": 0, "locations": 0, "voice_actors": 0}

    # --- Characters ---
    for char in characters:
        exists = db.query(models.Character).filter_by(api_id=char["id"]).first()
        if not exists:
            new_char = models.Character(
                api_id=char["id"],
                name=char["name"],
                status=char["status"],
                species=char["species"],
                gender=char["gender"]
            )
            db.add(new_char)
            saved["characters"] += 1

    # --- Locations ---
    for loc in locations:
        exists = db.query(models.Location).filter_by(api_id=loc["id"]).first()
        if not exists:
            new_loc = models.Location(
                api_id=loc["id"],
                name=loc["name"],
                dimension=loc["dimension"]
            )
            db.add(new_loc)
            saved["locations"] += 1

 # --- Voice Actors ---
    for actor in cast:
        exists = db.query(models.VoiceActor).filter_by(name=actor["name"]).first()
        if not exists:
            # Remove o "(voice)" do nome do personagem
            character_name = actor.get("character", "").replace(" (voice)", "").strip()
            new_actor = models.VoiceActor(
                name=actor["name"],
                character=character_name
            )
            db.add(new_actor)
            saved["voice_actors"] += 1


    db.commit()

    return {
        "message": "Dados coletados e salvos com sucesso!",
        "summary": saved
    }
