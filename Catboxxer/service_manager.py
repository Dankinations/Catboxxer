import pystray 
import PIL.Image
from threading import Thread
from ui import UI

image = PIL.Image.open("D:/Cristi/Kiprensky_Pushkin.jpg")

class Service:
    def __init__(self,ui:UI):
        self.menu = {
            "ToggleUI": True
        }
        self.icon = pystray.Icon("Catboxxer", image, "", pystray.Menu(
            pystray.MenuItem("OnClick",default=True,action=self.click_callback,visible=False),
            pystray.MenuItem("Toggle UI", self.toggle_ui_callback, checked=lambda item: self.menu["ToggleUI"]),
            pystray.MenuItem("Quit", self.exit)
        ),)
        self.ui = ui
        self.icon.run_detached()

    def toggle_ui_callback(self,icon,item):
        self.menu["ToggleUI"] = not self.menu["ToggleUI"]
        self.ui.set_enabled(self.menu["ToggleUI"])
    
    def click_callback(self):
        self.ui.set_enabled(True)
        self.menu["ToggleUI"] = False

    def exit(self):
        self.icon.stop()
        self.ui.window.quit()