from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base  # Supondo que você já tem a instância declarativa Base

# --- Association Table simples: Character <-> Episode ---
episode_characters = Table(
    "episode_characters",
    Base.metadata,
    Column("id_episode", Integer, ForeignKey("episodes.id"), primary_key=True),
    Column("id_character", Integer, ForeignKey("characters.id"), primary_key=True)
)


# --- VoiceActor ---
class VoiceActor(Base):
    __tablename__ = "voice_actors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)

    # Relacionamento com personagens via tabela intermediária
    characters = relationship("VoiceCharacter", back_populates="voice_actor")


# --- Character ---
class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)

    # Relacionamento N:N com Episode via tabela simples
    episodes = relationship(
        "Episode",
        secondary=episode_characters,
        back_populates="characters"
    )

    # Relacionamento com dubladores via tabela intermediária
    voice_actors = relationship("VoiceCharacter", back_populates="character")


# --- VoiceCharacter: Association Table com classe ---
class VoiceCharacter(Base):
    __tablename__ = "voice_characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    voice_actor_id = Column(Integer, ForeignKey("voice_actors.id"), index=True)

    # Relacionamentos ORM
    character = relationship("Character", back_populates="voice_actors")
    voice_actor = relationship("VoiceActor", back_populates="characters")


# --- Episode ---
class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, unique=True, index=True) 
    ep_name = Column(String, nullable=False)
    episode_code = Column(String, nullable=False)  # Ex: "S01E01"

    # Relacionamento N:N com Character via tabela simples
    characters = relationship(
        "Character",
        secondary=episode_characters,
        back_populates="episodes"
    )
