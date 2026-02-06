from customtkinter import CTk, CTkTabview, CTkFrame, CTkLabel, CTkFont, CTkImage, CTkScrollableFrame, CTkComboBox, CTkProgressBar, CTkToplevel, set_appearance_mode, CTkButton, DoubleVar, CTkEntry, StringVar, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD; from tkinterdnd2.TkinterDnD import DnDWrapper
from CTkScrollableDropdownPP import CTkScrollableDropdown
from CTkMessagebox import CTkMessagebox
from PIL import Image
from catbox import catboxAPI
import utils
from pathlib import Path
from threading import Thread
from pyperclip import copy
import webbrowser
import cache

class Tk(CTk, DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class AlbumWindowView(CTkToplevel):
    def __init__(self,ui:UI,**kwargs):
        super().__init__(ui, **kwargs)


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

class AlbumDialog(CTkMessagebox):
    def __init__(self, ui:UI,files=(None),**kwargs):
        if not files: return
        if len(files) < 1: return
        super().__init__(**kwargs,icon=utils.catboxICO,option_1="Nevermind",option_3="Confirm",message="Select an album to put your file in.")
        self.title("Album Dialog")

        albumsList = cache.get_albums()
        values = []

        for x in albumsList:
            print(x)

        self.selected_album = StringVar()
        self.selected_album.set("")

        self.combobox = CTkComboBox(self,variable=self.selected_album)
        self.combobox.grid(row=3,column=0)
        self.album_selection = CTkScrollableDropdown(self.combobox,values=values,justify="left",button_color="transparent")

        def confirm():
            if self.selected_album.get().strip() != "":
                ui.api.add_files_to_album(albumsList[self.selected_album.get().strip(),files])

        self.button_3.configure(command=confirm)

class UploadedFile(CTkFrame):
     def __init__(self,parent,ui:UI,link:str,**kwargs):
        super().__init__(master=parent, corner_radius=5, 
                         border_width=2, 
                         border_color="white", 
                         fg_color="gray24",
                         height=50, **kwargs)
        short = link.split("/")[-1]
        self.title = CTkLabel(master=self,text=short or "NOT_FOUND",font=CTkFont(family="Arial",size=16))
        self.title.place(rely=0.05,relx=0.025,relwidth=.95,relheight=.45)

        def open():
            webbrowser.open(new=2,url=self.link)

        def copytoclip():
            copy(self.link)
        
        def delete():
            return ui.api.delete_files(files=(short))

        def add_to_album():
            new = AlbumDialog(ui=self,files=(self.link))
        def extra():
            msg = CTkMessagebox(title="Catboxxer",message="Select an option",option_3="Delete",option_2="Add to album",option_1="Nevermind",icon=utils.catboxICO)
            msg.button_3.configure(fg_color="brown",hover_color="brown4")
            msg.button_2.configure(fg_color="#009C4B",hover_color="#005F2E")
            response = msg.get()
            if response == "Delete":
                if delete():
                    self.destroy()
            elif response == "Add to album":
                add_to_album()


        self.openbtn = CTkButton(master=self,text="Open",image=CTkImage(dark_image=Image.open(utils.resource_path("images/upload.ico"))), command=open)
        self.openbtn.place(rely=0.5,relx=0.025,relwidth=.45,relheight=.45)

        self.copybtn = CTkButton(master=self,text="Copy",image=CTkImage(dark_image=Image.open(utils.resource_path("images/copy-link.ico"))), command=copytoclip)
        self.copybtn.place(rely=0.5,relx=0.525,relwidth=.45,relheight=.45)

        self.optionsbtn = CTkButton(master=self,text="",image=CTkImage(dark_image=Image.open(utils.resource_path("images/dots.ico"))), 
                                    command=extra,fg_color="gray24", hover_color="gray20")
        self.optionsbtn.place(rely=0.05,relx=0.89,relwidth=.1,relheight=.45)

        self.link = link

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

        self.api = catboxAPI(open(utils.resource_path("catboxhash.txt")).read())
        self.mfc = 3

        ### // UPLOAD TAB \\ ###
        upload = self.tab_view.tab("Upload")
        
        def upload_file(path):
            file_size = Path(path).stat().st_size 
            mib = file_size / (1024**2) 
            display = file_size
            suffixSeries = ["B", "KiB", "MiB", "GiB", "TiB"]
            suffix = 0

            while display >= 1024:
                display /= 1024
                suffix += 1

            if mib >= 200:
                CTkMessagebox(title="Catboxxer",message=f"File too big! Your file's size: {round(display)}{suffixSeries[suffix]}\n(Max 200MiB)",icon=utils.catboxICO, sound=True)
            else:
                new = ToUpload(parent=uploadList,UI=self,filename=str.split(path,"/")[-1])
                new.grid(row=len(uploadList.children), column=0, sticky="ew", padx=5, pady=2.5)

                def set_progress(amount:int):
                    new.progressAmount.set(amount/file_size)
                
                def start():
                    link = self.api.upload_file(path,set_progress)
                    if not link:
                        new.destroy()
                        return
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

        ### // FILES TAB \\ ###

        files = self.tab_view.tab("Files")
        filesList = CTkScrollableFrame(files,corner_radius=30,border_color="white",border_width=1.5,fg_color="gray24")
        self.filesList = filesList
        self.uploaded_list = []
        filesList.place(rely=.025,relx=0.025,relwidth=.95,relheight=.95)

        ### // SETTINGS TAB \\ ###
        settings = self.tab_view.tab("Settings")
        userhashVal = StringVar()
        userhashVal.set(self.api.hash)
        userhashEntry = CTkEntry(settings, placeholder_text="Insert user hash here...", textvariable=userhashVal, fg_color="gray24", 
                                 border_color="white", corner_radius=5, bg_color="gray16", border_width=1)
        userhashLabel = CTkLabel(settings, text="Userhash:")
        userhashLabel.place(relx=.005,rely=.05, relwidth=.2,relheight=.05)
        userhashEntry.place(relx=.3,rely=.05, relwidth=.65,relheight=.05)

        def hashChanged(_any):
            with open(utils.resource_path("catboxhash.txt"),"r+") as hash:
                if len(userhashVal.get()) != 25:
                    old = hash.read()
                    CTkMessagebox(title="Catboxxer",message=f"Invalid userhash entered, defaulting to '{old}'!", icon=utils.catboxICO, sound=True)
                    userhashVal.set(old)
                else:
                    hash.write(userhashVal.get())
                    self.api = catboxAPI(userhashVal.get())
                hash.close()
            
        userhashEntry.bind("<Return>",hashChanged)

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
    
    def reorder_uploaded_files(self):
        for idx, widget in enumerate(self.uploaded_list):
            widget.grid(row=idx // self.mfc, column=idx % self.mfc)

    def add_uploaded_file(self,link:str):
        def on_destroy(_any):
            if new in self.uploaded_list:
                if not new.manual:
                    self.uploaded_list.remove(new)
                    self.reorder_uploaded_files()

        new = UploadedFile(self.filesList,link=link,ui=self)
        new.grid(row=len(self.uploaded_list)//self.mfc, column=len(self.uploaded_list)%self.mfc, padx=2.5, pady=5)
        self.uploaded_list.append(new)
        new.bind("<Destroy>",on_destroy)

    def clear_uploaded_files(self):
        for x in self.uploaded_list:
            x.manual = True
            x.destroy()
        self.uploaded_list.clear()