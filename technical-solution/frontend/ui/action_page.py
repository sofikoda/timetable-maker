import customtkinter as ctk 
from tkinter import Canvas, filedialog, messagebox
from frontend.ui.utils.draw_vertical_gradient import draw_vertical_gradient
from backend.core_structure.option_blocks import build_option_table

from backend.database import get_connection, retrieve_subject_names
from backend.core_structure.student_allocation import export_student_allocations_to_excel, build_student_allocations, save_student_allocations_to_db
from backend.core_structure.timetable_generator import generate_timetable



class ActionPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
#Drawing the acual frame 
        self.bg_canvas = Canvas(self, width=1600, height=1000, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        draw_vertical_gradient(self.bg_canvas, 1600, 1000, "#E21B67", "#375BFF")
#Drawing a Title 
        self.bg_canvas.create_text(
            720, 160,
            text="Your data has been imported \nsuccessfully, now you can... ",
            fill="white",
            font=("Alexandria", 48, "bold"),
            anchor="center"
        )

#Button "View Option Block Table"
        btn_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        btn_frame.place(relx=0.5, rely=0.32, anchor="center")

        ctk.CTkButton(
            btn_frame,
            text="View Option Block Table",
            width=420,
            height=52,
            font=("Alexandria", 24, "bold"),
            command=self.show_option_block_popup #runs a function show_option_block_popup which is an attribute of ActionPage 
        ).pack(padx=30, pady=10)

#Button "Save Student Groups Allocation"
        btn_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        btn_frame.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkButton(
            btn_frame,
            text="Save Student Groups Allocation",
            width=420,
            height=52,
            font=("Alexandria", 24, "bold"),
            command=self.export_allocation_excel #runs a function export_allocation_excel which is an attribute of ActionPage 
        ).pack(padx=30, pady=10)


#Button Generate Timetable 
        btn_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        btn_frame.place(relx=0.5, rely=0.57, anchor="center")

        ctk.CTkButton(
            btn_frame,
            text="Generate a Timetable",
            width=420,
            height=52,
            font=("Alexandria", 24, "bold"),
            command=self.generate_and_view
        ).pack(padx=30, pady=10)


    def show_option_block_popup(self):
        blocks, num_blocks = build_option_table()

        #getting the subject names from a database 
        conn = get_connection()
        subject_names = retrieve_subject_names(conn)
        conn.close()

        #this is a table builder to visualise the table with option blocks 
        popup = ctk.CTkToplevel(self)
        popup.title("Option Block Table")
        popup.geometry("1000x620")
        popup.transient(self.winfo_toplevel())
        popup.lift()
        popup.after(0, popup.grab_set)
        

        title = ctk.CTkLabel(popup,
            text=f"Option Block Table (Blocks used: {num_blocks})",
            font=("Alexandria", 22, "bold"),
        )
        title.pack(pady=(16, 10))

        outer = ctk.CTkScrollableFrame(popup, width=860, height=400)
        outer.pack(padx=16, pady=10, fill='both', expand = True)

        block_names = sorted(blocks.keys())
        columns = []
        for block in block_names:
            column = []

            for subject_id in blocks[block]:
                subject_name = subject_names.get(subject_id, str(subject_id))
                column.append(subject_name)

            column.sort()
            columns.append(column)

        max_rows = 0
        for column in columns:
            if len(column) > max_rows:
                max_rows = len(column)
        def make_cell(parent, text, r, c, header=False):
            lbl = ctk.CTkLabel(
                parent,
                text=text,
                font=("Alexandria", 18, "bold") if header else ("Alexandria", 14),
                anchor="center" if header else "w",
                padx=10,
                pady=8,
                corner_radius=10,
                fg_color=("#375BFF" if header else "transparent"),
                text_color = 'white',)
            lbl.grid(row=r, column=c, sticky="nsew", padx=8, pady=8 if header else 4)
            return lbl

    # Make columns expand evenly
        for c in range(len(block_names)):
            outer.grid_columnconfigure(c, weight=1)

    # Headers (row 0)
        for c, b in enumerate(block_names):
            make_cell(outer, b, r=0, c=c, header=True)

    # Cells (rows 1..max_rows)
        for r in range(1, max_rows + 1):
            for c in range(len(block_names)):
                text = columns[c][r - 1] if (r - 1) < len(columns[c]) else ""
                make_cell(outer, text, r=r, c=c, header=False)

        close_btn = ctk.CTkButton(popup, text="Close", command=popup.destroy, width=120)
        close_btn.pack(pady=(6, 16))

    def export_allocation_excel(self):
        save_student_allocations_to_db(max_students=20, clear_existing=True)
        rows = build_student_allocations(max_students=20)

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
#error handling 
        if not path:
            return

        export_student_allocations_to_excel(path, rows)
        messagebox.showinfo("Success", "Exported student allocation to Excel.")
    def generate_and_view(self):
        try:
            generate_timetable()          # run timetable generation
            self.app.show_page("ViewPage")     # show the ViewPage
        except ValueError as e:
            messagebox.showerror("Timetable generation failed", str(e))




        






        

