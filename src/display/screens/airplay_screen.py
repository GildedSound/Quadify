import os
import logging
from PIL import Image, ImageDraw, ImageFont
import threading
import time
import requests
from io import BytesIO
import itertools
from urllib.parse import urlparse, parse_qs, quote

class AirPlayScreen:
    def __init__(self, display_manager, volumio_listener, mode_manager):
        # Initialize logging and dependencies
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        self.display_manager = display_manager
        self.volumio_listener = volumio_listener
        self.mode_manager = mode_manager

        # Setup screen state and threading controls
        self.is_active = False
        self.latest_state = None
        self.current_state = None
        self.state_lock = threading.Lock()
        self.update_event = threading.Event()
        self.stop_event = threading.Event()

        # Scrolling offsets for long text
        self.scroll_offset_title = 0
        self.scroll_offset_artist = 0

        # Load fonts from display manager or fall back to default
        self.font_title = display_manager.fonts.get('radio_title', ImageFont.load_default())
        self.font_small = display_manager.fonts.get('radio_small', ImageFont.load_default())
        self.font_label = display_manager.fonts.get('radio_bitrate', ImageFont.load_default())

        # Start the display update thread
        self.update_thread = threading.Thread(target=self.update_display_loop, daemon=True)
        self.update_thread.start()
        self.logger.info("AirPlayScreen: Started background update thread.")

        # Subscribe to Volumio state changes
        if self.volumio_listener:
            self.volumio_listener.state_changed.connect(self.on_volumio_state_change)
        self.logger.info("AirPlayScreen initialised.")

        self.last_state = None

    # Respond only to active AirPlay state changes
    def on_volumio_state_change(self, sender, state):
        if not self.is_active:
            self.logger.debug("AirPlayScreen: ignoring state change; screen not active.")
            return

        if state.get("service", "").lower() not in ["airplay_emulation"]:
            self.logger.debug("AirPlayScreen: ignoring state change; service is not AirPlay.")
            return

        current_time = time.time()
        THRESHOLD = 3.0

        # Prevent frequent redraws for same track within short interval
        with self.state_lock:
            if self.last_state:
                same_track = (
                    state.get("title") == self.last_state.get("title") and
                    state.get("artist") == self.last_state.get("artist")
                )
                last_time = self.last_state.get("timestamp", 0)
                if same_track and (current_time - last_time < THRESHOLD):
                    self.logger.debug("AirPlayScreen: Ignoring repeated play event (same track within threshold).")
                    return
            state["timestamp"] = current_time
            self.last_state = state.copy()
            self.latest_state = state.copy()
        self.update_event.set()
    
    # Wait for display updates and render the screen accordingly GS Note that timeout= controls speed of scrolling
    def update_display_loop(self):
        while not self.stop_event.is_set():
            triggered = self.update_event.wait(timeout=0.1)
            with self.state_lock:
                if triggered and self.latest_state:
                    self.current_state = self.latest_state.copy()
                    self.latest_state = None
                    self.update_event.clear()
            if self.is_active and self.mode_manager.get_mode() == "airplay" and self.current_state:
                self.draw_display(self.current_state)
    
    # Enter AirPlay screen mode and refresh state
    def start_mode(self):
        if self.mode_manager.get_mode() != "airplay":
            self.logger.warning("AirPlayScreen: Mode is not 'airplay'; forcing start anyway.")
        self.is_active = True
        try:
            if self.volumio_listener and self.volumio_listener.socketIO:
                self.logger.debug("AirPlayScreen: Forcing getState from Volumio.")
                self.volumio_listener.socketIO.emit("getState", {})
        except Exception as e:
            self.logger.warning(f"AirPlayScreen: Failed to emit 'getState'. Error => {e}")
        if not self.update_thread.is_alive():
            self.stop_event.clear()
            self.update_thread = threading.Thread(target=self.update_display_loop, daemon=True)
            self.update_thread.start()
            self.logger.debug("AirPlayScreen: Display update thread restarted.")
    
    # Cleanly shut down the AirPlay screen
    def stop_mode(self):
        if not self.is_active:
            self.logger.debug("AirPlayScreen: stop_mode called but not active.")
            return

        self.is_active = False
        self.stop_event.set()
        self.update_event.set()

        if self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
            self.logger.debug("AirPlayScreen: Display update thread stopped.")

        self.display_manager.clear_screen()
        self.logger.info("AirPlayScreen: Stopped mode and cleared screen.")
    
    # GS Experimental Album Art loading script
    # Some symbols in artist and album titles may cause images not to load (, &)
    def get_albumart(self, url):
        if not url:
            default_path = self.display_manager.config.get("default_album_art")
            if default_path and os.path.exists(default_path):
                try:
                    return Image.open(default_path).convert("RGB")
                except Exception as e:
                    self.logger.error(f"Failed to load default album art from {default_path}: {e}")
                    return None
            return None

        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            web = query.get("web", [None])[0]
            if web:
                folders = web.split("/")
                artist = folders[0] if len(folders) > 0 else None
                album = folders[1] if len(folders) > 1 else None
                folder_parts = [artist] if artist else []
                if album:
                    folder_parts.append(album)
                folder_path = "/data/albumart/web/" + "/".join([
                    quote(f, safe="()%") for f in folder_parts if f
                ])
                if os.path.isdir(folder_path):
                    for fname in os.listdir(folder_path):
                        if fname.lower().endswith((".jpg", ".png", ".webp")):
                            img_path = os.path.join(folder_path, fname)
                            self.logger.debug(f"Loading album art from {img_path}")
                            return Image.open(img_path).convert("RGB")
                self.logger.warning(f"No image file found in {folder_path}") # GS Only uncomment this if debugging
        except Exception as e:
            self.logger.error(f"Error parsing or loading local album art: {e}")

        return None
        
    # GS Experimental Scroll text horizontally if wider than the screen
    def scroll_text_simple(self, draw, text, font, y, scroll_offset, screen_width, fill="white"):
        text_width, _ = draw.textsize(text, font=font)
        if text_width <= screen_width:
            draw.text((0, y), text, font=font, fill=fill)
            return 0, False
        x = screen_width - (scroll_offset % (text_width + screen_width))
        draw.text((x, y), text, font=font, fill=fill)
        return scroll_offset + 2, True
    
    # Main rendering logic for the AirPlay screen
    def draw_display(self, data):
        base_image = Image.new("RGB", self.display_manager.oled.size, "black")
        draw = ImageDraw.Draw(base_image)
        margin = 0
        screen_width, screen_height = self.display_manager.oled.size

        # Extract text info from playback state
        title = data.get("title", "AirPlay")
        artist = data.get("artist") or "No Info Available"
        service = data.get("service", "AirPlay").strip()
        quality = f"{data.get('bitdepth', 'N/A')}  {data.get('samplerate', 'N/A')}"

        # Define Y positions of each line
        title_y = margin - 5
        artist_y = margin + 13
        divider_y = margin + 33
        service_y = divider_y + 5
        quality_y = divider_y + 18

        # Scroll long title/artist text
        scrollable_width = screen_width - 75
        self.scroll_offset_title, _ = self.scroll_text_simple(
            draw, title, self.font_title, title_y, self.scroll_offset_title, scrollable_width
        )
        self.scroll_offset_artist, _ = self.scroll_text_simple(
            draw, artist, self.font_small, artist_y, self.scroll_offset_artist, scrollable_width
        )

        # Draw horizontal line and metadata text
        icon_width = 64
        gap = 11
        line_end_x = screen_width - margin - icon_width - gap
        draw.line((margin, divider_y, line_end_x, divider_y), fill="white")
        draw.text((margin, service_y), "AirPlay Mode", font=self.font_small, fill="white")
        draw.text((margin, quality_y), quality, font=self.font_label, fill="white")

        # Attempt to fetch and draw album art
        albumart_url = data.get("albumart")
        albumart_image = None
        if albumart_url and self.mode_manager.get_mode() == "airplay":
            albumart_image = self.get_albumart(albumart_url)
        icon_size = (64, 64)
        if albumart_image:
            albumart_image = albumart_image.resize(icon_size, Image.LANCZOS)
            art_x = screen_width - icon_size[0] - margin
            art_y = margin
            base_image.paste(albumart_image, (art_x, art_y))
        else:
            airplay_icon = self.display_manager.icons.get("airplay")
            if airplay_icon:
                airplay_icon = airplay_icon.resize(icon_size, Image.LANCZOS)
                art_x = screen_width - icon_size[0] - margin
                art_y = margin
                base_image.paste(airplay_icon, (art_x, art_y))

        # Mask left album art to hide text overflow
        box_width = 11
        box_height = 64
        box_x = art_x - box_width
        box_y = art_y
        draw.rectangle(
            [box_x, box_y, box_x + box_width - 1, box_y + box_height - 1],
            fill="black"
        )

        # Push final image to display
        self.display_manager.oled.display(base_image)
        self.logger.debug("AirPlayScreen: Display updated.")
    
    # Adjust system volume based on input delta
    def adjust_volume(self, volume_change):
        if not self.volumio_listener:
            self.logger.error("AirPlayScreen: No volumio_listener; cannot adjust volume.")
            return

        if self.latest_state is None:
            self.logger.debug("AirPlayScreen: latest_state is None; assuming volume=100.")
            self.latest_state = {"volume": 100}

        with self.state_lock:
            curr_vol = self.latest_state.get("volume", 100)
            new_vol = max(0, min(int(curr_vol) + volume_change, 100))

        self.logger.info(f"AirPlayScreen: Adjusting volume from {curr_vol} to {new_vol}.")
        try:
            if volume_change > 0:
                self.volumio_listener.socketIO.emit("volume", "+")
            elif volume_change < 0:
                self.volumio_listener.socketIO.emit("volume", "-")
            else:
                self.volumio_listener.socketIO.emit("volume", new_vol)
        except Exception as e:
            self.logger.error(f"AirPlayScreen: Error adjusting volume => {e}")
    
    # Toggle play/pause on Volumio
    def toggle_play_pause(self):
        
        self.logger.info("AirPlayScreen: Toggling play/pause.")
        if not self.volumio_listener or not self.volumio_listener.is_connected():
            self.logger.warning("AirPlayScreen: Not connected to Volumio; cannot toggle.")
            return
        try:
            self.volumio_listener.socketIO.emit("toggle", {})
            self.logger.debug("AirPlayScreen: Emitted 'toggle' event.")
        except Exception as e:
            self.logger.error(f"AirPlayScreen: Toggle play/pause failed => {e}")

    # Manual trigger to update display from current state
    def display_airplay_info(self):
        if not self.is_active:
            self.logger.info("AirPlayScreen: display_airplay_info called, but mode is not active.")
            return

        state = self.volumio_listener.get_current_state()
        if state:
            self.draw_display(state)
        else:
            self.logger.warning("AirPlayScreen: No current Volumio state available to display.")
