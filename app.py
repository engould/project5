import os
import re
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "customers.db"


# ---------- Database helpers ----------
def connect(db_path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birthday TEXT NOT NULL,            -- stored as ISO 'YYYY-MM-DD'
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                preferred_contact TEXT NOT NULL CHECK (preferred_contact IN ('Email','Phone','Mail')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )


# ---------- Validation helpers ----------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_DIGITS_RE = re.compile(r"\d")

def is_valid_date_yyyy_mm_dd(text: str) -> bool:
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def clean_phone(raw: str) -> str:
    # Keep only digits; basic sanity check for 10+ digits (US style)
    digits = "".join(PHONE_DIGITS_RE.findall(raw))
    return digits

def validate_inputs(name, birthday, email, phone, address, contact_method) -> tuple[bool, str]:
    if not name.strip():
        return False, "Name is required."
    if not birthday.strip() or not is_valid_date_yyyy_mm_dd(birthday.strip()):
        return False, "Birthday must be in YYYY-MM-DD format (e.g., 2001-09-17)."
    if not email.strip() or not EMAIL_RE.match(email.strip()):
        return False, "Please enter a valid email (e.g., name@example.com)."

    phone_digits = clean_phone(phone)
    if len(phone_digits) < 10:
        return False, "Phone should include at least 10 digits."
    if not address.strip():
        return False, "Address is required."
    if contact_method not in ("Email", "Phone", "Mail"):
        return False, "Preferred contact must be Email, Phone, or Mail."
    return True, ""


# ---------- Insert ----------
def insert_customer(name, birthday, email, phone, address, preferred_contact) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO customers (name, birthday, email, phone, address, preferred_contact)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), birthday.strip(), email.strip(), clean_phone(phone), address.strip(), preferred_contact),
        )
        return cur.lastrowid


# ---------- GUI ----------
class CustomerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customer Information")
        self.geometry("560x400")
        self.resizable(False, False)

        # Main frame
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # Labels + Inputs
        self.name_var = tk.StringVar()
        self.birthday_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.contact_var = tk.StringVar(value="Email")

        # Name
        ttk.Label(container, text="Name:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=6)
        self.name_entry = ttk.Entry(container, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=6, columnspan=2)

        # Birthday
        ttk.Label(container, text="Birthday (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
        self.birth_entry = ttk.Entry(container, textvariable=self.birthday_var, width=20)
        self.birth_entry.grid(row=1, column=1, sticky="w", pady=6)

        # Email
        ttk.Label(container, text="Email:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
        self.email_entry = ttk.Entry(container, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=2, column=1, sticky="w", pady=6, columnspan=2)

        # Phone
        ttk.Label(container, text="Phone:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
        self.phone_entry = ttk.Entry(container, textvariable=self.phone_var, width=24)
        self.phone_entry.grid(row=3, column=1, sticky="w", pady=6)

        # Address (multi-line)
        ttk.Label(container, text="Address:").grid(row=4, column=0, sticky="ne", padx=(0, 8), pady=6)
        self.address_text = tk.Text(container, width=40, height=4)
        self.address_text.grid(row=4, column=1, sticky="w", pady=6, columnspan=2)

        # Preferred Contact
        ttk.Label(container, text="Preferred Contact:").grid(row=5, column=0, sticky="e", padx=(0, 8), pady=6)
        self.contact_combo = ttk.Combobox(
            container,
            textvariable=self.contact_var,
            values=["Email", "Phone", "Mail"],
            state="readonly",
            width=18,
        )
        self.contact_combo.grid(row=5, column=1, sticky="w", pady=6)

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(16, 0))

        self.submit_btn = ttk.Button(btn_frame, text="Submit", command=self.on_submit)
        self.submit_btn.grid(row=0, column=0, padx=6)

        self.clear_btn = ttk.Button(btn_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.grid(row=0, column=1, padx=6)

        # Keyboard shortcuts
        self.bind("<Return>", lambda _e: self.on_submit())

        # Nice initial focus
        self.name_entry.focus_set()

        # Tidy grid
        for i in range(0, 6):
            container.grid_rowconfigure(i, weight=0)
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=0)

    def on_submit(self):
        name = self.name_var.get()
        birthday = self.birthday_var.get()
        email = self.email_var.get()
        phone = self.phone_var.get()
        address = self.address_text.get("1.0", "end").strip()
        contact = self.contact_var.get()

        ok, err = validate_inputs(name, birthday, email, phone, address, contact)
        if not ok:
            messagebox.showerror("Validation Error", err)
            return

        try:
            new_id = insert_customer(name, birthday, email, phone, address, contact)
            messagebox.showinfo("Success", f"Customer saved with ID #{new_id}.")
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not save customer.\n\n{e}")

    def clear_form(self):
        self.name_var.set("")
        self.birthday_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_text.delete("1.0", "end")
        self.contact_var.set("Email")
        self.name_entry.focus_set()


if __name__ == "__main__":
    # Ensure DB exists
    init_db()

    # Let user know where the DB lives (useful in VS Code)
    if not os.path.exists(DB_FILE):
        # init_db already creates it; this branch is unlikely, but kept for clarity
        open(DB_FILE, "a").close()

    app = CustomerApp()
    app.mainloop()
