import time
from PIL import Image, ImageDraw
# GS Removed threading from clock!

class Clock:

    """
    GS modified version +0.5
    Quadify's clever clock system, reloaded. Literally
    – All functionality as default – user can select clock design and store it
    – GS removed background threading, instead treating 'clock' like a mode that can be switched to and reloaded
    – Uses tick to keep track of time. stop_mode and start_mode called in mode_manager 
    """
    
    def __init__(self, display_manager, config, volumio_listener):
        self.display_manager = display_manager
        self.volumio_listener = volumio_listener
        self.config = config

        self.font_y_offsets = {
            "clock_sans": -15,
            "clock_dots": -10,
            "clock_digital": 0,
            "clock_bold": -5
        }

        self.font_line_spacing = {
            "clock_sans": 15,
            "clock_dots": 10,
            "clock_digital": 8,
            "clock_bold": 12
        }

        self.date_font_map = {
            "clock_sans": "clockdate_sans",
            "clock_dots": "clockdate_dots",
            "clock_digital": "clockdate_digital",
            "clock_bold": "clockdate_bold"
        }

    # GS New clock is a 'mode,' not a background thread, able to switch to and from clock cleanly
        self.is_active = False
        self.last_tick = 0

    def start_mode(self):
        self.is_active = True
        self.last_tick = 0
        print("Clock: Started.")
        self.draw_clock()  # Draw immediately on entry

    def stop_mode(self):
        self.is_active = False
        self.display_manager.clear_screen()
        print("Clock: Stopped.")

    def tick(self):
        if not self.is_active:
            return
        now = time.time()
        if now - self.last_tick >= 1:
            self.draw_clock()
            self.last_tick = now

    # GS Draw the clock as usual
    def draw_clock(self):
        time_font_key = self.config.get("clock_font_key", "clock_digital")
        if time_font_key not in self.display_manager.fonts:
            print(f"Warning: '{time_font_key}' not loaded; fallback to 'clock_digital'")
            time_font_key = "clock_digital"

        date_font_key = self.date_font_map.get(time_font_key, "clockdate_digital")

        show_seconds = self.config.get("show_seconds", False)
        time_str = time.strftime("%H:%M:%S") if show_seconds else time.strftime("%H:%M")

        show_date = self.config.get("show_date", False)
        date_str = time.strftime("%d %b %Y") if show_date else None

        y_offset = self.font_y_offsets.get(time_font_key, 0)
        line_gap = self.font_line_spacing.get(time_font_key, 10)

        w = self.display_manager.oled.width
        h = self.display_manager.oled.height
        img = Image.new("RGB", (w, h), "black")
        draw = ImageDraw.Draw(img)

        time_font = self.display_manager.fonts[time_font_key]
        date_font = self.display_manager.fonts.get(date_font_key, time_font)

        lines = []
        if time_str:
            lines.append((time_str, time_font))
        if date_str:
            lines.append((date_str, date_font))

        total_height = 0
        line_dims = []
        for (text, font) in lines:
            box = draw.textbbox((0, 0), text, font=font)
            lw = box[2] - box[0]
            lh = box[3] - box[1]
            line_dims.append((lw, lh, font))
            total_height += lh

        if len(lines) == 2:
            total_height += line_gap

        start_y = (h - total_height) // 2 + y_offset
        y_cursor = start_y

        for i, (text, font) in enumerate(lines):
            lw, lh, the_font = line_dims[i]
            x_pos = (w - lw) // 2
            draw.text((x_pos, y_cursor), text, font=the_font, fill="white")
            y_cursor += lh
            if i < len(lines) - 1:
                y_cursor += line_gap

        final_img = img.convert(self.display_manager.oled.mode)
        self.display_manager.oled.display(final_img)
