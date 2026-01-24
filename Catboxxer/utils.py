import sys,os
from win11toast import toast
from threading import Thread

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