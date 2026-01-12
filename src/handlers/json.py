import json
import asyncio
from src.scrapper.get_data import Scrapper
from src.urls import (WIKIURL, HEADERS, POPULATION_URL)

def init_json_flags(filename):
    scrapper = Scrapper(WIKIURL,HEADERS,POPULATION_URL)
    try:
        with open(filename, encoding="utf-8") as f:
            return json.load(f)
    except:
        data = asyncio.run(scrapper.get_flags())
        save_json(filename,data)
        return data

    
def load_json(path):
    scrapper = Scrapper(WIKIURL,HEADERS,POPULATION_URL)
    try:
        with open(path,'r') as f:
            return json.load(f)
    except Exception:
        return asyncio.run(scrapper.get_flags())

def save_json(path:str,data):
    with open(path,'w') as f:
        json.dump(data,f,indent=1)