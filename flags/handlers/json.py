import os
import json
import asyncio
from flags.scrapper import Scrapper
from flags.req_conf import (WIKIURL, HEADERS, POPULATION_URL)

scrapper = Scrapper(WIKIURL,POPULATION_URL,HEADERS)

#Change to sqlite ------

def init_json_flags(filename):
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            return json.load(f)
    else:
        data = asyncio.run(scrapper.get_flags())
        save_json(filename,data)
        return data

    
def load_json(path):
    if os.path.exists(path):
        with open(path,'r') as f:
            return json.load(f)
    else:
        return asyncio.run(scrapper.get_flags())
        
def save_json(path:str,data):
    with open(path,'w') as f:
        json.dump(data,f,indent=1)

#Change to sqlite ------