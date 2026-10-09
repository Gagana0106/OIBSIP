
"""
BMI Calculator - Advanced Tier
OASIS INFOBYTE Python Programming Internship - Task 2

Features:
1. Tkinter graphical user interface
2. BMI calculation and classification
3. Colour-coded results
4. Multiple users
5. SQLite database for historical records
6. BMI history viewer
7. BMI trend graph using Matplotlib
8. Input validation and database error handling
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
from datetime import datetime

# Matplotlib is used for the BMI trend graph.
# If it is not installed, install it using:
# python -m pip install matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# -------------------- CONFIGURATION --------------------

DB_NAME = "bmi_records.db"

WEIGHT_MIN, WEIGHT_MAX = 1, 300
HEIGHT_MIN, HEIGHT_MAX = 0.5, 2.5

COLORS = {
    "Underweight": "#3498DB",
    "Normal": "#27AE60",
    "Overweight": "#E67E22",
    "Obese": "#E74C3C",
}


# -------------------- DATABASE --------------------

def initialize_database():
    """Create the database and table if they do not exist."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            """)
    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not initialize the database:\n{error}"
        )
        return False

    return True


def save_record(name, weight, height, bmi, category):
    """Save a BMI record to SQLite."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            conn.execute("""
                INSERT INTO bmi_records
                (name, weight, height, bmi, category, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, weight, height, bmi, category,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        return True

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not save the BMI record:\n{error}"
        )
        return False


def fetch_records(name):
    """Retrieve historical BMI records for a particular user."""
    try:
        with sqlite3.connect(DB_NAME, timeout=5) as conn:
            cursor = conn.execute("""
                SELECT id, name, weight, height, bmi,
                       category, recorded_at
                FROM bmi_records
                WHERE name = ? COLLATE NOCASE
                ORDER BY id DESC
            """, (name,))
            return cursor.fetchall()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not retrieve BMI history:\n{error}"
        )
        return None


# -------------------- BMI LOGIC --------------------

def calculate_bmi(weight, height):
    """Calculate BMI using weight in kg and height in metres."""
    return weight / (height ** 2)


