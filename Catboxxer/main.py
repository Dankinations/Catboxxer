from catbox import catboxAPI
from pathlib import Path
from ui import UI
from service_manager import Service,KeyListener
from pynput.keyboard import Key

listener = KeyListener(Key.shift_l)

# Logic

def exit():
    ui.window.quit()
    service.icon.stop()

def on_quit():
    if listener.down:
        exit()
    else:
        ui.set_enabled(False)
        service.set_ui_toggle(False)

ui = UI()
service = Service(ui,exit)
ui.window.protocol("WM_DELETE_WINDOW",on_quit)

ui.mainloop()