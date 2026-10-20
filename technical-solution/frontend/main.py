import customtkinter as ctk
from backend.database import init_db
from frontend.app import App

if __name__ == '__main__':
    ctk.set_appearance_mode("system")
    app = App()
    init_db()
    app.mainloop()
    
    
    #from frontend.ui.welcome import WelcomePage
#from fronted.ui.choice import ChoicePage
#from fronted.ui.login import LoginPage
#from fronted.ui.signup import SignupPage



