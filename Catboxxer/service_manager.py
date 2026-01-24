import pystray 
import PIL.Image
from ui import UI
from pynput.keyboard import Listener,Key
import utils

image = PIL.Image.open(utils.resource_path("images/icon.ico"))

class Service:
    def __init__(self,ui:UI,on_quit):
        self.menu = {
            "ToggleUI": True
        }
        self.icon = pystray.Icon("Catboxxer", image, "Catboxxer", pystray.Menu(
            pystray.MenuItem("OnClick",default=True,action=self.click_callback,visible=False),
            pystray.MenuItem("Toggle UI", self.toggle_ui_callback, checked=lambda item: self.menu["ToggleUI"]),
            pystray.MenuItem("Quit",action=on_quit)
        ),)
        self.ui = ui
        self.icon.run_detached()

    def toggle_ui_callback(self,icon,item):
        self.set_ui_toggle(not self.menu["ToggleUI"])
        self.ui.set_enabled(self.menu["ToggleUI"])
        self.menu.update()
    
    def set_ui_toggle(self,val:bool):
        self.menu["ToggleUI"] = val
        self.icon.update_menu()

    def click_callback(self):
        self.set_ui_toggle(True)
        self.ui.set_enabled(True)

class KeyListener():
    def __init__(self,desired:Key):
        self.down = False
        def on_pressed(key:Key):
            if key == desired:
                self.down=True
        def on_released(key:Key):
            if key == desired:
                self.down=False
        
        self.Listener = Listener(on_press=on_pressed,on_release=on_released)
        self.Listener.start()