"""
Basic Weather App - Advanced Tier
Oasis Infobyte Python Programming Internship, Task 4

A weather dashboard with a gradient background and a rounded card. It shows
current conditions, the next 6 hours, a 5-day forecast, weather icons,
a Celsius/Fahrenheit toggle and automatic location detection.
"""

import io
import os
import tkinter as tk
from datetime import datetime, timedelta, timezone

import requests
from PIL import Image, ImageTk

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
IP_URL = "https://ipinfo.io/json"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"
ZIP_COUNTRY = "IN"          # Change this if you are not in India
REQUEST_TIMEOUT = 10

C = {
    "sky_top": "#cdc6ef",
    "sky_bottom": "#a6cde8",
    "shadow": "#b4bfd9",
    "card": "#eef0f6",
    "text": "#2d2d33",
    "muted": "#6b7280",
    "line": "#c9ced8",
    "pill": "#dde5ee",
    "pill_hover": "#cbd7e4",
    "accent": "#4a90c2",
    "accent_hover": "#3b7db0",
    "error": "#d9485f",
    "ok": "#16865b",
}

FONT = "Segoe UI"
CARD_MARGIN = 28    # space between the window edge and the card
CARD_RADIUS = 28    # corner rounding of the card
CARD_INSET = 18     # space between the card edge and the frame that holds the widgets


class WeatherError(Exception):
    """A problem the user should see in the window."""


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def request_json(url, params):
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        raise WeatherError("The request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise WeatherError("Could not connect. Check your internet connection.")

    if response.status_code == 200:
        return response.json()
    if response.status_code == 401:
        raise WeatherError("Invalid API key. Check it, or wait for a new key to activate.")
    if response.status_code == 404:
        raise WeatherError("Location not found. Check the spelling.")
    raise WeatherError(f"Unexpected error (status code {response.status_code}).")


def build_location_params(text):
    if text.isdigit():
        return {"zip": f"{text},{ZIP_COUNTRY}"}
    return {"q": text}


def fetch_weather(location_params):
    params = dict(location_params, appid=API_KEY, units="metric")
    current = request_json(CURRENT_URL, params)
    forecast = request_json(FORECAST_URL, params)
    return current, forecast


def detect_city():
    data = request_json(IP_URL, {})
    city = data.get("city")
    if not city:
        raise WeatherError("Could not detect your city automatically.")
    return city


def load_icon(code, size):
    """Download a weather icon as a Tk image, or return None if it fails."""
    try:
        response = requests.get(ICON_URL.format(code), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).resize((size, size))
        return ImageTk.PhotoImage(image)
    except (requests.exceptions.RequestException, OSError):
        return None


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def local_time(timestamp, utc_offset):
    return datetime.fromtimestamp(timestamp, timezone(timedelta(seconds=utc_offset)))


def parse_forecast(forecast, utc_offset):
    """The free forecast gives one reading every 3 hours."""
    items = []
    for entry in forecast.get("list", []):
        items.append({
            "time": local_time(entry["dt"], utc_offset),
            "temp": entry["main"]["temp"],
            "min": entry["main"]["temp_min"],
            "max": entry["main"]["temp_max"],
            "icon": entry["weather"][0]["icon"],
            "desc": entry["weather"][0]["description"].capitalize(),
        })
    return items


def daily_summary(items):
    """Group the 3-hour readings by date and return up to 5 days."""
    days = {}
    for item in items:
        key = item["time"].date()
        if key not in days:
            days[key] = {"date": key, "min": item["min"], "max": item["max"],
                         "icon": item["icon"], "desc": item["desc"]}
        day = days[key]
        day["min"] = min(day["min"], item["min"])
        day["max"] = max(day["max"], item["max"])
        # Use a midday reading for the day's icon and description
        if item["time"].hour in (12, 13, 14, 15):
            day["icon"], day["desc"] = item["icon"], item["desc"]
    return list(days.values())[:5]


def format_temp(celsius, unit):
    if unit == "F":
        return f"{celsius * 9 / 5 + 32:.0f}°"
    return f"{celsius:.0f}°"


def location_name(data):
    country = data.get("sys", {}).get("country", "")
    return f"{data.get('name', 'Unknown')}, {country}" if country else data.get("name", "Unknown")


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(colour):
    colour = colour.lstrip("#")
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))


def blend(colour_a, colour_b, t):
    """Mix two colours. t=0 gives colour_a, t=1 gives colour_b."""
    r1, g1, b1 = hex_to_rgb(colour_a)
    r2, g2, b2 = hex_to_rgb(colour_b)
    return "#%02x%02x%02x" % (
        round(r1 + (r2 - r1) * t),
        round(g1 + (g2 - g1) * t),
        round(b1 + (b2 - b1) * t),
    )


