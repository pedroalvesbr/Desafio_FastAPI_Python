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
    # Consulta todos os dubladores
    actors = db.query(models.VoiceActor).all()

    # Retorna uma lista de dicionários
    result = [
        {
            "id": actor.id,
            "name": actor.name,
            "tmdb_id": actor.tmdb_id,
        }
        for actor in actors
    ]

    return result

    

@router.get("/voice_actor/{voice_actor_id}/acted_in")
def get_voice_actor_episodes(voice_actor_id: int, db: Session = Depends(get_db)):
    # Verifica se o dublador existe
    actor = db.query(models.VoiceActor).filter(models.VoiceActor.id == voice_actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Voice actor not found")

    # Busca os episódios em que personagens dublados por esse ator apareceram
    episodes = (
        db.query(models.Episode)
        .join(models.Episode.characters)  # via association table: episode_characters
        .join(models.VoiceCharacter, models.VoiceCharacter.character_id == models.Character.id)
        .filter(models.VoiceCharacter.voice_actor_id == voice_actor_id)
        .distinct()
        .all()
    )

    return {
        "voice_actor": actor.name,
        "episodes": [
            {
                "id": ep.id,
                "ep_name": ep.ep_name,
                "episode_code": ep.episode_code,
            }
            for ep in episodes
        ]
    }
