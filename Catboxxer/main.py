from catbox import catboxAPI
from pathlib import Path
from ui import UI
from service_manager import Service

ui = UI()
service = Service(ui)
ui.mainloop()