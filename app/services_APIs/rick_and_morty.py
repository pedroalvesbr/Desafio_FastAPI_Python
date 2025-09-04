import requests

BASE_URL = "https://rickandmortyapi.com/api"

def get_characters():
    resp = requests.get(f"{BASE_URL}/character")
    return resp.json()["results"]


def get_episodes():
    resp = requests.get(f"{BASE_URL}/episode")
    return resp.json()["results"]