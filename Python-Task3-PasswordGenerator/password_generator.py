"""
Random Password Generator - Advanced Tier
Oasis Infobyte Python Programming Internship, Task 3
"""

import secrets
import string
import tkinter as tk

import pyperclip

MIN_LENGTH = 8
MAX_LENGTH = 20
DEFAULT_LENGTH = 20
AMBIGUOUS = "0OIl1"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"

COLORS = {
    "header": "#4c1d95",
    "header_text": "#ddd6fe",
    "bg": "#faf5ff",
    "card": "#ffffff",
    "border": "#e9d5ff",
    "text": "#2e1065",
    "muted": "#7c6a99",
    "accent": "#7c3aed",
    "accent_hover": "#6d28d9",
    "pink": "#db2777",
    "pink_hover": "#be185d",
    "track": "#f3e8ff",
    "entry_bg": "#fdf4ff",
}

STRENGTH_COLOURS = {"Weak": "#dc2626", "Medium": "#ca8a04", "Strong": "#0891b2"}

FONT = "Segoe UI"
MONO = "Consolas"


def make_card(parent):
    return tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["border"],
                    highlightthickness=1, padx=20, pady=12)


def make_title(parent, text):
    return tk.Label(parent, text=text, bg=COLORS["card"], fg=COLORS["text"],
                    font=(FONT, 12, "bold"))


def make_button(parent, text, command, colour, hover):
    return tk.Button(parent, text=text, command=command, bg=colour, fg="white",
                     activebackground=hover, activeforeground="white", relief="flat",
                     bd=0, font=(FONT, 11, "bold"), cursor="hand2", pady=6)


def make_checkbox(parent, text, variable):
    return tk.Checkbutton(parent, text=text, variable=variable, bg=COLORS["card"],
                          activebackground=COLORS["card"], selectcolor="white",
                          font=(FONT, 10), fg=COLORS["text"])


class PasswordGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")
        self.geometry("680x900")
        self.minsize(620, 800)
        self.resizable(True, True)
        self.configure(bg=COLORS["bg"])

        self.history = []
        self.strength_name = None
        self.strength_value = 0

        self.length_var = tk.IntVar(value=DEFAULT_LENGTH)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digit_var = tk.BooleanVar(value=True)
        self.symbol_var = tk.BooleanVar(value=True)
        self.no_ambiguous_var = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Choose your options and click Generate.")

        self._build_ui()

    # ----- layout --------------------------------------------------------

    def _build_ui(self):
        header = tk.Frame(self, bg=COLORS["header"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Password Generator", bg=COLORS["header"], fg="white",
                 font=(FONT, 20, "bold")).pack(anchor="w", padx=24, pady=(12, 0))
        tk.Label(header, text="Create strong, random passwords in seconds",
                 bg=COLORS["header"], fg=COLORS["header_text"],
                 font=(FONT, 10)).pack(anchor="w", padx=24)

        status = tk.Label(self, textvariable=self.status_var, bg=COLORS["card"],
                          fg=COLORS["muted"], anchor="w", font=(FONT, 9),
                          padx=20, pady=6)
        status.pack(fill="x", side="bottom")

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=12)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(2, weight=1)

        self._build_settings(body).grid(row=0, column=0, sticky="ew")
        self._build_output(body).grid(row=1, column=0, sticky="ew", pady=10)
        self._build_history(body).grid(row=2, column=0, sticky="nsew")

    def _build_settings(self, parent):
        frame = make_card(parent)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        make_title(frame, "Settings").grid(row=0, column=0, columnspan=2, sticky="w")

        length_row = tk.Frame(frame, bg=COLORS["card"])
        length_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        tk.Label(length_row, text=f"Length ({MIN_LENGTH}-{MAX_LENGTH})",
                 bg=COLORS["card"], fg=COLORS["muted"],
                 font=(FONT, 10)).pack(side="left")
        tk.Scale(length_row, from_=MIN_LENGTH, to=MAX_LENGTH, orient="horizontal",
                 variable=self.length_var, bg=COLORS["card"], troughcolor=COLORS["track"],
                 highlightthickness=0, activebackground=COLORS["accent"],
                 length=380).pack(side="left", fill="x", expand=True, padx=12)

        options = [
            ("Uppercase (A-Z)", self.upper_var),
            ("Lowercase (a-z)", self.lower_var),
            ("Numbers (0-9)", self.digit_var),
            ("Symbols (!@#$...)", self.symbol_var),
        ]
        for i, (text, variable) in enumerate(options):
            make_checkbox(frame, text, variable).grid(row=2 + i // 2, column=i % 2,
                                                      sticky="w", pady=2)

        make_checkbox(frame, "Exclude ambiguous characters (0, O, l, 1)",
                      self.no_ambiguous_var).grid(row=4, column=0, columnspan=2,
                                                  sticky="w", pady=2)

        make_button(frame, "Generate Password", self.generate,
                    COLORS["accent"], COLORS["accent_hover"]).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        return frame

    def _build_output(self, parent):
        frame = make_card(parent)
        frame.grid_columnconfigure(0, weight=1)
        make_title(frame, "Your password").grid(row=0, column=0, sticky="w")

        tk.Entry(frame, textvariable=self.password_var, state="readonly",
                 readonlybackground=COLORS["entry_bg"], fg=COLORS["text"],
                 font=(MONO, 15), justify="center", relief="solid", bd=1).grid(
            row=1, column=0, sticky="ew", pady=8, ipady=6)

        strength_row = tk.Frame(frame, bg=COLORS["card"])
        strength_row.grid(row=2, column=0, sticky="ew")
        tk.Label(strength_row, text="Strength", bg=COLORS["card"], fg=COLORS["muted"],
                 font=(FONT, 10)).pack(side="left")
        self.strength_label = tk.Label(strength_row, text="-", bg=COLORS["card"],
                                       fg=COLORS["muted"], font=(FONT, 10, "bold"))
        self.strength_label.pack(side="right")

        self.strength_canvas = tk.Canvas(frame, height=10, bg=COLORS["track"],
                                         highlightthickness=0)
        self.strength_canvas.grid(row=3, column=0, sticky="ew", pady=(5, 10))
        self.strength_canvas.bind("<Configure>", lambda event: self._draw_strength())

        make_button(frame, "Copy to Clipboard", self.copy_password,
                    COLORS["pink"], COLORS["pink_hover"]).grid(row=4, column=0, sticky="ew")
        return frame

    def _build_history(self, parent):
        frame = make_card(parent)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        make_title(frame, "Last 5 passwords").grid(row=0, column=0, columnspan=2, sticky="w")

        # Shows exactly 5 rows. The scrollbar is a backup if the window is very small.
        self.history_list = tk.Listbox(frame, height=5, font=(MONO, 13), bd=0,
                                       highlightthickness=0, activestyle="none",
                                       fg=COLORS["text"])
        self.history_list.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.history_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(8, 0))
        self.history_list.configure(yscrollcommand=scrollbar.set)

        tk.Label(frame, text="Kept in memory for this session only.", bg=COLORS["card"],
                 fg=COLORS["muted"], font=(FONT, 9)).grid(row=2, column=0, columnspan=2,
                                                          sticky="w", pady=(4, 0))
        return frame

    # ----- actions -------------------------------------------------------

    def build_character_groups(self):
        groups = []
        if self.upper_var.get():
            groups.append(string.ascii_uppercase)
        if self.lower_var.get():
            groups.append(string.ascii_lowercase)
        if self.digit_var.get():
            groups.append(string.digits)
        if self.symbol_var.get():
            groups.append(SYMBOLS)

        if self.no_ambiguous_var.get():
            groups = ["".join(c for c in group if c not in AMBIGUOUS) for group in groups]
        return groups

    def generate(self):
        groups = self.build_character_groups()
        if len(groups) < 2:
            self.status_var.set("Please select at least two character types.")
            return

        try:
            length = int(self.length_var.get())
        except (ValueError, tk.TclError):
            length = DEFAULT_LENGTH
        length = max(MIN_LENGTH, min(MAX_LENGTH, length))

        # One character from each selected group, so every type is used
        chars = [secrets.choice(group) for group in groups]

        # Fill the rest from all selected characters together
        all_chars = "".join(groups)
        chars += [secrets.choice(all_chars) for _ in range(length - len(chars))]

        # Shuffle so the guaranteed characters are not always at the start
        secrets.SystemRandom().shuffle(chars)

        password = "".join(chars)
        self.password_var.set(password)
        self.update_strength(password, len(groups))
        self.add_to_history(password)

        if self._copy(password):
            self.status_var.set("Password generated and copied to clipboard.")
        else:
            self.status_var.set("Password generated. Automatic copy failed, use the button.")

    def update_strength(self, password, group_count):
        length = len(password)
        if length >= 16 and group_count >= 3:
            name, value = "Strong", 100
        elif length >= 12:
            name, value = "Medium", 65
        else:
            name, value = "Weak", 30

        self.strength_name = name
        self.strength_value = value
        self.strength_label.config(text=name, fg=STRENGTH_COLOURS[name])
        self._draw_strength()

    def _draw_strength(self):
        canvas = self.strength_canvas
        canvas.delete("all")
        width = canvas.winfo_width()
        if self.strength_name is None or width <= 1:
            return
        fill_width = width * self.strength_value / 100
        canvas.create_rectangle(0, 0, fill_width, 10,
                                fill=STRENGTH_COLOURS[self.strength_name], outline="")

    def copy_password(self):
        password = self.password_var.get()
        if not password:
            self.status_var.set("Generate a password first.")
            return
        if self._copy(password):
            self.status_var.set("Password copied to clipboard.")
        else:
            self.status_var.set("Could not copy. Select the text and copy it manually.")

    def _copy(self, text):
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def add_to_history(self, password):
        self.history.insert(0, password)
        self.history = self.history[:5]
        self.history_list.delete(0, tk.END)
        for item in self.history:
            self.history_list.insert(tk.END, item)


if __name__ == "__main__":
    app = PasswordGenerator()
    app.mainloop()