def rounded_points(x1, y1, x2, y2, r):
    """Corner points for a rounded rectangle, drawn as a smooth polygon."""
    return [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]


def clear(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def make_button(parent, text, command, bg, hover, fg="white"):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     activebackground=hover, activeforeground=fg, relief="flat",
                     bd=0, font=(FONT, 10, "bold"), cursor="hand2", padx=14, pady=8)


def make_icon_label(parent, image, fallback_text, bg, fg):
    if image is not None:
        return tk.Label(parent, image=image, bg=bg)
    return tk.Label(parent, text=fallback_text, bg=bg, fg=fg, font=(FONT, 9))


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WeatherNow")
        self.geometry("1000x760")
        self.minsize(860, 600)
        self.configure(bg=C["sky_bottom"])

        self.unit = "C"
        self.current = None
        self.forecast_items = []
        self.utc_offset = 0
        self.icon_cache = {}

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Search for a city or ZIP code to see the forecast.")

        # The canvas draws the gradient and card, and scrolls the whole page.
        # The scrollbar is packed first so it stays on the right edge.
        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=C["sky_bottom"],
                                yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.bind("<Configure>", lambda event: self._redraw())

        self.card = tk.Frame(self.canvas, bg=C["card"])
        self.card.bind("<Configure>", lambda event: self._redraw())
        self.card_window = self.canvas.create_window(0, 0, window=self.card, anchor="nw")

        # Mouse wheel scrolls the page (Windows, Mac, and Linux)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

        self._build_content()
        self._show_placeholder()

        if not API_KEY:
            self.set_status("No API key found. Set OPENWEATHER_API_KEY, then restart.",
                            error=True)

    # ----- layout --------------------------------------------------------

    def _build_content(self):
        content = tk.Frame(self.card, bg=C["card"])
        content.pack(fill="both", expand=True, padx=24, pady=18)

        # Search row
        search = tk.Frame(content, bg=C["card"])
        search.pack(fill="x")

        entry = tk.Entry(search, textvariable=self.search_var, font=(FONT, 12),
                         bg=C["pill"], fg=C["text"], insertbackground=C["text"],
                         relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        entry.bind("<Return>", lambda event: self.search())

        make_button(search, "Search", self.search,
                    C["accent"], C["accent_hover"]).pack(side="left")
        make_button(search, "My location", self.use_my_location,
                    C["pill"], C["pill_hover"], fg=C["text"]).pack(side="left", padx=(8, 0))
        self.unit_button = make_button(search, "Show °F", self.toggle_unit,
                                       C["pill"], C["pill_hover"], fg=C["text"])
        self.unit_button.pack(side="left", padx=(8, 0))

        # Current conditions: text on the left, large icon on the right
        hero = tk.Frame(content, bg=C["card"])
        hero.pack(fill="x", pady=(20, 0))

        self.hero_left = tk.Frame(hero, bg=C["card"])
        self.hero_left.pack(side="left", fill="both", expand=True)

        self.hero_icon = tk.Label(hero, bg=C["card"])
        self.hero_icon.pack(side="right", padx=(10, 0))

        # Next 6 hours
        self.hourly_frame = tk.Frame(content, bg=C["card"])
        self.hourly_frame.pack(fill="x", pady=(18, 0))

        # Divider with the section title
        divider = tk.Frame(content, bg=C["card"])
        divider.pack(fill="x", pady=(18, 10))
        tk.Frame(divider, bg=C["line"], height=1).pack(side="left", fill="x", expand=True)
        tk.Label(divider, text="5-DAY FORECAST", bg=C["card"], fg=C["muted"],
                 font=(FONT, 10)).pack(side="left", padx=12)
        tk.Frame(divider, bg=C["line"], height=1).pack(side="left", fill="x", expand=True)

        # Footer: status on the left, last update on the right.
        # It is packed before the forecast so it always stays visible.
        footer = tk.Frame(content, bg=C["card"])
        footer.pack(fill="x", side="bottom", pady=(8, 0))

        self.status_label = tk.Label(footer, textvariable=self.status_var, bg=C["card"],
                                     fg=C["muted"], font=(FONT, 9), anchor="w")
        self.status_label.pack(side="left")

        self.updated_label = tk.Label(footer, text="", bg=C["card"], fg=C["muted"],
                                      font=(FONT, 9))
        self.updated_label.pack(side="right")

        # 5-day forecast
        self.daily_frame = tk.Frame(content, bg=C["card"])
        self.daily_frame.pack(fill="both", expand=True)

    def _redraw(self):
        """Redraw the gradient and card so they fit the window and the content."""
        width = self.canvas.winfo_width()
        if width <= 1:
            return

        margin, inset = CARD_MARGIN, CARD_INSET
        card_width = width - 2 * margin
        card_height = self.card.winfo_reqheight() + 2 * inset

        # Page height is the card plus margins, but never less than the window,
        # so the gradient always covers the visible area.
        content_height = 2 * margin + card_height + 8
        total_height = max(content_height, self.canvas.winfo_height())

        self.canvas.delete("bg", "shape")

        # Vertical gradient from lavender at the top to blue at the bottom
        for y in range(0, total_height, 2):
            colour = blend(C["sky_top"], C["sky_bottom"], y / total_height)
            self.canvas.create_rectangle(0, y, width, y + 2, fill=colour, outline="",
                                         tags="bg")

        x1, y1 = margin, margin
        x2, y2 = width - margin, margin + card_height

        shadow = rounded_points(x1 + 4, y1 + 8, x2 + 4, y2 + 8, CARD_RADIUS)
        self.canvas.create_polygon(shadow, smooth=True, fill=C["shadow"], outline="",
                                   tags="shape")
        shape = rounded_points(x1, y1, x2, y2, CARD_RADIUS)
        self.canvas.create_polygon(shape, smooth=True, fill=C["card"], outline="",
                                   tags="shape")

        # Place the widget frame inside the rounded card
        self.canvas.coords(self.card_window, x1 + inset, y1 + inset)
        self.canvas.itemconfigure(self.card_window, width=card_width - 2 * inset)
        self.canvas.tag_raise(self.card_window)

        self.canvas.configure(scrollregion=(0, 0, width, total_height))

    def _on_mousewheel(self, event):
        if event.num == 4 or (event.delta and event.delta > 0):
            step = -1
        elif event.num == 5 or (event.delta and event.delta < 0):
            step = 1
        else:
            return
        self.canvas.yview_scroll(step, "units")

    def _show_placeholder(self):
        clear(self.hero_left)
        clear(self.hourly_frame)
        clear(self.daily_frame)
        self.hero_icon.config(image="", text="")
        self.updated_label.config(text="")

        tk.Label(self.hero_left, text="Welcome", bg=C["card"], fg=C["text"],
                 font=(FONT, 30)).pack(anchor="w")
        tk.Label(self.hero_left, text="Type a city or ZIP code above, or use My location.",
                 bg=C["card"], fg=C["muted"], font=(FONT, 12)).pack(anchor="w", pady=(6, 0))

    def set_status(self, text, error=False):
        self.status_var.set(text)
        self.status_label.config(fg=C["error"] if error else C["ok"])

    def _icon(self, code, size):
        """Return a cached icon. Each icon is downloaded once per session."""
        key = (code, size)
        if key not in self.icon_cache:
            self.icon_cache[key] = load_icon(code, size)
        return self.icon_cache[key]

    # ----- actions -------------------------------------------------------

    def search(self):
        text = self.search_var.get().strip()
        if not text:
            self.set_status("Please enter a city name or ZIP code.", error=True)
            return
        self.lookup(build_location_params(text))

    def use_my_location(self):
        try:
            city = detect_city()
        except WeatherError as error:
            self.set_status(str(error), error=True)
            return
        self.search_var.set(city)
        self.lookup({"q": city})

    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_button.config(text="Show °C" if self.unit == "F" else "Show °F")
        if self.current:
            self.render_all()

    def lookup(self, location_params):
        if not API_KEY:
            self.set_status("No API key found. Set OPENWEATHER_API_KEY, then restart.",
                            error=True)
            return

        self.set_status("Loading weather...")
        self.update_idletasks()

        try:
            current, forecast = fetch_weather(location_params)
            utc_offset = current.get("timezone", 0)
            items = parse_forecast(forecast, utc_offset)
        except WeatherError as error:
            self.set_status(str(error), error=True)
            return
        except (KeyError, IndexError, TypeError, ValueError):
            self.set_status("The weather data was not in the expected format.", error=True)
            return

        # Save the new data only after it has loaded successfully
        self.current = current
        self.utc_offset = utc_offset
        self.forecast_items = items

        try:
            self.render_all()
        except (KeyError, IndexError, TypeError, ValueError):
            self.set_status("The weather data was incomplete. Try another location.",
                            error=True)
            return

        self.set_status(f"Showing weather for {location_name(current)}.")

    # ----- rendering -----------------------------------------------------

    def render_all(self):
        self.render_hero()
        self.render_hourly()
        self.render_daily()
        self.updated_label.config(text=f"Updated {datetime.now().strftime('%H:%M')}")

    def render_hero(self):
        clear(self.hero_left)
        data = self.current
        weather = data["weather"][0]
        main = data["main"]

        tk.Label(self.hero_left, text=f"Today  ·  {location_name(data)}",
                 bg=C["card"], fg=C["text"], font=(FONT, 15)).pack(anchor="w")

        temp_row = tk.Frame(self.hero_left, bg=C["card"])
        temp_row.pack(anchor="w", pady=(6, 0))
        tk.Label(temp_row, text=format_temp(main["temp"], self.unit), bg=C["card"],
                 fg=C["text"], font=(FONT, 72)).pack(side="left", anchor="s")
        tk.Label(temp_row, text=f"Feels like {format_temp(main['feels_like'], self.unit)}",
                 bg=C["card"], fg=C["muted"], font=(FONT, 14)).pack(side="left", anchor="s",
                                                                   padx=(10, 0), pady=(0, 18))

        tk.Label(self.hero_left,
                 text=f"{weather['description'].capitalize()}  ·  "
                      f"High {format_temp(main['temp_max'], self.unit)}  ·  "
                      f"Low {format_temp(main['temp_min'], self.unit)}",
                 bg=C["card"], fg=C["text"], font=(FONT, 13)).pack(anchor="w")

        sys_data = data.get("sys", {})
        sunrise = sunset = "-"
        if "sunrise" in sys_data and "sunset" in sys_data:
            sunrise = local_time(sys_data["sunrise"], self.utc_offset).strftime("%H:%M")
            sunset = local_time(sys_data["sunset"], self.utc_offset).strftime("%H:%M")
        wind_kmh = data.get("wind", {}).get("speed", 0) * 3.6

        tk.Label(self.hero_left,
                 text=f"Humidity {main['humidity']}%   ·   Wind {wind_kmh:.1f} km/h   ·   "
                      f"Pressure {main['pressure']} hPa   ·   "
                      f"Sunrise {sunrise}   ·   Sunset {sunset}",
                 bg=C["card"], fg=C["muted"], font=(FONT, 10)).pack(anchor="w", pady=(12, 0))

        icon = self._icon(weather["icon"], 130)
        if icon is not None:
            self.hero_icon.config(image=icon, text="")
        else:
            self.hero_icon.config(image="", text=weather["description"],
                                  fg=C["text"], font=(FONT, 11))

    def render_hourly(self):
        clear(self.hourly_frame)
        tk.Label(self.hourly_frame, text="NEXT 6 HOURS", bg=C["card"], fg=C["muted"],
                 font=(FONT, 10)).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(self.hourly_frame, bg=C["card"])
        row.pack(anchor="w")

        if not self.forecast_items:
            tk.Label(row, text="Forecast unavailable.", bg=C["card"], fg=C["muted"],
                     font=(FONT, 10)).pack(anchor="w")
            return

        # The free plan gives one reading every 3 hours, so 2 readings cover 6 hours
        for item in self.forecast_items[:2]:
            box = tk.Frame(row, bg=C["pill"], padx=20, pady=8)
            box.pack(side="left", padx=(0, 12))

            tk.Label(box, text=item["time"].strftime("%H:%M"), bg=C["pill"],
                     fg=C["muted"], font=(FONT, 10)).pack()
            icon = self._icon(item["icon"], 48)
            make_icon_label(box, icon, item["desc"], C["pill"], C["text"]).pack()
            tk.Label(box, text=format_temp(item["temp"], self.unit), bg=C["pill"],
                     fg=C["text"], font=(FONT, 15, "bold")).pack()

    def render_daily(self):
        clear(self.daily_frame)
        days = daily_summary(self.forecast_items)
        if not days:
            tk.Label(self.daily_frame, text="Forecast unavailable.", bg=C["card"],
                     fg=C["muted"], font=(FONT, 10)).pack(anchor="w")
            return

        for index, day in enumerate(days):
            if index > 0:
                tk.Frame(self.daily_frame, bg=C["line"], width=1).pack(
                    side="left", fill="y", pady=8)

            column = tk.Frame(self.daily_frame, bg=C["card"])
            column.pack(side="left", expand=True, fill="both")

            tk.Label(column, text=day["date"].strftime("%a"), bg=C["card"],
                     fg=C["text"], font=(FONT, 12)).pack()

            icon = self._icon(day["icon"], 56)
            make_icon_label(column, icon, day["desc"], C["card"], C["text"]).pack(pady=4)

            tk.Label(column, text=format_temp(day["max"], self.unit), bg=C["card"],
                     fg=C["text"], font=(FONT, 20)).pack()

            tk.Label(column, text=format_temp(day["min"], self.unit), bg=C["pill"],
                     fg=C["muted"], font=(FONT, 11), padx=14, pady=4).pack(pady=(6, 0))


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()