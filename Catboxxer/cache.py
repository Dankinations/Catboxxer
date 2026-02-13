from utils import resource_path
from pathlib import Path
import json
import ui as UIMODULE
import requests
from io import BytesIO
from PIL import Image
import tempfile 
import utils

cache = None
UI:UIMODULE.UI = None
TEMPCACHE:dict = {}

def is_allowed(x:str):
    allowed = ["png","jpg","jpeg","webp"]
    for s in allowed:
        if x.endswith(".%s"%s):
            return True
    return False

def get_file_thumbnail(link:str) -> str:
    global TEMPCACHE
    if link in list(TEMPCACHE.keys()): return TEMPCACHE[link]
    if is_allowed(link):
        try:
            r = requests.get(link,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            content = BytesIO(r.content)
            img = Image.open(content)
            img.verify()
            img = Image.open(content)
            img.thumbnail((128,128))
        except Exception as e:
            TEMPCACHE[link] = None
            return
        
        temp_path:str

        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
            img.save(tmp.name)
            temp_path = tmp.name
            TEMPCACHE[link] = temp_path
        
        return temp_path
    else:
        TEMPCACHE[link] = None
    return False

def remove_file(link:str|tuple):
    if isinstance(link,tuple):
        for l in link:
            l = l.split("/")[-1]
            UI.remove_uploaded_file(l)
            cache["Files"].remove(l)
    else:
        UI.remove_uploaded_file(link)
        l = link.split("/")[-1]
        if l in cache["Files"]:
            cache["Files"].remove(link)
    update_cache("w")

def remove_file_from_album(short: str, files: str | tuple | list):
    if short not in cache["Albums"]:
        return
    
    files_to_remove = [files] if isinstance(files, str) else list(files)
    album_files = cache["Albums"][short]["files"]
    
    for f in files_to_remove:
        filename = f.split("/")[-1]
        
        if filename in album_files:
            album_files.remove(filename)
            
    update_cache("w")

def remove_album(link:str):
    UI.remove_album(link)

    if link in list(cache["Albums"].keys()):
        del cache["Albums"][link]
    update_cache("w",True)

def add_album(name:str,desc:str,short:str,files:list[str]):
    if short in list(cache["Albums"].keys()): return
    cache["Albums"][short] = {
        "name":name,
        "files":files,
        "desc":desc
    }
    update_cache("w",True)

def add_file(link: str):
    links = [link] if isinstance(link, str) else link
    
    for l in links:
        filename = l.split("/")[-1]
        
        if filename not in cache["Files"]:
            cache["Files"].append(filename)
            if UI:
                UI.add_uploaded_file(filename)

    update_cache("w")

def add_file_to_album(short: str, files: str | list | tuple):
    if short not in cache["Albums"]: 
        return
    
    files_to_add = [files] if isinstance(files, str) else list(files)
    album_files = cache["Albums"][short]["files"]
    
    for f in files_to_add:
        filename = f.split("/")[-1]

        if filename not in cache["Files"]:
            cache["Files"].append(filename)
            if UI: UI.add_uploaded_file(filename)

        if filename not in album_files:
            album_files.append(filename)
            
    update_cache("w")

def get_albums() -> dict:
    return cache["Albums"]

def update_cache(mode="r",refresh=False,override=None):
    global cache
    cachelocation = Path(resource_path(f"catbox_{override or open(resource_path("catboxhash.txt")).read() }.json"))

    if cachelocation.exists():
        with open(cachelocation, mode) as f:
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
    if UI and (mode == "r" or refresh):
        for x in cache["Files"]:
            found = False
            for v in UI.uploaded_list:
                if v.link.split("/")[-1] == x:
                    found = True
                    break
            if found: continue
            UI.add_uploaded_file(link=x)

        for short in cache["Albums"]:
            found = False
            for v in UI.albums_list:
                if v.short == short:
                    found = True
                    break
            if found: continue
            UI.add_album(short=short,info=cache["Albums"][short])

    for album_id in cache["Albums"]:
        album = cache["Albums"][album_id]
        files_list = album["files"]

        for file_url in files_list[:]: 
            if file_url not in cache["Files"]:
                files_list.remove(file_url)