def classify_bmi(bmi):
    """Return the BMI category."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def validate_inputs(name, weight_text, height_text):
    """Validate the name, weight and height entered by the user."""
    name = name.strip()

    if not name:
        messagebox.showwarning(
            "Input Error", "Please enter the user's name."
        )
        return None

    try:
        weight = float(weight_text)
        height = float(height_text)
    except ValueError:
        messagebox.showwarning(
            "Input Error",
            "Weight and height must be numeric values."
        )
        return None

    if not math.isfinite(weight) or not math.isfinite(height):
        messagebox.showwarning(
            "Input Error",
            "Please enter finite numeric values."
        )
        return None

    if not WEIGHT_MIN <= weight <= WEIGHT_MAX:
        messagebox.showwarning(
            "Input Error",
            f"Weight must be between {WEIGHT_MIN} and "
            f"{WEIGHT_MAX} kg."
        )
        return None

    if not HEIGHT_MIN <= height <= HEIGHT_MAX:
        messagebox.showwarning(
            "Input Error",
            f"Height must be between {HEIGHT_MIN} and "
            f"{HEIGHT_MAX} metres."
        )
        return None

    return name, weight, height


# -------------------- MAIN APPLICATION --------------------

class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator | OASIS INFOBYTE")
        self.root.geometry("720x650")
        self.root.minsize(620, 600)
        self.root.configure(bg="#F2F5F9")

        self.current_name = ""

        self.create_widgets()

    def create_widgets(self):
        """Build the main application interface."""

        # Header
        header = tk.Frame(self.root, bg="#203864", pady=18)
        header.pack(fill="x")

        tk.Label(
            header,
            text="BMI CALCULATOR",
            font=("Arial", 22, "bold"),
            bg="#203864",
            fg="white"
        ).pack()

        tk.Label(
            header,
            text="Calculate, save and track your BMI",
            font=("Arial", 10),
            bg="#203864",
            fg="#DCE6F1"
        ).pack(pady=(5, 0))

        # Input section
        form = tk.Frame(self.root, bg="white", padx=28, pady=20)
        form.pack(fill="x", padx=25, pady=20)

        tk.Label(
            form, text="User Name",
            font=("Arial", 11, "bold"), bg="white"
        ).grid(row=0, column=0, sticky="w", pady=9)

        self.name_entry = ttk.Entry(form, width=30, font=("Arial", 11))
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=15, pady=9)

        tk.Label(
            form, text="Weight (kg)",
            font=("Arial", 11, "bold"), bg="white"
        ).grid(row=1, column=0, sticky="w", pady=9)

        self.weight_entry = ttk.Entry(form, width=30, font=("Arial", 11))
        self.weight_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=9)

        tk.Label(
            form, text="Height (metres)",
            font=("Arial", 11, "bold"), bg="white"
        ).grid(row=2, column=0, sticky="w", pady=9)

        self.height_entry = ttk.Entry(form, width=30, font=("Arial", 11))
        self.height_entry.grid(row=2, column=1, sticky="ew", padx=15, pady=9)

        form.columnconfigure(1, weight=1)

        # Calculate button
        ttk.Button(
            form,
            text="Calculate BMI",
            command=self.calculate
        ).grid(row=3, column=0, columnspan=2, pady=(15, 5), ipadx=20, ipady=5)

        # Results section
        result_frame = tk.Frame(
            self.root, bg="white", padx=20, pady=18
        )
        result_frame.pack(fill="x", padx=25, pady=(0, 15))

        tk.Label(
            result_frame,
            text="YOUR RESULT",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#667085"
        ).pack()

        self.bmi_label = tk.Label(
            result_frame,
            text="BMI: --",
            font=("Arial", 25, "bold"),
            bg="white",
            fg="#203864"
        )
        self.bmi_label.pack(pady=5)

        self.category_label = tk.Label(
            result_frame,
            text="Enter your details to calculate BMI",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#667085"
        )
        self.category_label.pack()

        # Action buttons
        actions = tk.Frame(self.root, bg="#F2F5F9")
        actions.pack(pady=5)

        ttk.Button(
            actions,
            text="View BMI History",
            command=self.show_history
        ).grid(row=0, column=0, padx=8, ipadx=8, ipady=5)

        ttk.Button(
            actions,
            text="Show BMI Trend Graph",
            command=self.show_graph
        ).grid(row=0, column=1, padx=8, ipadx=8, ipady=5)

        ttk.Button(
            actions,
            text="Clear Fields",
            command=self.clear_fields
        ).grid(row=0, column=2, padx=8, ipadx=8, ipady=5)

        tk.Label(
            self.root,
            text="Records are stored locally in an SQLite database.",
            font=("Arial", 9),
            bg="#F2F5F9",
            fg="#667085"
        ).pack(side="bottom", pady=12)

    # -------------------- CALCULATE --------------------

    def calculate(self):
        """Calculate BMI, display the result and save the record."""

        values = validate_inputs(
            self.name_entry.get(),
            self.weight_entry.get(),
            self.height_entry.get()
        )

        if values is None:
            return

        name, weight, height = values

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)

        self.current_name = name

        self.bmi_label.config(
            text=f"BMI: {bmi:.2f}",
            fg=COLORS[category]
        )

        self.category_label.config(
            text=f"Category: {category}",
            fg=COLORS[category]
        )

        # Save every successful calculation.
        saved = save_record(name, weight, height, bmi, category)

        if saved:
            self.root.title(
                f"BMI Calculator | Current User: {name}"
            )

    # -------------------- HISTORY --------------------

    def show_history(self):
        """Display the selected user's saved BMI records."""

        name = self.name_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "User Required",
                "Enter a user's name to view their history."
            )
            return

        records = fetch_records(name)

        if records is None:
            return

        if not records:
            messagebox.showinfo(
                "No Records",
                f"No BMI records found for {name}."
            )
            return

        window = tk.Toplevel(self.root)
        window.title(f"BMI History - {name}")
        window.geometry("850x350")

        tk.Label(
            window,
            text=f"BMI HISTORY — {name}",
            font=("Arial", 15, "bold")
        ).pack(pady=12)

        columns = (
            "date", "weight", "height", "bmi", "category"
        )

        table = ttk.Treeview(
            window, columns=columns, show="headings"
        )

        table.heading("date", text="Date & Time")
        table.heading("weight", text="Weight (kg)")
        table.heading("height", text="Height (m)")
        table.heading("bmi", text="BMI")
        table.heading("category", text="Category")

        table.column("date", width=190)
        table.column("weight", width=110, anchor="center")
        table.column("height", width=110, anchor="center")
        table.column("bmi", width=90, anchor="center")
        table.column("category", width=150, anchor="center")

        for record in records:
            _, record_name, weight, height, bmi, category, date = record

            table.insert(
                "",
                "end",
                values=(
                    date,
                    f"{weight:.2f}",
                    f"{height:.2f}",
                    f"{bmi:.2f}",
                    category
                )
            )

        scrollbar = ttk.Scrollbar(
            window, orient="vertical", command=table.yview
        )
        table.configure(yscrollcommand=scrollbar.set)

        table.pack(
            side="left", fill="both", expand=True,
            padx=(12, 0), pady=10
        )
        scrollbar.pack(
            side="right", fill="y", padx=(0, 12), pady=10
        )

    # -------------------- BMI TREND GRAPH --------------------

    def show_graph(self):
        """Plot the selected user's historical BMI values."""

        name = self.name_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "User Required",
                "Enter a user's name to view their BMI graph."
            )
            return

        records = fetch_records(name)

        if records is None:
            return

        if len(records) < 2:
            messagebox.showinfo(
                "Insufficient Data",
                "At least two BMI records are required to "
                "display a trend. Calculate BMI again for this user."
            )
            return

        # Records are returned newest first; reverse them for the graph.
        records.reverse()

        dates = [record[6] for record in records]
        bmis = [record[4] for record in records]

        window = tk.Toplevel(self.root)
        window.title(f"BMI Trend - {name}")
        window.geometry("800x520")

        figure = Figure(figsize=(8, 4.5), dpi=100)
        axis = figure.add_subplot(111)

        axis.plot(
            range(1, len(bmis) + 1),
            bmis,
            marker="o",
            linewidth=2,
            color="#2878B5",
            label="BMI"
        )

        axis.axhline(
            18.5, color="#3498DB", linestyle="--",
            linewidth=1, label="Underweight boundary"
        )
        axis.axhline(
            25, color="#27AE60", linestyle="--",
            linewidth=1, label="Normal BMI upper boundary"
        )
        axis.axhline(
            30, color="#E74C3C", linestyle="--",
            linewidth=1, label="Obesity boundary"
        )

        axis.set_title(f"BMI Trend for {name}")
        axis.set_xlabel("Record Number")
        axis.set_ylabel("BMI")
        axis.set_xticks(range(1, len(dates) + 1))
        axis.grid(True, alpha=0.3)
        axis.legend(fontsize=8)

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10
        )

        tk.Label(
            window,
            text=(
                f"Records shown: {len(bmis)} | "
                f"First: {dates[0]} | Latest: {dates[-1]}"
            ),
            font=("Arial", 9)
        ).pack(pady=(0, 8))

    # -------------------- CLEAR FIELDS --------------------

    def clear_fields(self):
        """Clear the input fields and result display."""

        self.name_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)

        self.bmi_label.config(
            text="BMI: --", fg="#203864"
        )
        self.category_label.config(
            text="Enter your details to calculate BMI",
            fg="#667085"
        )

        self.current_name = ""
        self.root.title("BMI Calculator | OASIS INFOBYTE")


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    root = tk.Tk()

    if initialize_database():
        app = BMICalculator(root)
        root.mainloop()
    else:
        root.destroy()