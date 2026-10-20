import customtkinter as ctk
from frontend.ui.utils.draw_vertical_gradient import draw_vertical_gradient
from tkinter import Canvas, Frame, messagebox
from backend.database import create_user
from backend.validation import validate_email, validate_password
import sqlite3

class SignupPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        # ===== Background =====
        self.bg_canvas = Canvas(self, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        draw_vertical_gradient(
            self.bg_canvas, 1600, 1000,
            "#E21B67", "#375BFF"
        )

        # ===== Title =====
        self.bg_canvas.create_text(
            850, 210,
            text="Please register… or",
            fill="white",
            font=("Alexandria", 42, "bold"),
            anchor="e"
        )

        self.bg_canvas.create_text(
            855, 210,
            text=" sign in?",
            fill="white",
            font=("Alexandria", 42, "bold", "underline"),
            anchor="w",
            tags="signin_link"
        )

        self.bg_canvas.tag_bind(
            "signin_link",
            "<Button-1>",
            lambda e: self.app.show_page("SigninPage")
        )

        # ===== Card =====
        card = ctk.CTkFrame(
            self,
            width=600,
            height=520,
            corner_radius=28,
            fg_color="white"
        )
        card.place(relx=0.5, rely=0.55, anchor="center")
        card.pack_propagate(False)

        # ===== Name Row =====
        name_frame = ctk.CTkFrame(card, fg_color="transparent")
        name_frame.pack(pady=(50, 20))

        self.first_name = ctk.CTkEntry(
            name_frame,
            width=260,
            height=56,
            fg_color="#F8F8F8",
            text_color="black",
            placeholder_text="Enter your name..."
        )
        self.first_name.pack(side="left", padx=(0, 20))

        self.last_name = ctk.CTkEntry(
            name_frame,
            width=260,
            height=56,
            fg_color="#F8F8F8",
            text_color="black",
            placeholder_text="Enter your surname..."
        )
        self.last_name.pack(side="left")

        # ===== Email =====
        self.email = ctk.CTkEntry(
            card,
            width=530,
            height=56,
            fg_color="#F8F8F8",
            text_color="black",
            placeholder_text="you@school-domain.com"
        )
        self.email.pack(pady=(0, 20))

        # ===== Password =====
        self.password = ctk.CTkEntry(
            card,
            width=530,
            height=56,
            fg_color="#F8F8F8",
            text_color="black",
            placeholder_text="Password",
            show="*"
        )
        self.password.pack(pady=(0, 30))

        # ===== Register Button =====
        self.register_btn = ctk.CTkButton(
            card,
            text="Register",
            width=530,
            height=52,
            font=("Alexandria", 16, "bold"),
            fg_color="#375BFF",
            hover_color="#2C49CC", 
            command = self.register_user
        )
        self.register_btn.pack()


    def register_user(self): 
        first = self.first_name.get().strip()
        last = self.last_name.get().strip()
        email = self.email.get().strip()
        password = self.password.get().strip()
#make sure the user fills in the input fields 
        if not first or not last or not email or not password: 
            messagebox.showerror("Error", "All fields are required")
            return 
        if not validate_password(password): 
            messagebox.showerror("Error", "Password must be at least 8 characters long,\n contain an uppercase letter, a number,\n"
            "and a special character.")
            return
        if not validate_email(email): 
            messagebox.showerror("Error", 
            "You entered invalid email")
            return

        try: 
            user_id = create_user(first, last, email, password)
            self.app.user_id = user_id
            self.app.current_user_email = email
            self.app.show_page("DataEntryPage")
#hadles a database error if there is an email that already exists 
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists")

