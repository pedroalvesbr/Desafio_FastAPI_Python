from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class VoiceActor(Base):
    __tablename__ = "voice_actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String, nullable=True)
    character = Column(String, nullable=True)


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    status = Column(String, nullable=True)
    species = Column(String, nullable=True)
    gender = Column(String, nullable=True)

    appearances = relationship("Appearance", back_populates="character")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    dimension = Column(String, nullable=True)


class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    first_air_date = Column(String, nullable=True)

    episodes = relationship("Episode", back_populates="show")



class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    season = Column(Integer, nullable=True)
    number = Column(Integer, nullable=True)
    show_id = Column(Integer, ForeignKey("shows.id"))

    show = relationship("Show", back_populates="episodes")
    appearances = relationship("Appearance", back_populates="episode")

class Appearance(Base):
    __tablename__ = "appearances"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))

    character = relationship("Character", back_populates="appearances")
    episode = relationship("Episode", back_populates="appearances")
