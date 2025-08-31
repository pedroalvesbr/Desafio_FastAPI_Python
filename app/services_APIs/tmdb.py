import requests

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "775c2b1c04714f0b8fcfd1beabc89a40"

def get_shows(query):
    """Busca séries pelo nome (mantido para referência)"""
    url = f"{BASE_URL}/search/tv?api_key={API_KEY}&query={query}"
    resp = requests.get(url)
    return resp.json().get("results", [])

def get_show_cast(tv_id: int = 60625):
    """Retorna o elenco (cast) de uma série pelo tv_id"""
    url = f"{BASE_URL}/tv/{tv_id}/credits?api_key={API_KEY}"
    resp = requests.get(url)
    return resp.json().get("cast", [])
