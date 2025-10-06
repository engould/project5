# 🧾 Customer Information Management System

This project is a simple Python-based application that allows users to enter, store, and view customer data using a graphical user interface (GUI) and an SQLite database.

---

## 📁 Project Structure

| File | Description |
|------|--------------|
| **app.py** | Launches the main Tkinter GUI where customers can enter their information (name, email, birthday, etc.). Upon submission, the data is stored in the `customers.db` database. |
| **readDatabase.py** | Opens a separate GUI to view all customer records stored in `customers.db`. Records are displayed in a sortable and scrollable table. |
| **check.py** | Script that reads and verifies records from `customers.db` (useful for testing or debugging database entries). |
| **customers.db** | SQLite database file that stores all submitted customer information. Automatically created if it doesn’t exist. |
| **README.md** | Documentation file describing the project, files, and usage. |

---

## 🚀 How to Run the Application

1. **Install Python (3.8 or higher)**  
   Make sure Python and `tkinter` are installed on your system.

2. **Clone or Download this Repository**
   ```bash
   git clone https://github.com/yourusername/customer-database.git
   cd customer-database

