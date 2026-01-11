from customtkinter import CTk, CTkTabview, set_appearance_mode

class TabView(CTkTabview):
    def __init__(self,parent,**kwargs):
        super().__init__(parent, **kwargs)
        
        self.add("Main")
        self.add("Albums")
        self.add("User")

class UI:
    def __init__(self):
        print("Initialized UI")
        set_appearance_mode("Dark")

        self.window = CTk()
        self.window.geometry("800x600")
        self.mainloop = self.window.mainloop

        self.tab_view = TabView(parent=self.window)
        self.tab_view.pack(fill="both", padx=20,pady=20,expand=True)

        self.window.protocol("WM_DELETE_WINDOW",self.exit)
    
    def exit(self):
        self.window.withdraw()

    def set_enabled(self,val:bool):
        if val:
            self.window.deiconify()
            self.window.lift()
            self.window.focus()
        else:
            self.window.withdraw()