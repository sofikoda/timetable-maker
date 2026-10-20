#from backend.validation import validate_email, validate_password

import customtkinter as ctk
from tkinter import Canvas, messagebox
from frontend.ui.utils.draw_vertical_gradient import draw_vertical_gradient
from backend.database import login_user
from frontend.ui.data_entry import DataEntryPage 
from backend.database import get_connection, has_imported_data



class SigninPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.failed_attempts = 0 
        self.max_attempts = 3 

        # Drawing the gradient 
        self.bg_canvas = Canvas(self, width=1600, height=1000, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        draw_vertical_gradient(self.bg_canvas, 1600, 1000, "#E21B67", "#375BFF")

        # Title 
        self.bg_canvas.create_text(
            700, 220,
            text="Please enter the details of your account",
            fill="white",
            font=("Alexandria", 42, "bold"),
            anchor="center")

        # Drawing a Card
        card = ctk.CTkFrame(
            self,
            width=520,
            height=420,
            corner_radius=28,
            fg_color="white")
        card.place(relx=0.5, rely=0.55, anchor="center")
        card.pack_propagate(False)  # IMPORTANT

        # Getting the inputs 
        self.email = ctk.CTkEntry(
            card,
            placeholder_text="Enter your email",
            width=420,
            height=56,
            fg_color="#F8F8F8",
            text_color="black")
        self.email.pack(pady=(50, 18))

        self.password = ctk.CTkEntry(
            card,
            placeholder_text="Password",
            show="*",
            width=420,
            height=56,
            fg_color="#F8F8F8",
            text_color="black")
        self.password.pack(pady=(0, 30))

        # Sign in button 
        ctk.CTkButton(
            card,
            text="Sign in",
            width=420,
            height=52,
            font=("Alexandria", 16, "bold"),
            fg_color="#375BFF",
            hover_color="#2C49CC", 
            command=self.handle_signin).pack(pady=(0,30))
        

        # Bottom text 
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack()

        ctk.CTkLabel(
            bottom_frame,
            text="Don’t have an account?",
            font=("Alexandria", 13),
            text_color="#666").pack(side="left")

        signup_label = ctk.CTkLabel(
            bottom_frame,
            text=" Sign up",
            font=("Alexandria", 13, "underline"),
            text_color="#375BFF",
            cursor="hand2", )
        signup_label.pack(side="left")

        signup_label.bind(
            "<Button-1>",
            lambda e: self.app.show_page("SignupPage"))

#User can have one timetable only which means one to one relationship between user and school strucuture    
    def handle_signin(self):
        email = self.email.get().strip()
        password = self.password.get()
#Error handling 
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return

        if self.failed_attempts >= self.max_attempts:
            messagebox.showerror("Account locked", "Too many failed attempts.")
            return

        user_id = login_user(email, password)

        if user_id:
            self.failed_attempts = 0
            self.app.user_id = user_id
            self.app.current_user_email = email

            if has_imported_data(user_id): 
                self.app.show_page('ActionPage') #so if the account exists and the data has been imported then we show Action Page
            else: 
                self.app.show_page("DataEntryPage") #if there is an account but the user hasn't imported the data then we show DataEntryPage
        else:
            self.failed_attempts += 1
            remaining = self.max_attempts - self.failed_attempts

            if remaining > 0:
                messagebox.showerror(
                    "Error",
                    f"Invalid email or password.\nAttempts remaining: {remaining}")
            else:
                messagebox.showerror(
                    "Account locked",
                    "Too many failed attempts. Please restart the app")
                self.signin_button.configure(state="disabled")

        
