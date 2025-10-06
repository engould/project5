import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "customers.db"

# ---------- Database Helper ----------
def fetch_customers():
    """Retrieve all customer records from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers;")
        rows = cur.fetchall()
        col_names = [description[0] for description in cur.description]
        conn.close()
        return col_names, rows
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error reading database:\n{e}")
        return [], []


# ---------- GUI ----------
class CustomerViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customer Database Viewer")
        self.geometry("900x500")

        # Title label
        ttk.Label(
            self, text="Customer Records", font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        # Table Frame
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Load data
        self.load_data()

        # Refresh Button
        ttk.Button(self, text="Refresh Data", command=self.refresh).pack(pady=10)

    def load_data(self):
        columns, data = fetch_customers()

        if not columns:
            ttk.Label(self.table_frame, text="No data found in database.").pack()
            return

        self.tree = ttk.Treeview(
            self.table_frame, columns=columns, show="headings", height=15
        )

        # Scrollbars
        y_scroll = ttk.Scrollbar(
            self.table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=y_scroll.set)
        y_scroll.pack(side="right", fill="y")

        # Set up headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c, False))
            self.tree.column(col, anchor="center", width=120)

        # Insert data
        for row in data:
            self.tree.insert("", "end", values=row)

        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        """Reload the table."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.load_data()

    def sort_by(self, col, descending):
        """Sort table by column."""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        try:
            data.sort(reverse=descending, key=lambda t: t[0])
        except TypeError:
            pass
        for index, (val, child) in enumerate(data):
            self.tree.move(child, "", index)
        self.tree.heading(col, command=lambda: self.sort_by(col, not descending))


if __name__ == "__main__":
    app = CustomerViewer()
    app.mainloop()
