from customtkinter import CTk, CTkTabview, CTkFrame, CTkLabel, CTkFont, CTkImage, CTkScrollableFrame, CTkComboBox, ThemeManager, CTkProgressBar, CTkToplevel, set_appearance_mode, CTkButton, DoubleVar, CTkEntry, StringVar, filedialog
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
    def __init__(self,ui:UI,short:str,files:list,**kwargs):
        super().__init__(ui.window,**kwargs)
        self.lift(); self.focus_force()
        self.geometry(f"800x600+{self.winfo_screenwidth()//2}+{self.winfo_screenheight()//2-300}")
        self.resizable(False,False)
        self.iconbitmap(utils.catboxICO)
        self.title("Catboxxer Album Viewer")

        self.mfc = 3
        self.short = short
        self.ui = ui

        self.filesList = CTkScrollableFrame(self,corner_radius=30,border_color="white",border_width=1.5,fg_color="gray24")
        self.uploaded_list = []
        self.filesList.place(rely=.025,relx=0.025,relwidth=.95,relheight=.95)
        
        for x in files:
            self.add_uploaded_file(x)

    def add_uploaded_file(self,link:str):
        def on_destroy(_any):
            if new in self.uploaded_list:
                if not "manual" in list(new.keys()):
                    self.uploaded_list.remove(new)
                    self.reorder_uploaded_files()

        new = UploadedFile(self.filesList,link=link,ui=self.ui,album_id=self.short)
        new.grid(row=len(self.uploaded_list)//self.mfc, column=len(self.uploaded_list)%self.mfc, padx=2.5, pady=5)
        self.uploaded_list.append(new)
        new.bind("<Destroy>",on_destroy)

    def reorder_uploaded_files(self):
        for idx, widget in enumerate(self.uploaded_list):
            widget.grid(row=idx // self.mfc, column=idx % self.mfc)

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

        UI.upload_queue_list.append(self)
        self.bind("<Destroy>",lambda e,s=self: UI.upload_queue_list.remove(s))

class CTkToolTip: # Taken from online, credits to stack overflow (the site)
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        self.tooltip_window = CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) 
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = CTkLabel(self.tooltip_window, text=self.text, 
                             fg_color="#333333", corner_radius=0, padx=5)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class AlbumCreationDialog(CTkMessagebox):
    def __init__(self,ui:UI,**kwargs):
        super().__init__(**kwargs,icon=utils.catboxICO,option_1="Nevermind",option_3="Confirm",message=" ",title="Catboxxer Album Creation")
        self.info.configure(image=None)

        def confirm():
            name = nameInput.get()
            desc = descInput.get()
            result = ui.api.create_album(name,desc)
            if result:
                short = result.split("/")[-1]
                cache.add_album(name,desc,short,[])
            self.destroy()

        self.button_3.configure(fg_color="#009C4B",hover_color="#005F2E",command=confirm)
        self.button_1.configure(fg_color="brown",hover_color="brown4")

        nameInput = CTkEntry(self,placeholder_text="Album name",bg_color="gray24",justify="center")
        nameInput.place(relwidth=.65,relheight=.1,relx=.5-.325,rely=.4)

        descInput = CTkEntry(self,placeholder_text="Album description",bg_color="gray24",justify="center")
        descInput.place(relwidth=.65,relheight=.1,relx=.5-.325,rely=.505)

class AlbumDialog(CTkMessagebox):
    def __init__(self, ui:UI,files=(None),**kwargs):
        if not files: return
        if len(files) < 1: return
        super().__init__(**kwargs,icon=utils.catboxICO,option_1="Nevermind",option_3="Confirm",message="Select an album to put your file in.",title="Catboxxer Album Dialog")
        self.button_1.configure(fg_color="brown",hover_color="brown4")
        self.button_3.configure(fg_color="#009C4B",hover_color="#005F2E")

        albumsList = cache.get_albums()
        values = []
        respective = {}

        for idx in albumsList:
            x = albumsList[idx]
            s = f"{x["name"]} ({idx})"
            values.append(s)
            respective[s] = idx
        
        self.selected_album = StringVar()
        self.selected_album.set("")

        self.combobox = CTkComboBox(self,variable=self.selected_album)
        self.combobox.grid(row=2,column=0)
        self.album_selection = CTkScrollableDropdown(self.combobox,values=values,justify="left",button_color="transparent")

        if not isinstance(files,tuple):
            files = [files]

        def confirm():
            curr = self.selected_album.get()
            if curr.strip() != "" and curr.strip() in list(respective.keys()):
                short = respective[curr]
                ui.api.add_files_to_album(short,files)
                cache.add_file_to_album(short,files=files)
                self.destroy()

        self.button_3.configure(command=confirm)

class UploadedFile(CTkFrame):
     def __init__(self, parent, ui:UI, link: str, album_id=None, **kwargs):
        super().__init__(master=parent, corner_radius=5, border_width=2, border_color="white", fg_color="gray24", height=50, **kwargs)
        self.ui = ui
        self.link = "files.catbox.moe/"+link
        self.album_id = album_id

        short = link.split("/")[-1]
        self.title = CTkLabel(master=self, text=short or "NOT_FOUND", font=CTkFont(family="Arial", size=16))
        self.title.place(rely=0.05, relx=0.025, relwidth=.95, relheight=.45)

        def open_link():
            webbrowser.open(new=2, url=self.link)

        def copytoclip():
            copy(self.link)
        
        def delete_file():
            cache.remove_file(self.link.split("/")[-1])
            return self.ui.api.delete_files(files=(short))

        def add_to_album():
            AlbumDialog(ui=self.ui, files=(short))

        def remove_from_album():
            self.ui.api.remove_files_from_album(self.album_id, [short])
            cache.remove_file_from_album(self.album_id, self.link)
            self.destroy()

        def extra_options():
            opt2_text = "Remove from album" if self.album_id else "Add to album"
            
            msg = CTkMessagebox(title="Catboxxer", message="Select an option", option_3="Delete", option_2=opt2_text, option_1="Nevermind", icon=utils.catboxICO)
            msg.button_3.configure(fg_color="brown", hover_color="brown4")
            msg.button_2.configure(fg_color="#009C4B", hover_color="#005F2E")
            msg.info.configure(text="Loading thumbnail...")

            def load_img():
                img = cache.get_file_thumbnail(self.link) or utils.catboxICO
                if msg.winfo_exists():
                    newimg = msg.load_icon(img, (64, 64))
                    msg.info.configure(image=newimg, text=msg.message)

            Thread(target=load_img).start()

            def handle_response(response):
                if response == "Delete":
                    sure = CTkMessagebox(title="Catboxxer", message="Are you sure?", option_3="Yes", option_1="Nevermind", icon=utils.catboxICO)
                    sure.button_3.configure(fg_color="brown",hover_color="brown4")
                    if sure.get() == "Yes":
                        msg.destroy()
                        self.destroy()
                        delete_file()
                elif response == opt2_text:
                    if self.album_id:
                        remove_from_album()
                    else:
                        add_to_album()
            
            msg.button_3.configure(command=lambda: handle_response("Delete"))
            msg.button_2.configure(command=lambda: handle_response(opt2_text))

        self.openbtn = CTkButton(master=self, text="Open", image=CTkImage(dark_image=Image.open(utils.resource_path("images/upload.ico"))), command=open_link)
        self.openbtn.place(rely=0.5, relx=0.025, relwidth=.45, relheight=.45)

        self.copybtn = CTkButton(master=self, text="Copy", image=CTkImage(dark_image=Image.open(utils.resource_path("images/copy-link.ico"))), command=copytoclip)
        self.copybtn.place(rely=0.5, relx=0.525, relwidth=.45, relheight=.45)

        self.optionsbtn = CTkButton(master=self, text="", image=CTkImage(dark_image=Image.open(utils.resource_path("images/dots.ico"))), 
                                    command=extra_options, fg_color="gray24", hover_color="gray20")
        self.optionsbtn.place(rely=0.05, relx=0.89, relwidth=.1, relheight=.45)

class UploadedAlbum(CTkFrame):
     def __init__(self,parent,ui:UI,info:dict,short:str,**kwargs):
        super().__init__(master=parent, corner_radius=5, 
                         border_width=2, 
                         border_color="white", 
                         fg_color="gray24",
                         height=50, **kwargs)
        self.short = short

        def open():
            webbrowser.open(new=2,url="https://catbox.moe/c/" + self.short)

        def copytoclip():
            copy("https://catbox.moe/c/" + self.short)

        def delete():
            result = ui.api.delete_album(self.short)
            cache.remove_album(self.short)
            return result

        def extra():
            msg = CTkMessagebox(title=f"Catboxxer Album Dialog",message= "Select an option" ,option_3="Delete",option_2="View", option_1="Nevermind",icon=utils.catboxICO)
            msg.button_3.configure(fg_color="brown",hover_color="brown4")
            msg.button_2.configure(fg_color="#009C4B",hover_color="#005F2E")

            desc = CTkToplevel(msg,fg_color="#010101")
            desc.wm_attributes("-transparentcolor", "#010101")

            desc.attributes("-topmost",True)
            desc.attributes("-disabled",True)
            desc.overrideredirect(True)
            
            holder = CTkFrame(desc,corner_radius=30,border_width=2.5,border_color="gray24")
            desc_content = CTkLabel(holder, text=info["desc"],justify="left",anchor="nw")
            t = CTkLabel(holder, text="Description",justify="left",anchor="nw")

            holder.place(relx=0.075,rely=0.05,relwidth=.85,relheight=.95)
            desc_content.place(relwidth=.85,relheight=.85,relx=0.075,rely=.125)
            t.place(relx=.075,rely=.025,relwidth=.85,relheight=.1)

            def upd_descpos(_any):
                x = msg.winfo_rootx(); y = msg.winfo_rooty()
                desc.geometry(f"{msg.winfo_width()}x{msg.winfo_height()}+{x+msg.winfo_width()//2-desc.winfo_width()//2}+{y+msg.winfo_height()}")

            upd_descpos("a")
            desc._apply_appearance_mode("Dark")
            msg.bind("<Configure>",upd_descpos)

            def handle_response(response):
                if response == "Delete":
                    delete()
                if response == "View":
                    self.after(5,lambda: AlbumWindowView(ui,files=cache.get_albums()[short]["files"],short=short))
            response = msg.get()
            self.after(0,lambda: handle_response(response))

        self.title = CTkLabel(master=self,text=f"{len(info["name"]) > 5 and f"{info["name"][:4]}..." or info["name"]} ({short})",
                              font=CTkFont(family="Arial",size=16))
        self.title.place(rely=0.05,relx=0.025,relwidth=.95,relheight=.45)

        self.openbtn = CTkButton(master=self,text="Open",image=CTkImage(dark_image=Image.open(utils.resource_path("images/upload.ico"))), command=open)
        self.openbtn.place(rely=0.5,relx=0.025,relwidth=.45,relheight=.45)

        self.copybtn = CTkButton(master=self,text="Copy",image=CTkImage(dark_image=Image.open(utils.resource_path("images/copy-link.ico"))), command=copytoclip)
        self.copybtn.place(rely=0.5,relx=0.525,relwidth=.45,relheight=.45)

        self.optionsbtn = CTkButton(master=self,text="",image=CTkImage(dark_image=Image.open(utils.resource_path("images/dots.ico"))), 
                                    command=extra,fg_color="gray24", hover_color="gray20")
        self.optionsbtn.place(rely=0.05,relx=0.89,relwidth=.1,relheight=.45)

        CTkToolTip(self.title,f"{info["name"]} ({short})")

class UI:
    def __init__(self):
        print("Initialized UI")
        set_appearance_mode("Dark")

        self.window = Tk()
        self.window.geometry("800x600")
        self.window.iconbitmap(utils.catboxICO)
        self.window.title("Catboxxer")
        self.window.resizable(False,False)

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
        self.upload_queue = uploadList
        self.upload_queue_list = []

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

        ### // ALBUM TAB \\ ###

        def create_album():
            AlbumCreationDialog(ui=self)

        albums = self.tab_view.tab("Albums")

        create_album_btn = CTkButton(albums,text="Create album",command=create_album)
        create_album_btn.place(rely=.025,relx=.25,relwidth=.5,relheight=.0625)

        albumsList = CTkScrollableFrame(albums,corner_radius=30,border_color="white",border_width=1.5,fg_color="gray24")
        self.albumsList = albumsList
        self.albums_list = []
        albumsList.place(rely=.15,relx=.025,relwidth=.95,relheight=.85)

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

    def reoder_albums(self):
        for idx, widget in enumerate(self.albums_list):
            widget.grid(row=idx // self.mfc, column=idx % self.mfc)

    def add_uploaded_file(self,link:str):
        def on_destroy(_any):
            if new in self.uploaded_list:
                if not "manual" in list(new.keys()):
                    self.uploaded_list.remove(new)
                    self.reorder_uploaded_files()

        new = UploadedFile(self.filesList,link=link,ui=self)
        new.grid(row=len(self.uploaded_list)//self.mfc, column=len(self.uploaded_list)%self.mfc, padx=2.5, pady=5)
        self.uploaded_list.append(new)
        new.bind("<Destroy>",on_destroy)

    def remove_uploaded_file(self,link:str):
        for x in self.uploaded_list:
            if x.link == link:
                x.destroy()
                break
        
        for x in self.upload_queue_list:
            if x.link == link:
                x.destroy()
                break

    def clear_uploaded_files(self):
        for x in self.uploaded_list:
            x.manual = True
            x.destroy()
        self.uploaded_list.clear()

        for x in self.upload_queue_list:
            x.destroy()

    def add_album(self,short:str,info:dict):
        new = UploadedAlbum(self.albumsList,ui=self,short=short,info=info)
        row = len(self.albums_list) // self.mfc; column = len(self.albums_list) % self.mfc
        new.grid(row=row,column=column,padx=5,pady=2.5)

        def on_destroy(_any):
            if new in self.albums_list:
                if not "manual" in list(new.keys()):
                    self.albums_list.remove(new)
                    self.reoder_albums()
        
        new.bind("<Destroy>",on_destroy)
        self.albums_list.append(new)
    
    def remove_album(self,short:str):
        for x in self.albums_list:
            if x.short == short:
                x.destroy()
                break