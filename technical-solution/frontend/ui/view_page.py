import customtkinter as ctk
from frontend.ui.utils.draw_vertical_gradient import draw_vertical_gradient
from tkinter import Canvas, Frame, messagebox
from backend.services.timetable_export_service import export_person_timetable


class ViewPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        # Background
        self.bg_canvas = Canvas(self, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        draw_vertical_gradient(
            self.bg_canvas, 1600, 1000, "#E21B67", "#375BFF")
        # Title
        self.bg_canvas.create_text(
            720, 160,
            text="Enter student's or teacher's name\n to download the timetable",
            fill="white",
            font=("Alexandria", 48, "bold"),
            anchor="center")

        # Card
        card = ctk.CTkFrame(
            self,
            width=650,
            height=560,
            corner_radius=28,
            fg_color="white"
        )
        card.place(relx=0.5, rely=0.58, anchor="center")
        card.pack_propagate(False)

        # Role selector
        self.person_type = ctk.StringVar(value="student")

        role_label = ctk.CTkLabel(
            card,
            text="Select timetable type",
            text_color="black",
            font=("Alexandria", 20, "bold"))
        role_label.pack(pady=(35, 10))
        role_frame = ctk.CTkFrame(card, fg_color="transparent")
        role_frame.pack(pady=(0, 20))

        student_radio = ctk.CTkRadioButton(
            role_frame,
            text="Student",
            variable=self.person_type,
            value="student",
            text_color="black")
        student_radio.pack(side="left", padx=20)

        teacher_radio = ctk.CTkRadioButton(
            role_frame,
            text="Teacher",
            variable=self.person_type,
            value="teacher",
            text_color="black")
        teacher_radio.pack(side="left", padx=20)

        # Name row
        name_frame = ctk.CTkFrame(card, fg_color="transparent")
        name_frame.pack(pady=(20, 20))

        self.first_name = ctk.CTkEntry(
            name_frame,
            width=260,
            height=56,
            fg_color="#F8F8F8",
            text_color="black",
            placeholder_text="First name...")
        self.first_name.pack(side="left", padx=(0, 20))

        self.last_name = ctk.CTkEntry(
            name_frame,
            width=260,
            height=56,
            fg_color="#F8F8F8",
            text_color="black",
            placeholder_text="Last name...")
        self.last_name.pack(side="left")

        # Download button
        download_button = ctk.CTkButton(
            card,
            text="Download Timetable",
            width=300,
            height=55,
            corner_radius=16,
            fg_color="#375BFF",
            hover_color="#2447D6",
            font=("Alexandria", 18, "bold"),
            command=self.download_timetable #calling the download_timetable fucntion that is defined below
            )
        download_button.pack(pady=(30, 15))

    def download_timetable(self):
        first_name = self.first_name.get().strip().lower()
        last_name = self.last_name.get().strip().lower() 
        person_type = self.person_type.get().strip().lower()

#error hadling, making sure that the user inputs information 
        if not first_name or not last_name:
            messagebox.showerror("Missing information", "Please enter first and last name.")
            return

        try:
            file_path = export_person_timetable(
                person_type=person_type,
                first_name=first_name,
                last_name=last_name)
            messagebox.showinfo("Success", f"Timetable exported successfully.\n\nSaved to:\n{file_path}")
#Error handling if something is wrong with downloading
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export timetable.\n{e}")