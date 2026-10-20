import customtkinter as ctk 

from frontend.ui.welcome import WelcomePage 
from frontend.ui.signin import SigninPage
from frontend.ui.signup import SignupPage 
from frontend.ui.data_entry import DataEntryPage
from frontend.ui.action_page import ActionPage
from frontend.ui.view_page import ViewPage
from backend.database import get_connection

 
class App(ctk.CTk):
    def __init__ (self): #whenever you create a new object of this class you are automatically call this function 
        super().__init__()
        self.user_id = None 
        self.db_connection = get_connection()

        self.title("Your Timetable Maker")
        window_width = 1440 
        window_height = 1024

#get the screen dimension 
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

#finding the center point 
        center_x = int(screen_width/2 - window_width /2)
        center_y = int(screen_height/2 - window_height / 2)

        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.resizable(False, False)
        self.container = ctk.CTkFrame(self) #the first page of a big stack wiht all the pages, creating a frame inside my main window 

        #make sure that your pages fill the actual window and you do not have weird gaps
        self.container.pack(fill='both', expand = True )

        self.pages = {} #dictionary where we store all the page instances

        # 
        for PageClass in (WelcomePage, SigninPage, SignupPage, DataEntryPage, ActionPage, ViewPage):
            page = PageClass(self.container, self)
            self.pages[PageClass.__name__] = page
            page.place(relwidth=1, relheight=1)

        
        self.show_page('WelcomePage')
        

    def show_page(self, page_name): 
        page = self.pages.get(page_name) #give me a value for a key defined by page_name but return None if it doenst exist

        if page: #passing an object which is treated as True 
            page.tkraise() #bring the page to the front 