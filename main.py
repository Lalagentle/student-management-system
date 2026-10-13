import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "students.db"


class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("900x580")
        self.root.minsize(760, 500)
        self.selected_id = None

        self.conn = sqlite3.connect(DB_NAME)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matric_no TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                level TEXT NOT NULL,
                email TEXT
            )
        """)
        self.conn.commit()

        self.build_ui()
        self.load_students()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def build_ui(self):
        title = ttk.Label(
            self.root,
            text="STUDENT MANAGEMENT SYSTEM",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=(15, 3))

        subtitle = ttk.Label(
            self.root,
            text="Add, search, update and remove student records"
        )
        subtitle.pack(pady=(0, 12))

        form = ttk.LabelFrame(self.root, text="Student Details", padding=12)
        form.pack(fill="x", padx=18, pady=5)

        self.matric_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.department_var = tk.StringVar(value="Computer Science")
        self.level_var = tk.StringVar(value="300 Level")
        self.email_var = tk.StringVar()
        self.search_var = tk.StringVar()

        ttk.Label(form, text="Matric Number *").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.matric_var, width=25).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form, text="Full Name *").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(form, text="Department *").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.department_var, width=25).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form, text="Level *").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ttk.Combobox(
            form, textvariable=self.level_var,
            values=["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"],
            state="readonly", width=27
        ).grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(form, text="Email (optional)").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.email_var, width=25).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        for col in (1, 3):
            form.columnconfigure(col, weight=1)

        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", padx=18, pady=8)
        ttk.Button(buttons, text="Add Student", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Update Selected", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete Selected", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=22, pady=(3, 7))
        ttk.Label(search_frame, text="Search by name or matric number:").pack(side="left", padx=(0, 8))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=35)
        search_entry.pack(side="left", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda _event: self.load_students())
        ttk.Button(search_frame, text="Show All", command=self.show_all).pack(side="left")

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        columns = ("id", "matric_no", "full_name", "department", "level", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "id": "ID", "matric_no": "Matric Number", "full_name": "Full Name",
            "department": "Department", "level": "Level", "email": "Email"
        }
        widths = {"id": 45, "matric_no": 145, "full_name": 185, "department": 145, "level": 95, "email": 180}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def validate_form(self):
        matric = self.matric_var.get().strip()
        name = self.name_var.get().strip()
        department = self.department_var.get().strip()
        level = self.level_var.get().strip()
        email = self.email_var.get().strip()
        if not matric or not name or not department or not level:
            messagebox.showwarning("Missing information", "Please fill in matric number, full name, department and level.")
            return None
        if email and ("@" not in email or "." not in email.split("@")[-1]):
            messagebox.showwarning("Invalid email", "Enter a valid email address or leave the email field empty.")
            return None
        return matric, name, department, level, email

    def add_student(self):
        values = self.validate_form()
        if not values:
            return
        try:
            self.conn.execute(
                "INSERT INTO students (matric_no, full_name, department, level, email) VALUES (?, ?, ?, ?, ?)",
                values
            )
            self.conn.commit()
            self.load_students()
            self.clear_form()
            self.status_var.set("Student record added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate matric number", "That matric number already exists. Use a unique matric number.")

    def update_student(self):
        if self.selected_id is None:
            messagebox.showinfo("Select a record", "Select a student from the table before updating.")
            return
        values = self.validate_form()
        if not values:
            return
        try:
            self.conn.execute(
                "UPDATE students SET matric_no=?, full_name=?, department=?, level=?, email=? WHERE id=?",
                (*values, self.selected_id)
            )
            self.conn.commit()
            self.load_students()
            self.clear_form()
            self.status_var.set("Student record updated successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate matric number", "Another record already uses that matric number.")

    def delete_student(self):
        if self.selected_id is None:
            messagebox.showinfo("Select a record", "Select a student from the table before deleting.")
            return
        if not messagebox.askyesno("Confirm deletion", "Delete the selected student record?"):
            return
        self.conn.execute("DELETE FROM students WHERE id=?", (self.selected_id,))
        self.conn.commit()
        self.load_students()
        self.clear_form()
        self.status_var.set("Student record deleted.")

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = self.search_var.get().strip()
        if query:
            rows = self.conn.execute(
                """SELECT id, matric_no, full_name, department, level, email
                   FROM students
                   WHERE matric_no LIKE ? OR full_name LIKE ?
                   ORDER BY full_name""",
                (f"%{query}%", f"%{query}%")
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT id, matric_no, full_name, department, level, email FROM students ORDER BY full_name"
            ).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.status_var.set(f"{len(rows)} student record(s) displayed.")

    def on_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        row = self.tree.item(selection[0], "values")
        self.selected_id = int(row[0])
        self.matric_var.set(row[1])
        self.name_var.set(row[2])
        self.department_var.set(row[3])
        self.level_var.set(row[4])
        self.email_var.set(row[5] or "")

    def clear_form(self):
        self.selected_id = None
        self.matric_var.set("")
        self.name_var.set("")
        self.department_var.set("Computer Science")
        self.level_var.set("300 Level")
        self.email_var.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def show_all(self):
        self.search_var.set("")
        self.load_students()

    def close_app(self):
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()
