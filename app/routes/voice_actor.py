from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/voice_actor/list")
def list_voice_actors(db: Session = Depends(get_db)):
    # Join entre VoiceActor.character e Character.name
    actors = (
        db.query(models.VoiceActor)
        .join(models.Character, models.VoiceActor.character == models.Character.name)
        .all()
    )

    # Retorna uma lista de dicionários
    result = [
        {
            "id": actor.id,
            "name": actor.name,
            "character": actor.character,
            "country": actor.country
        }
        for actor in actors
    ]

    return result

    
@router.get("/voice_actor/{voice_actor_id}/acted_in")
def get_voice_actor_episodes(voice_actor_id: int, db: Session = Depends(get_db)):
    # Pega o ator
    actor = db.query(models.VoiceActor).filter(models.VoiceActor.id == voice_actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Voice actor not found")

    # Faz join do personagem -> aparições -> episódios
    episodes = (
        db.query(models.Episode)
        .join(models.Appearance, models.Episode.id == models.Appearance.episode_id)
        .join(models.Character, models.Appearance.character_id == models.Character.id)
        .filter(models.Character.name == actor.character)
        .all()
    )

    return {
        "voice_actor": actor.name,
        "character": actor.character,
        "episodes": [
            {
                "id": ep.id,
                "name": ep.name,
                "season": ep.season,
                "number": ep.number,
            }
            for ep in episodes
        ]
    }
