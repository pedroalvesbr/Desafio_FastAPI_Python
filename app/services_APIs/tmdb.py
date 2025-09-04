from fastapi import APIRouter, Depends
import re
import requests
from typing import List, Dict, Optional, Tuple


router = APIRouter()

# Regex para remover qualquer sufixo entre parênteses: (voice), (uncredited), etc.
PAREN_CONTENT = re.compile(r"\s*\([^)]*\)")

GENERIC_NAMES = {
    "additional voices",
    "various",
    "background voices",
    "voices",
}

def split_and_clean(char_str: str):
    """
    Divide por '/', remove sufixos entre parênteses, normaliza espaços.
    Retorna lista de nomes de personagens limpos (sem vazios).
    """
    if not char_str:
        return []

    parts = [p.strip() for p in char_str.split("/")]
    cleaned = []
    for p in parts:
        p = PAREN_CONTENT.sub("", p)              # remove (...) como (voice)
        p = re.sub(r"\s+", " ", p).strip()        # normaliza espaços
        if p:
            cleaned.append(p)
    return cleaned

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "775c2b1c04714f0b8fcfd1beabc89a40"


#id 60625 devido a existir mais de um resultado para rick and morty no tmdb
def get_show_cast(tv_id: int = 60625):
    """Retorna o elenco (cast) de uma série pelo tv_id"""
    url = f"{BASE_URL}/tv/{tv_id}/aggregate_credits?api_key={API_KEY}"
    resp = requests.get(url)
    return resp.json().get("cast", [])

@router.get("/tmdb_distinct_voice")
def get_distinct_voice_actors():
    array_dubladores = get_all_voice_actors()
    distinct_dublador = {}
    for actor in array_dubladores:
        tmdb_id = actor["tmdb_id"]
        if tmdb_id not in distinct_dublador:
            distinct_dublador[tmdb_id]  = {
            "tmdb_id": tmdb_id,
            "name": actor["name"]
            }
    return list(distinct_dublador.values())


@router.get("/tmdb_teste")
def get_all_voice_actors(
    tv_id: int = 60625,
    dedupe: bool = True,
    drop_generic: bool = True,
):
    """
    Retorna uma lista de {name, character, tmdb_id} já:
      - separada por '/', 
      - sem '(voice)' e similares,
      - deduplicada por ator+personagem,
      - (opcional) sem genéricos como 'Additional Voices'.
    """
    cast = get_show_cast(tv_id)

    results = []
    seen_global = set()  # (tmdb_id, character_lower) p/ dedupe global

    for actor in cast:
        name = actor.get("name")
        tmdb_id = actor.get("id")
        roles = actor.get("roles", [])

        # Deduplicação no escopo do ator (mesmo personagem em vários roles)
        seen_actor_chars = set()  # character_lower

        for role in roles:
            raw = role.get("character", "") or ""
            for ch in split_and_clean(raw):
                ch_low = ch.lower()

                if drop_generic and ch_low in GENERIC_NAMES:
                    continue
                if ch_low in seen_actor_chars:
                    continue  # já pegamos esse personagem para este ator

                seen_actor_chars.add(ch_low)

        # Agora grava 1 linha por personagem limpo desse ator
        for ch_low in seen_actor_chars:
            key = (tmdb_id, ch_low)
            if dedupe and key in seen_global:
                continue
            seen_global.add(key)
            results.append({
                "name": name,
                "character": ch_low.title(),  # opcional: capitaliza
                "tmdb_id": tmdb_id
            })

    return results
