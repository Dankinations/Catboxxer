from customtkinter import CTk, CTkTabview, CTkFrame, CTkLabel, CTkFont, CTkImage, CTkScrollableFrame, set_appearance_mode, ThemeManager
from tkinterdnd2 import DND_FILES, TkinterDnD; from tkinterdnd2.TkinterDnD import DnDWrapper
from PIL import Image
import utils

class Tk(CTk, DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class TabView(CTkTabview):
    def __init__(self,parent,**kwargs):
        super().__init__(parent, **kwargs)
        
        self.add("Upload")
        self.add("Files")
        self.add("Albums")
        self.add("Settings")

class UI:
    def __init__(self):
        print("Initialized UI")
        set_appearance_mode("Dark")

        self.window = Tk()
        self.window.geometry("800x600")
        self.window.minsize(400,400)
        self.mainloop = self.window.mainloop

        self.tab_view = TabView(parent=self.window)
        self.tab_view.pack(fill="both", padx=20,pady=20,expand=True)
        
        ## UPLOAD TAB ##
        upload = self.tab_view.tab("Upload")

        dropThingie = CTkFrame(upload,corner_radius=30,border_color="white",border_width=1.5,fg_color="gray24")
        dropThingie.place(rely=.005,relx=0.05,relwidth=.9,relheight=.35)
        
        uploadList = CTkScrollableFrame(upload,corner_radius=30,border_color="white",border_width=1.5,fg_color="gray24")
        uploadList.place(rely=.505,relx=0.05,relwidth=.9,relheight=.475)

        ctkuploadimg = CTkImage(dark_image=Image.open(utils.resource_path("images/upload.ico")))

        uploadlbl = CTkLabel(dropThingie,text="",corner_radius=100,font=CTkFont("Arial",48,"bold"),image=ctkuploadimg)
        uploadlbl.place(rely=.05,relx=.05,relwidth=.9,relheight=.9)

        #Function that uhausdfhaushuashuifhau yep
        def on_drop(e):
            paths = self.window.tk.splitlist(e.data)
    
            for path in paths:
                pass
                #uploadlbl.place(rely=.05,relx=.05,relwidth=.9,relheight=.9)
        
        # SETTING UP SIGNALS
        dropThingie.drop_target_register(DND_FILES)
        dropThingie.dnd_bind("<<Drop>>",on_drop)


    def set_enabled(self,val:bool):
        if val:
            self.window.deiconify()
            self.window.lift()
            self.window.focus()
        else:
            self.window.withdraw()