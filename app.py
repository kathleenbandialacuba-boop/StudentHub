
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import storage

BG = "#f3f6fa"
NAVY = "#112b3c"
TEAL = "#007f75"
WHITE = "#ffffff"

PROGRAMS = ["BSIT", "BSAM", "BSIS"]


class StudentHub(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("StudentHub | CICT")
        self.geometry("1100x700")
        self.configure(bg=BG)

        self.students = []

        self.create_widgets()
        self.refresh()

    def create_widgets(self):

        header = tk.Frame(self, bg=NAVY, height=90)
        header.pack(fill="x")

        tk.Label(
            header,
            text="STUDENTHUB | CICT",
            font=("Segoe UI", 22, "bold"),
            fg=WHITE,
            bg=NAVY
        ).pack(side="left", padx=25, pady=25)

        main = tk.Frame(self, bg=BG, padx=25, pady=20)
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text="Student Records",
            font=("Segoe UI", 22, "bold"),
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            main,
            text="BSIT • BSAM • BSIS | Department of CICT",
            bg=BG,
            fg="#65778a"
        ).pack(anchor="w", pady=(5, 15))

        tools = tk.Frame(main, bg=BG)
        tools.pack(fill="x", pady=10)

        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.display())

        ttk.Entry(
            tools,
            textvariable=self.search,
            width=35
        ).pack(side="left", padx=(0, 10))

        self.program = tk.StringVar(value="All Programs")

        ttk.Combobox(
            tools,
            textvariable=self.program,
            values=["All Programs"] + PROGRAMS,
            state="readonly",
            width=18
        ).pack(side="left", padx=5)

        self.program.trace_add("write", lambda *_: self.display())

        ttk.Button(
            tools,
            text="Refresh",
            command=self.refresh
        ).pack(side="right", padx=5)

        ttk.Button(
            tools,
            text="Export CSV",
            command=self.export
        ).pack(side="right", padx=5)

        columns = (
            "id",
            "name",
            "email",
            "department",
            "program",
            "amount"
        )

        self.table = ttk.Treeview(
            main,
            columns=columns,
            show="headings",
            height=16
        )

        headings = {
            "id": "STUDENT ID",
            "name": "STUDENT NAME",
            "email": "EMAIL ADDRESS",
            "department": "DEPARTMENT",
            "program": "PROGRAM",
            "amount": "CONTRIBUTION AMOUNT"
        }

        widths = {
            "id": 90,
            "name": 190,
            "email": 220,
            "department": 110,
            "program": 100,
            "amount": 170
        }

        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(col, width=widths[col], anchor="w")

        self.table.pack(fill="both", expand=True, pady=10)

        actions = tk.Frame(main, bg=BG)
        actions.pack(fill="x", pady=10)

        ttk.Button(
            actions,
            text="+ Add Student",
            command=self.add_student
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Edit Student",
            command=self.edit_student
        ).pack(side="left", padx=5)

        ttk.Button(
            actions,
            text="Delete Student",
            command=self.delete_student
        ).pack(side="left", padx=5)

        self.total_label = tk.Label(
            actions,
            text="Total Students: 0",
            font=("Segoe UI", 11, "bold"),
            bg=BG
        )

        self.total_label.pack(side="right")

    def refresh(self):
        try:
            self.students = storage.get_students()
            self.display()
        except Exception as error:
            messagebox.showerror("Database Error", str(error))

    def display(self):

        self.table.delete(*self.table.get_children())

        query = self.search.get().lower()
        selected_program = self.program.get()

        filtered = []

        for student in self.students:

            if selected_program != "All Programs":
                if student["program"] != selected_program:
                    continue

            searchable = (
                str(student["id"]) +
                student["name"] +
                student["email"] +
                student["program"]
            ).lower()

            if query not in searchable:
                continue

            filtered.append(student)

            self.table.insert(
                "",
                "end",
                iid=str(student["id"]),
                values=(
                    student["id"],
                    student["name"],
                    student["email"],
                    "CICT",
                    student["program"],
                    f"₱{float(student['contribution_amount']):,.2f}"
                )
            )

        self.total_label.config(
            text=f"Total Students: {len(filtered)}"
        )

    def student_form(self, title, student=None):

        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("400x400")
        window.configure(bg=WHITE)
        window.transient(self)
        window.grab_set()

        fields = {}

        values = {
            "name": student["name"] if student else "",
            "email": student["email"] if student else "",
            "program": student["program"] if student else "BSIT",
            "contribution_amount": (
                str(student["contribution_amount"]) if student else ""
            )
        }

        for field, label in [
            ("name", "Student Name"),
            ("email", "Email Address"),
            ("program", "Program"),
            ("contribution_amount", "Contribution Amount (₱)")
        ]:

            tk.Label(
                window,
                text=label,
                bg=WHITE,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", padx=30, pady=(12, 4))

            variable = tk.StringVar(value=values[field])

            if field == "program":
                widget = ttk.Combobox(
                    window,
                    textvariable=variable,
                    values=PROGRAMS,
                    state="readonly"
                )
            else:
                widget = ttk.Entry(
                    window,
                    textvariable=variable
                )

            widget.pack(fill="x", padx=30)

            fields[field] = variable

        def save():

            data = {
                key: value.get()
                for key, value in fields.items()
            }

            try:
                storage.save_student(
                    data,
                    student["id"] if student else None
                )

                messagebox.showinfo(
                    "Success",
                    "Student record saved successfully."
                )

                window.destroy()
                self.refresh()

            except Exception as error:
                messagebox.showerror("Error", str(error), parent=window)

        ttk.Button(
            window,
            text="Save Student",
            command=save
        ).pack(pady=25)

    def add_student(self):
        self.student_form("Add Student")

    def edit_student(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Student",
                "Please select a student first."
            )
            return

        student_id = int(selected[0])

        student = next(
            s for s in self.students if s["id"] == student_id
        )

        self.student_form("Edit Student", student)

    def delete_student(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Student",
                "Please select a student first."
            )
            return

        student_id = int(selected[0])

        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        ):

            try:
                storage.delete_student(student_id)
                self.refresh()

            except Exception as error:
                messagebox.showerror("Error", str(error))

    def export(self):

        if not self.students:
            messagebox.showinfo("Export", "No student records available.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="CICT_Students.csv"
        )

        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Student ID",
                    "Student Name",
                    "Email",
                    "Department",
                    "Program",
                    "Contribution Amount"
                ])

                for student in self.students:
                    writer.writerow([
                        student["id"],
                        student["name"],
                        student["email"],
                        "CICT",
                        student["program"],
                        student["contribution_amount"]
                    ])

            messagebox.showinfo("Export", "CSV exported successfully.")

        except OSError as error:
            messagebox.showerror("Export Error", str(error))


if __name__ == "__main__":
    StudentHub().mainloop()