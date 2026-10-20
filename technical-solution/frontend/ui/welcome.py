import customtkinter as ctk 
from tkinter import Canvas
from frontend.ui.utils.draw_vertical_gradient import draw_vertical_gradient
from frontend.ui.signup import SignupPage

class WelcomePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.bg_canvas = Canvas(self, width=1600, height=1000, highlightthickness=0)
        #self.bg_canvas.place(x=0, y=0)
        self.bg_canvas.pack(fill='both', expand = True)

        draw_vertical_gradient(self.bg_canvas, 1600, 1000, "#E21B67", "#375BFF")

        self.bg_canvas.create_text(
            720, 160,
            text="Welcome to your\nTimetable Maker",
            fill="white",
            font=("Alexandria", 48, "bold"),
            anchor="center")
        self.create_step(
            y=350,
            step="STEP 1",
            title="Enter your details",
            text="Start by adding classes, subjects, teachers, and classrooms. Add extra details about teachers’ availability, students’ optional subjects and the structure of your school. ")

        self.create_step(
            y=520,
            step="STEP 2",
            title="Generate your timetable",
            text="The algorithms automatically checks entered data and creates a conflict-free timetable for your school, entering unique requirements. ")

        self.create_step(
            y=690,
            step="STEP 3",
            title="Export & Share",
            text="Export your timetable in multiple formats, or share it online  with staff and students - keeping everyone on the same page,  effortlessly.")

        # ===== Bottom Button =====
        btn_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        btn_frame.place(relx=0.5, rely=0.92, anchor="center")

        ctk.CTkButton(
            btn_frame,
            text="Get started",
            width=200,
            height=45,
            font=("Alexandria", 16, "bold"),
            command=lambda: self.app.show_page("SignupPage")
        ).pack(padx=30, pady=20)

    def create_step(self, y, step, title, text):
        frame = ctk.CTkFrame(self, width=700, height=140, fg_color="white", corner_radius=20)
        frame.place(x=370, y=y)

        ctk.CTkLabel(frame, text=step, font=("Alexandria", 12), text_color="black").place(x=30, y=20)
        ctk.CTkLabel(frame, text=title, font=("Alexandria", 22, "bold"), text_color='black').place(x=30, y=45)
        ctk.CTkLabel(
            frame,
            text=text,
            font=("Alexandria", 14),
            text_color='black',
            wraplength=620,
            justify="left"
        ).place(x=30, y=80)




