from customtkinter import CTk, CTkTabview, CTkFrame, CTkLabel, CTkFont, CTkImage, CTkScrollableFrame, CTkProgressBar, set_appearance_mode, CTkButton, DoubleVar, CTkEntry, StringVar, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD; from tkinterdnd2.TkinterDnD import DnDWrapper
from PIL import Image
from catbox import catboxAPI
import utils
from pathlib import Path
from threading import Thread
from pyperclip import copy
from playsound3 import playsound

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

class ToUpload(CTkFrame):
    def __init__(self,parent,UI:UI,filename:str,**kwargs):
        super().__init__(master=parent, corner_radius=30, 
                         border_width=1.5, 
                         border_color="white", 
                         fg_color="gray24",
                         height=50, **kwargs)
        self.title = CTkLabel(master=self,text=filename or "NOT_FOUND")
        self.title.place(rely=0.05,relx=0.05,relwidth=.45,relheight=.45)
        self.progressLabel = CTkLabel(master=self)
        self.progressLabel.place(rely=0.5,relx=0.05,relwidth=.45,relheight=.45)

        self.progressAmount = DoubleVar(self)

        def progress_changed(var_name, index, mode):
            percent = min(round(self.progressAmount.get()*100), 100)
            self.progressLabel.configure(text=str(percent)  + "%")
            if percent >= 100:
                self.progressLabel.configure(text="Done!")

        self.link = ""
        def copy_link():
            copy(self.link)

        self.progressAmount.trace_add("write",progress_changed)
        self.copyLink = CTkButton(master=self,text="Copy link",image=CTkImage(dark_image=Image.open(utils.resource_path("images/copy-link.ico"))), command=copy_link, corner_radius=30)

        self.progress = CTkProgressBar(master=self,variable=self.progressAmount)
        self.progress.set(0)
        self.progress.place(rely=0.25,relx=0.5,relwidth=.45,relheight=.45)
        self.pack_propagate(False)
        
class UI:
    def __init__(self):
        print("Initialized UI")
        set_appearance_mode("Dark")

        self.window = Tk()
        self.window.geometry("800x600")
        self.window.minsize(400,400)
        self.window.iconbitmap(utils.catboxICO)
        self.window.title("Catboxxer")

        self.mainloop = self.window.mainloop

        self.tab_view = TabView(parent=self.window)
        self.tab_view.pack(fill="both", padx=20,pady=20,expand=True)

        self.api = catboxAPI(open(utils.resource_path("catboxhash.txt")))

        ### // UPLOAD TAB \\ ###
        upload = self.tab_view.tab("Upload")
        
        def upload_file(path):
            file_size = Path(path).stat().st_size 

            if file_size / (1024**2) >= 200:
                utils.displayNotification("Catboxxer",f"File too big! (Max 200MB)",icon=utils.resource_path)
            else:
                new = ToUpload(parent=uploadList,UI=self,filename=str.split(path,"/")[-1])
                new.grid(row=len(uploadList.children), column=0, sticky="ew", padx=5, pady=2.5)

                def set_progress(amount:int):
                    new.progressAmount.set(amount/file_size)
                
                def start():
                    link = self.api.upload_file(path,set_progress)
                    new.progress.destroy()
                    new.copyLink.place(rely=0.25,relx=0.5,relwidth=.45,relheight=.45)
                    new.link = link

                Thread(target=start).start()

        def select_file():
            paths = filedialog.askopenfilenames()
            for path in paths:
                upload_file(path)
        
        ctkuploadimg = CTkImage(dark_image=Image.open(utils.resource_path("images/upload.ico")))
        uploadbtn = CTkButton(upload,text="",corner_radius=30,border_color="white",border_width=1.5,
                              font=CTkFont("Arial",48,"bold"),image=ctkuploadimg,bg_color="transparent",fg_color="gray24",hover_color="gray28", command=select_file)
        uploadbtn.place(rely=.005,relx=0.05,relwidth=.9,relheight=.35)

        uploadList = CTkScrollableFrame(upload,corner_radius=30,border_color="white",border_width=1.5,fg_color="gray24")
        uploadList.place(rely=.405,relx=0.05,relwidth=.9,relheight=.575)
        uploadList.grid_rowconfigure(0,weight=1)
        uploadList.grid_columnconfigure(0,weight=1)
        
        #Function that uhausdfhaushuashuifhau yep
        def on_file_drop(e):
            paths = self.window.tk.splitlist(e.data)
            for path in paths:
                upload_file(path)

        ### // SETTINGS TAB \\ ###
        settings = self.tab_view.tab("Settings")
        userhashVal = StringVar()
        userhashVal.set(open(utils.resource_path("catboxhash.txt")).read())
        userhashEntry = CTkEntry(settings, placeholder_text="Insert user hash here...", textvariable=userhashVal, fg_color="gray24", 
                                 border_color="white", corner_radius=30, bg_color="gray16")
        userhashLabel = CTkLabel(settings, text="Userhash:")
        userhashLabel.place(relx=.005,rely=.05, relwidth=.2,relheight=.05)
        userhashEntry.place(relx=.3,rely=.05, relwidth=.65,relheight=.05)

        def hashChanged(_var_name, _index, _mode):
            with open(utils.resource_path("catboxhash.txt"),"w") as hash:
                hash.write(userhashVal.get())
                hash.close()
            self.api = catboxAPI(open(utils.resource_path("catboxhash.txt")).read())
        userhashVal.trace_add("write",hashChanged)

        # SETTING UP SIGNALS
        uploadbtn.drop_target_register(DND_FILES)
        uploadbtn.dnd_bind("<<Drop>>",on_file_drop)

    def set_enabled(self,val:bool):
        if val:
            self.window.deiconify()
            self.window.lift()
            self.window.focus()
        else:
            self.window.withdraw()