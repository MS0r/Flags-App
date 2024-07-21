import json
from . import get_data

def init_json_flags(filename):
    try:
        with open(filename, encoding="utf-8") as f:
            return json.load(f)
    except:
        data = get_data.get_flags_url()
        save_json(filename,data)
        return data

    
def load_json(path):
    try:
        with open(path,'r') as f:
            return json.load(f)
    except Exception as e:
        return get_data.get_flags_url()

def save_json(path:str,data):
    with open(path,'w') as f:
        json.dump(data,f,indent=1)