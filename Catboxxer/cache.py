from utils import resource_path
from pathlib import Path
import json
import ui as UIMODULE

cache = None
UI:UIMODULE.UI = None

def add_file(link:str):
    UI.add_uploaded_file(link)
    cache["Files"].append(link)
    update_cache("w")

def add_album(name:str,desc:str,short:str,files):
    if not cache["Albums"][short]: return
    cache["Albums"][short] = {
        "name":name,
        "files":files,
        "desc":desc
    }
    update_cache("w")

def add_files_to_album(short:str,files=(str)):
    if not cache["Albums"][short]: return
    cache["Albums"][short]["files"] += list(files)

def get_albums() -> dict:
    return cache["Albums"]

def update_cache(mode="r",refresh=False,override=None):
    global cache
    cachelocation = Path(resource_path(f"catbox_{override or open(resource_path("catboxhash.txt")).read() }.json"))

    if cachelocation.exists():
        with open(cachelocation, "r+") as f:
            if mode == "w":
                json.dump(cache,f)
            else:
                cache = json.load(f)
    else:
        with open(cachelocation, "w") as f:
            template_content = {
                "Albums" : {},
                "Settings" : {},
                "Files" : []
            }
            toWrite = json.dumps(template_content)
            f.write(toWrite)
            cache = template_content
    
    if UI:
        if refresh:
            UI.clear_uploaded_files()
        
        for x in cache["Files"]:
            found = False
            for v in UI.uploaded_list:
                if v.link == x:
                    found = True
                    break
            if found: continue
            UI.add_uploaded_file(link=x)