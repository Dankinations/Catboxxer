from pathlib import Path
from ui import UI
import os
from service_manager import Service,KeyListener
from pynput.keyboard import Key
import utils
listener = KeyListener(Key.shift_l)

# API STUFF
apikeylocation = Path(utils.resource_path("catboxhash.txt"))

if apikeylocation.exists():
    with open(apikeylocation, "r") as f:
        API_KEY = f.read().strip()
else:
    with open(apikeylocation, "w") as f:
        f.write("TEMPLATE")

# Logic

def exit():
    ui.window.quit()
    service.icon.stop()

def open_window(_):
    service.set_ui_toggle(True)
    ui.set_enabled(True)

def on_quit():
    if listener.down:
        exit()
    else:
        utils.displayNotification("Catboxxer","Catbox has been closed to tray.\nTo fully exit, Shift+Click when closing the window, or quit from tray.", 
                                  icon=utils.toastIcon, on_click=open_window)
        ui.set_enabled(False)
        service.set_ui_toggle(False)

ui = UI()
service = Service(ui,exit)
ui.window.protocol("WM_DELETE_WINDOW",on_quit)

ui.mainloop()