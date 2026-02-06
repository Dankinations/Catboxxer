import sys,os
from win11toast import toast
from threading import Thread
from pathlib import Path
import json

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # For development, the path is relative to the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

catboxICO = resource_path("images/icon.ico")

toastIcon = {
    'src': catboxICO,
    'placement': 'appLogoOverride'
}

def displayNotification(*args, **kwargs):
    Thread(target=lambda: toast(*args, **kwargs)).start()

def is_file_allowed(file:str) -> bool:
    pat = Path(file)
    not_allowed = [".exe",".scr",".doc",".jar",".cpl"]
    if pat.suffix in not_allowed:
        return False
    return True