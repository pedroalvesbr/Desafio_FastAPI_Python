import requests

BASE_URL = "https://rickandmortyapi.com/api"

def get_characters():
    resp = requests.get(f"{BASE_URL}/character")
    return resp.json()["results"]

def get_locations():
    resp = requests.get(f"{BASE_URL}/location")
    return resp.json()["results"]
