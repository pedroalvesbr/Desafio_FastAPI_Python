from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.services_APIs import rick_and_morty, tmdb
import re

# dependência para abrir e fechar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

def normalize_name(name: str) -> str:
    """Normaliza nomes para comparação (remove acentos, espaços extras, etc.)"""
    if not name:
        return ""
    # Remove texto entre parênteses como "(voice)"
    name = re.sub(r'\s*\([^)]*\)', '', name)
    # Remove espaços extras e converte para minúsculo
    return name.strip().lower()

def find_character_by_voice_actor(db: Session, character_name: str):
    """Encontra um personagem no banco pelo nome do personagem que o dublador faz"""
    normalized_search = normalize_name(character_name)
    
    # Buscar todos os personagens
    characters = db.query(models.Character).all()
    
    for char in characters:
        normalized_char = normalize_name(char.name)
        
        # Verifica se há correspondência exata ou parcial
        if (normalized_search == normalized_char or 
            normalized_search in normalized_char or 
            normalized_char in normalized_search):
            return char
    
    return None

@router.post("/collect")
def collect_data(db: Session = Depends(get_db)):
    saved = {"characters": 0, "episodes": 0, "voice_actors": 0, "associations": 0, "voice_characters": 0}
    
    # --- 1. RICK AND MORTY API: Characters ---
    print("Coletando personagens da Rick and Morty API...")
    characters = rick_and_morty.get_characters()
    
    for char in characters:
        exists = db.query(models.Character).filter_by(api_id=char["id"]).first()
        if not exists:
            new_char = models.Character(
                api_id=char["id"],
                name=char["name"],
            )
            db.add(new_char)
            saved["characters"] += 1
    
    db.commit()  # Commit characters primeiro
    
    
    # --- 2. RICK AND MORTY API: Episodes ---
    print("Coletando episódios da Rick and Morty API...")
    episodes = rick_and_morty.get_episodes()
    
    episode_char_map = {}  # Para mapear episódios e personagens
    
    for ep in episodes:
        exists = db.query(models.Episode).filter_by(api_id=ep["id"]).first()
        if not exists:
            new_ep = models.Episode(
                api_id=ep["id"],
                ep_name=ep["name"],
                episode_code=ep["episode"],

            )
            db.add(new_ep)
            saved["episodes"] += 1
            
            # Guardar relação episódio-personagens para depois
            episode_char_map[ep["id"]] = ep.get("characters", [])
    
    db.commit()  # Commit episodes
    

    # --- 3. Associar Episódios com Personagens ---
    print("Criando associações episódio-personagem...")
    for episode_api_id, character_urls in episode_char_map.items():
        episode = db.query(models.Episode).filter_by(api_id=episode_api_id).first()
        
        if episode:
            for char_url in character_urls:
                # Extrair ID do personagem da URL
                try:
                    char_api_id = int(char_url.split('/')[-1])
                    character = db.query(models.Character).filter_by(api_id=char_api_id).first()
                    
                    if character and character not in episode.characters:
                        episode.characters.append(character)
                except (ValueError, IndexError):
                    continue
    
    db.commit()  # Commit final

    print("Coletando os dubladores da API do TMDB...")
    voice_actors = tmdb.get_distinct_voice_actors()
    
    for va in voice_actors:
        exists = db.query(models.VoiceActor).filter_by(tmdb_id=va["tmdb_id"]).first()
        if not exists:
            new_VoiceActor = models.VoiceActor(
                tmdb_id=va["tmdb_id"],
                name=va["name"],
            )
            db.add(new_VoiceActor)
            saved["voice_actors"] += 1
    
    db.commit()  # Commit Voice Actors


    print("Correlacionando os dubladores com os personagens..")
    voice_actor_data = tmdb.get_all_voice_actors()

    for entry in voice_actor_data:
        actor_tmdb_id = entry["tmdb_id"]
        actor_name = entry["name"]
        character_name = entry["character"]

        # 1. Buscar ou criar o VoiceActor
        voice_actor = db.query(models.VoiceActor).filter_by(tmdb_id=actor_tmdb_id).first()
        if not voice_actor:
            voice_actor = models.VoiceActor(
                name=actor_name,
                tmdb_id=actor_tmdb_id
            )
            db.add(voice_actor)
            db.flush()  # Garante que o ID será gerado antes de usar

        # 2. Buscar o Character correspondente (pelo nome)
        character = db.query(models.Character).filter(
            models.Character.name.ilike(character_name)
        ).first()

        if not character:
            continue

        # 3. Verificar se a associação já existe
        exists = db.query(models.VoiceCharacter).filter_by(
            character_id=character.id,
            voice_actor_id=voice_actor.id
        ).first()

        if exists:
            continue  # Já existe, não duplica

        # 4. Criar a associação VoiceCharacter
        voice_char = models.VoiceCharacter(
            character_id=character.id,
            voice_actor_id=voice_actor.id
        )
        db.add(voice_char)
        saved["voice_characters"] += 1  # contabiliza

    db.commit()
    print(f"✓ {saved['voice_characters']} dublagens correlacionadas com sucesso.")

    
    






   