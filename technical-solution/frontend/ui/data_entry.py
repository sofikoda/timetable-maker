import customtkinter as ctk
from tkinter import Canvas, messagebox, filedialog
from frontend.ui.utils.draw_vertical_gradient import draw_vertical_gradient
from pathlib import Path 
from PIL import Image 
from backend.database import (get_connection, insert_school_structure, create_timetable)
from backend.excel.validation.common import (ValidationError, validate_excel_file)

#imports of validation helper functions
from backend.excel.classrooms_validation import import_classrooms_excel
from backend.excel.students_validation import import_students_excel
from backend.excel.subjects_validation import import_subjects_excel
from backend.excel.teachers_validation import import_teachers_excel

from frontend.ui.action_page import ActionPage


class DataEntryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.imported_files = { 
            'subjects': None, 
            'teachers': None, 
            'students': None, 
            'classrooms': None }
        self.selected_cycle = None 
        self.import_links = {}
#Icon 
        ICON_PATH = Path(__file__).parent.parent / "icons" / "xls import.png"
        self.xls_icon = ctk.CTkImage(
            light_image=Image.open(ICON_PATH),
            dark_image=Image.open(ICON_PATH),
            size=(40, 40) )

#Drawing the acual frame 
        self.bg_canvas = Canvas(self, width=1600, height=1000, highlightthickness=0)
        #self.bg_canvas.place(x=0, y=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        draw_vertical_gradient(self.bg_canvas, 1600, 1000, "#E21B67", "#375BFF")
#Title 
        self.bg_canvas.create_text(
            720, 160,
            text="We need to collect some data to \nstart timetable generation...",
            fill="white",
            font=("Alexandria", 48, "bold"),
            anchor="center")

        structure_card = ctk.CTkFrame(
            self, 
            width=820, 
            height=170,
            corner_radius = 28, 
            fg_color = 'white')
        structure_card.place(relx=0.5, rely = 0.35, anchor='center')
        structure_card.pack_propagate(False) #the card size stays the same as it was defined by me

        ctk.CTkLabel(
            structure_card, 
            text='School Structure', 
            font=('Alexandria', 14, 'bold'), 
            text_color='#333652'
        ).place(x=30, y=20)

        ctk.CTkLabel( 
            structure_card, 
            text='Do you follow a one or a two week system?', 
            font=("Alexandria", 24, 'bold'),
            text_color="black"
        ).place(x=30, y=55)
        
        self.week1_btn = ctk.CTkButton(
            structure_card,
            text="1",
            width=40,
            height=32,
            fg_color="#E5E5E5",
            text_color="black",
            command=lambda: self.select_cycle(1))
        self.week1_btn.place(x=550, y=55)

        self.week2_btn = ctk.CTkButton(
            structure_card,
            text="2",
            width=40,
            height=32,
            fg_color="#E5E5E5",
            text_color="black",
            command=lambda: self.select_cycle(2))
        self.week2_btn.place(x=600, y=55)

        ctk.CTkLabel(
            structure_card,
            text="How many periods do you teach per day?",
            font=("Alexandria", 24, 'bold'),
            text_color="black"
        ).place(x=30, y=105)

        self.periods_entry = ctk.CTkEntry(
            structure_card,
            width=180,
            height=34,
            placeholder_text="Enter an integer",
            fg_color="#F8F8F8",
            text_color="black"
        )
        self.periods_entry.place(x=550, y=107)


        self.create_import_card(310, 460, "Students Information Entry", "students")
        self.create_import_card(730, 620, "Teachers Information Entry", "teachers")
        self.create_import_card(310, 620, "Classroom Information Entry", "classrooms")
        self.create_import_card(730, 460, "Subject Information Entry", "subjects")


        # Submit button
        submit_card = ctk.CTkFrame(
            self, 
            width = 560, 
            height = 70, 
            corner_radius=28,
            fg_color='white')
        submit_card.place(relx=0.5, rely=0.85, anchor = 'center')
        submit_card.configure(border_width=1, border_color = "#E5E5E5")
        submit_card.pack_propagate(False)

        self.submit_button = ctk.CTkButton(
            submit_card,
            text="Submit",
            width=200,
            height=46,
            font=("Alexandria", 16, "bold"),
            fg_color="#375BFF",
            hover_color="#B51752",
            command=self.handle_submit
        )
        self.submit_button.place(relx=0.5, rely=0.5, anchor="center")

#All the functions
    def select_cycle(self, cycle):
        self.selected_cycle = cycle

        self.week1_btn.configure(fg_color="#E5E5E5", text_color="black")
        self.week2_btn.configure(fg_color="#E5E5E5", text_color="black")

        if cycle == 1:
            self.week1_btn.configure(fg_color="#375BFF", text_color="white")
        else:
            self.week2_btn.configure(fg_color="#375BFF", text_color="white")
    def create_import_card(self, x,y, title, key):
        card = ctk.CTkFrame(
            self,
            width=380,
            height=135,
            corner_radius=28,
            fg_color="white"
        )
        card.place(x=x, y=y)
        card.grid_propagate(False)

        # Title
        ctk.CTkLabel(
            card,
            text=title,
            font=("Alexandria", 16, "bold"),
            text_color="#333652"
        ).place(x=20, y=20)


        ctk.CTkLabel(
            card,
            image=self.xls_icon,
            text=""
        ).place(x=20, y=70)

        link = ctk.CTkLabel( 
            card, 
            text="Import excel file", 
            font=("Alexandria", 24, "underline"),
            text_color = "black", 
            cursor = 'hand2'
        )
        link.place(x=65, y=72)

        link.bind("<Button-1>", lambda e: self.handle_import(key))
        self.import_links[key] = link 

    def mark_imported(self, key):
        label = self.import_links[key]
        label.configure(
            text="Imported",
            text_color="#375BFF")


    def handle_import(self, key):
        file_path = filedialog.askopenfilename(
            title="Select Excel file",
            filetypes=[("Excel files", "*.xlsx")])

        if not file_path:
            return

        try: 
            validate_excel_file(file_path)
        except ValidationError as e: 
            messagebox.showerror("Invalid Excel File", str(e))
            return 
        self.imported_files[key] = file_path 
        self.mark_imported(key)

#This functions checks that there is no information missing 
    def handle_submit(self):
        missing_files = [k for k, v in self.imported_files.items() if v is None]

        if missing_files:
            messagebox.showerror(
                "Missing files",
                f"Please import all files before submitting:\n{', '.join(missing_files)}")
            return

        if not self.periods_entry.get().isdigit(): 
            messagebox.showerror("Please enter a number of periods per day")
            return 

        if self.selected_cycle is None: 
            messagebox.showerror("You have not selected a week cycle for your school")
            return 
        #if not getattr(self.app, "user_id", None):
        #    messagebox.showerror("Error", "No user is signed in (user_id missing)")
        #    return 
        conn = None 
#if all the files have been imported and information about school has been entered timetable_id is created
        try:
            conn = get_connection()

            periods = int(self.periods_entry.get())
            structure_id = insert_school_structure(self.app.user_id, periods, self.selected_cycle)

            timetable_id = create_timetable(self.app.user_id, structure_id)

            import_subjects_excel(self.imported_files["subjects"], conn)
            import_teachers_excel(self.imported_files["teachers"], conn)
            import_students_excel(self.imported_files["students"], conn)
            import_classrooms_excel(self.imported_files["classrooms"], conn)

            self.app.show_page("ActionPage") #the user is redirected to the Action Page

        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))

        except Exception as e:
            messagebox.showerror("Unexpected Error", repr(e))

        finally:
            if conn is not None: 
                conn.close()