import os
import tkinter as tk
from tkinter import filedialog, ttk
import vlc
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from PIL import Image, ImageTk
import io

# Created by Eymen ERDOĞDU
# GitHub: github.com/eymenerdogdu

class AdvancedMP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Player - Created by Eymen ERDOĞDU")
        self.root.geometry("520x860")
        
        # Tema Paletleri Tanımları
        self.themes = {
            "Wine Ember": {
                "bg": "#2A1215",
                "panel": "#3D1A21",
                "panel_hover": "#4F232D",
                "selected": "#5C1D16",
                "accent": "#D35400",
                "text": "#F5EEF0",
                "muted": "#B8979B",
                "default_art_bg": (45, 20, 25),
                "use_custom_buttons": False
            },
            "Legacy": {
                "bg": "#2c3e50",
                "panel": "#34495e",
                "panel_hover": "#3e5771",
                "selected": "#1abc9c",
                "accent": "#2ecc71",
                "text": "#ffffff",
                "muted": "#bdc3c7",
                "default_art_bg": (50, 50, 50),
                "use_custom_buttons": True,
                "btn_folder": "#3498db",
                "btn_nav": "#9b59b6",
                "btn_play": "#2ecc71",
                "btn_stop": "#e74c3c",
                "btn_loop": "#1abc9c",
                "btn_seek": "#f39c12"
            },
            "Dark (Siyah)": {
                "bg": "#121212",
                "panel": "#1e1e1e",
                "panel_hover": "#2d2d2d",
                "selected": "#333333",
                "accent": "#1db954",
                "text": "#ffffff",
                "muted": "#a0a0a0",
                "default_art_bg": (30, 30, 30),
                "use_custom_buttons": False
            },
            "Light (Açık)": {
                "bg": "#f0f2f5",
                "panel": "#ffffff",
                "panel_hover": "#e4e6eb",
                "selected": "#d8dadf",
                "accent": "#0066cc",
                "text": "#050505",
                "muted": "#65676b",
                "default_art_bg": (220, 220, 220),
                "use_custom_buttons": False
            }
        }
        
        self.current_theme_name = "Wine Ember"
        self.apply_theme_colors(self.current_theme_name)
        
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        
        self.song_list = []          
        self.song_metadata = []      
        self.current_index = 0
        self.folder_path = ""
        self.is_playing = False
        self.is_looping = False      
        self.updating_slider = False
        
        self.view_mode = "Normal"
        self.view_configs = {
            "Büyük": {"art": 64, "title_font": ("Arial", 11, "bold"), "sub_font": ("Arial", 9)},
            "Normal": {"art": 48, "title_font": ("Arial", 10, "bold"), "sub_font": ("Arial", 8)},
            "Küçük": {"art": 36, "title_font": ("Arial", 9, "bold"), "sub_font": ("Arial", 7)},
            "Kompakt": {"art": 20, "title_font": ("Arial", 9), "sub_font": ("Arial", 7)}
        }
        
        self.setup_styles()
        self.create_menu()           
        self.create_widgets()
        self.check_playback_status()

    def apply_theme_colors(self, theme_name):
        t = self.themes[theme_name]
        self.COLOR_BG = t["bg"]
        self.COLOR_PANEL = t["panel"]
        self.COLOR_PANEL_HOVER = t["panel_hover"]
        self.COLOR_SELECTED = t["selected"]
        self.COLOR_ACCENT = t["accent"]
        self.COLOR_TEXT = t["text"]
        self.COLOR_MUTED = t["muted"]
        self.DEFAULT_ART_RGB = t["default_art_bg"]
        self.use_custom_buttons = t["use_custom_buttons"]
        
        if self.use_custom_buttons:
            self.c_folder = t["btn_folder"]
            self.c_nav = t["btn_nav"]
            self.c_play = t["btn_play"]
            self.c_stop = t["btn_stop"]
            self.c_loop = t["btn_loop"]
            self.c_seek = t["btn_seek"]

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScale", background=self.COLOR_BG, troughcolor=self.COLOR_PANEL, 
                          sliderrelief="flat", bordercolor=self.COLOR_BG)

    def create_menu(self):
        if hasattr(self, 'menubar') and self.menubar:
            self.root.config(menu="")

        self.menubar = tk.Menu(self.root, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT, activeforeground=self.COLOR_TEXT, bd=0)
        
        file_menu = tk.Menu(self.menubar, tearoff=0, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT, activeforeground=self.COLOR_TEXT)
        file_menu.add_command(label="Klasör Aç...", command=self.open_folder, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="File", menu=file_menu)

        playback_menu = tk.Menu(self.menubar, tearoff=0, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT, activeforeground=self.COLOR_TEXT)
        playback_menu.add_command(label="Oynat / Duraklat", command=self.toggle_play, accelerator="Space")
        playback_menu.add_command(label="Durdur", command=self.stop_music, accelerator="Ctrl+S")
        playback_menu.add_separator()
        playback_menu.add_command(label="Sonraki Şarkı", command=self.next_song, accelerator="Ctrl+Right")
        playback_menu.add_command(label="Önceki Şarkı", command=self.prev_song, accelerator="Ctrl+Left")
        playback_menu.add_separator()
        playback_menu.add_command(label="+10s İleri Sar", command=lambda: self.seek_relative(10), accelerator="Right")
        playback_menu.add_command(label="-10s Geri Sar", command=lambda: self.seek_relative(-10), accelerator="Left")
        playback_menu.add_command(label="+20s İleri Sar", command=lambda: self.seek_relative(20), accelerator="Shift+Right")
        playback_menu.add_command(label="-20s Geri Sar", command=lambda: self.seek_relative(-20), accelerator="Shift+Left")
        playback_menu.add_separator()
        playback_menu.add_command(label="Tekrarla (Loop) Aç/Kapat", command=self.toggle_loop, accelerator="Ctrl+R")
        self.menubar.add_cascade(label="Playback", menu=playback_menu)

        view_menu = tk.Menu(self.menubar, tearoff=0, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT, activeforeground=self.COLOR_TEXT)
        
        theme_submenu = tk.Menu(view_menu, tearoff=0, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT, activeforeground=self.COLOR_TEXT)
        self.theme_var = tk.StringVar(value=self.current_theme_name)
        for theme_name in self.themes.keys():
            theme_submenu.add_radiobutton(label=theme_name, variable=self.theme_var, value=theme_name, command=lambda tn=theme_name: self.change_theme(tn))
        view_menu.add_cascade(label="Theme", menu=theme_submenu)

        view_menu.add_separator()

        size_submenu = tk.Menu(view_menu, tearoff=0, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT, activeforeground=self.COLOR_TEXT)
        self.view_var = tk.StringVar(value=self.view_mode)
        for mode in self.view_configs.keys():
            size_submenu.add_radiobutton(label=mode, variable=self.view_var, value=mode, command=lambda m=mode: self.change_view_mode(m))
        view_menu.add_cascade(label="Playlist Size", menu=size_submenu)

        self.menubar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=self.menubar)

        self.root.bind("<Control-o>", lambda e: self.open_folder())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<space>", lambda e: self.toggle_play())
        self.root.bind("<Control-s>", lambda e: self.stop_music())
        self.root.bind("<Control-Right>", lambda e: self.next_song())
        self.root.bind("<Control-Left>", lambda e: self.prev_song())
        self.root.bind("<Right>", lambda e: self.seek_relative(10))
        self.root.bind("<Left>", lambda e: self.seek_relative(-10))
        self.root.bind("<Shift-Right>", lambda e: self.seek_relative(20))
        self.root.bind("<Shift-Left>", lambda e: self.seek_relative(-20))
        self.root.bind("<Control-r>", lambda e: self.toggle_loop())

    def create_widgets(self):
        self.root.configure(bg=self.COLOR_BG)

        for w in [getattr(self, attr, None) for attr in ['art_outer_frame', 'info_frame', 'slider_outer_frame', 'playlist_outer_frame', 'btn_outer_frame', 'seek_outer_frame', 'signature_label']]:
            if w:
                w.destroy()

        # 1. ÜST KISIM: Albüm Kapağı
        self.art_outer_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        self.art_outer_frame.pack(pady=10)

        self.art_label = tk.Label(self.art_outer_frame, bg=self.COLOR_PANEL, width=180, height=180, relief="flat")
        self.art_label.pack()
        self.create_default_art()

        # 2. ŞARKI BİLGİLERİ
        self.info_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        self.info_frame.pack(pady=5, padx=20, fill="x")

        self.lbl_title = tk.Label(self.info_frame, text="Seçilen Şarkı Yok", font=("Arial", 11, "bold"), fg=self.COLOR_TEXT, bg=self.COLOR_BG, justify="center", wraplength=440)
        self.lbl_title.pack(anchor="center", pady=(0, 2))

        self.lbl_artist_album = tk.Label(self.info_frame, text="Sanatçı --- • Albüm ---", font=("Arial", 9), fg=self.COLOR_MUTED, bg=self.COLOR_BG, justify="center")
        self.lbl_artist_album.pack(anchor="center")

        # 3. SEEKBAR VE ZAMAN GÖSTERGESİ
        self.slider_outer_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        self.slider_outer_frame.pack(pady=5, padx=25, fill="x")

        self.time_slider = ttk.Scale(self.slider_outer_frame, from_=0, to=100, orient="horizontal", command=self.on_seek)
        self.time_slider.pack(fill="x", expand=True)

        time_lbl_frame = tk.Frame(self.slider_outer_frame, bg=self.COLOR_BG)
        time_lbl_frame.pack(fill="x", pady=2)
        
        self.lbl_current_time = tk.Label(time_lbl_frame, text="0:00", font=("Arial", 9), fg=self.COLOR_MUTED, bg=self.COLOR_BG)
        self.lbl_current_time.pack(side="left")
        
        self.lbl_total_time = tk.Label(time_lbl_frame, text="0:00", font=("Arial", 9), fg=self.COLOR_MUTED, bg=self.COLOR_BG)
        self.lbl_total_time.pack(side="right")

        # 4. OYNATMA LİSTESİ (DIV / SCROLLABLE FRAME)
        self.playlist_outer_frame = tk.Frame(self.root, bg=self.COLOR_PANEL)
        self.playlist_outer_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.canvas = tk.Canvas(self.playlist_outer_frame, bg=self.COLOR_PANEL, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.playlist_outer_frame, orient="vertical", command=self.canvas.yview)
        
        self.playlist_inner_frame = tk.Frame(self.canvas, bg=self.COLOR_PANEL)
        
        self.playlist_inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.playlist_inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 5. ANA KONTROL BUTONLARI
        self.btn_outer_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        self.btn_outer_frame.pack(pady=8)

        if self.use_custom_buttons:
            bg_folder = self.c_folder
            bg_prev = self.c_nav
            bg_play = self.c_play
            bg_next = self.c_nav
            bg_stop = self.c_stop
            bg_loop = self.c_loop if self.is_looping else self.c_nav
            relief_type = "ridge"
        else:
            bg_folder = self.COLOR_PANEL
            bg_prev = self.COLOR_PANEL
            bg_play = self.COLOR_ACCENT
            bg_next = self.COLOR_PANEL
            bg_stop = self.COLOR_PANEL
            bg_loop = self.COLOR_ACCENT if self.is_looping else self.COLOR_PANEL
            relief_type = "flat"

        btn_style = {"font": ("Arial", 12, "bold"), "fg": "white", "relief": relief_type, "bd": 2 if self.use_custom_buttons else 0, "width": 4, "pady": 4}

        tk.Button(self.btn_outer_frame, text="📂", command=self.open_folder, bg=bg_folder, **btn_style).grid(row=0, column=0, padx=4)
        tk.Button(self.btn_outer_frame, text="⏮", command=self.prev_song, bg=bg_prev, **btn_style).grid(row=0, column=1, padx=4)

        play_symbol = "⏸️" if self.is_playing else "▶️"
        self.btn_play = tk.Button(self.btn_outer_frame, text=play_symbol, command=self.toggle_play, bg=bg_play, **btn_style)
        self.btn_play.grid(row=0, column=2, padx=4)

        tk.Button(self.btn_outer_frame, text="⏭", command=self.next_song, bg=bg_next, **btn_style).grid(row=0, column=3, padx=4)
        tk.Button(self.btn_outer_frame, text="⏹", command=self.stop_music, bg=bg_stop, **btn_style).grid(row=0, column=4, padx=4)

        self.btn_loop = tk.Button(self.btn_outer_frame, text="🔁", command=self.toggle_loop, bg=bg_loop, **btn_style)
        self.btn_loop.grid(row=0, column=5, padx=4)

        # 6. İLERİ / GERİ SARMA BUTONLARI
        self.seek_outer_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        self.seek_outer_frame.pack(pady=5)
        
        seek_bg = self.c_seek if self.use_custom_buttons else self.COLOR_PANEL
        seek_btn_style = {"font": ("Arial", 9, "bold"), "bg": seek_bg, "fg": "white",
                          "relief": relief_type, "bd": 2 if self.use_custom_buttons else 0, "width": 8, "pady": 3}

        tk.Button(self.seek_outer_frame, text="⏪ -20s", command=lambda: self.seek_relative(-20), **seek_btn_style).grid(row=0, column=0, padx=4)
        tk.Button(self.seek_outer_frame, text="⏪ -10s", command=lambda: self.seek_relative(-10), **seek_btn_style).grid(row=0, column=1, padx=4)
        tk.Button(self.seek_outer_frame, text="+10s ⏩", command=lambda: self.seek_relative(10), **seek_btn_style).grid(row=0, column=2, padx=4)
        tk.Button(self.seek_outer_frame, text="+20s ⏩", command=lambda: self.seek_relative(20), **seek_btn_style).grid(row=0, column=3, padx=4)

        # 7. İMZA SATIRI
        self.signature_label = tk.Label(
            self.root, 
            text="Created by Eymen ERDOĞDU\nGitHub: github.com/eymenerdogdu", 
            font=("Arial", 8), 
            fg=self.COLOR_MUTED, 
            bg=self.COLOR_BG,
            justify="center"
        )
        self.signature_label.pack(pady=(2, 8))

        if self.song_list:
            self.rebuild_playlist_ui()

    def update_control_buttons_state(self):
        """Tüm arayüzü silip baştan kurmadan sadece butonların görünümünü/rengini günceller."""
        play_symbol = "⏸️" if self.is_playing else "▶️"
        self.btn_play.config(text=play_symbol)
        
        if self.use_custom_buttons:
            bg_loop = self.c_loop if self.is_looping else self.c_nav
        else:
            bg_loop = self.COLOR_ACCENT if self.is_looping else self.COLOR_PANEL
        self.btn_loop.config(bg=bg_loop)

    def create_default_art(self):
        img = Image.new("RGB", (180, 180), self.DEFAULT_ART_RGB)
        self.default_photo = ImageTk.PhotoImage(img)
        self.art_label.config(image=self.default_photo)
        self.art_label.image = self.default_photo

    def change_theme(self, theme_name):
        self.current_theme_name = theme_name
        self.apply_theme_colors(theme_name)
        self.create_menu()
        self.create_widgets()
        if self.song_list:
            self.load_song(self.current_index, start_playing=False)

    def change_view_mode(self, mode):
        self.view_mode = mode
        if self.song_list:
            self.rebuild_playlist_ui()

    def rebuild_playlist_ui(self):
        for widget in self.playlist_inner_frame.winfo_children():
            widget.destroy()

        self.song_widgets = []
        cfg = self.view_configs[self.view_mode]

        for index, (path, (title, artist, album, duration, art_data)) in enumerate(zip(self.song_list, self.song_metadata)):
            is_current = (index == self.current_index)
            card_bg = self.COLOR_SELECTED if is_current else self.COLOR_PANEL
            
            card = tk.Frame(self.playlist_inner_frame, bg=card_bg, padx=6, pady=4)
            card.pack(fill="x", expand=True, pady=1)

            art_size = cfg["art"]
            img_label = tk.Label(card, bg=card_bg)
            img_label.pack(side="left", padx=(0, 8))

            if art_data:
                try:
                    img = Image.open(io.BytesIO(art_data)).resize((art_size, art_size), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img_label.config(image=photo)
                    img_label.image = photo
                except Exception:
                    img_label.config(image=self.get_default_thumb(art_size))
            else:
                img_label.config(image=self.get_default_thumb(art_size))

            text_frame = tk.Frame(card, bg=card_bg)
            text_frame.pack(side="left", fill="both", expand=True)

            lbl_t = tk.Label(text_frame, text=title, font=cfg["title_font"], fg=self.COLOR_TEXT, bg=card_bg, anchor="w", justify="left")
            lbl_t.pack(anchor="w", fill="x")

            lbl_sub = tk.Label(text_frame, text=f"{artist}  •  {album}", font=cfg["sub_font"], fg=self.COLOR_MUTED, bg=card_bg, anchor="w", justify="left")
            lbl_sub.pack(anchor="w", fill="x")

            idx = index
            for w in [card, img_label, text_frame, lbl_t, lbl_sub]:
                w.bind("<Button-1>", lambda e, i=idx: self.load_song(i, start_playing=True))
                w.bind("<Enter>", lambda e, c=card, cur=is_current: c.config(bg=self.COLOR_SELECTED if cur else self.COLOR_PANEL_HOVER))
                w.bind("<Leave>", lambda e, c=card, cur=is_current: c.config(bg=self.COLOR_SELECTED if cur else self.COLOR_PANEL))

            self.song_widgets.append((card, img_label, text_frame, lbl_t, lbl_sub))

    def get_default_thumb(self, size):
        img = Image.new("RGB", (size, size), self.DEFAULT_ART_RGB)
        return ImageTk.PhotoImage(img)

    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            return

        self.song_list.clear()
        self.song_metadata.clear()

        files = sorted([f for f in os.listdir(self.folder_path) if f.lower().endswith(".mp3")])
        
        for file in files:
            path = os.path.join(self.folder_path, file)
            self.song_list.append(path)
            title, artist, album, duration, art = self.extract_metadata(path)
            self.song_metadata.append((title, artist, album, duration, art))

        if self.song_list:
            self.current_index = 0
            self.rebuild_playlist_ui()
            self.load_song(0, start_playing=True)

    def extract_metadata(self, path):
        title = os.path.basename(path)[:-4]
        artist = "Bilinmeyen Sanatçı"
        album = "Bilinmeyen Albüm"
        duration = 0
        art_image = None

        try:
            audio = MP3(path, ID3=ID3)
            if audio.info:
                duration = int(audio.info.length)
            
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, TIT2) and tag.text:
                        title = str(tag.text[0])
                    elif isinstance(tag, TPE1) and tag.text:
                        artist = str(tag.text[0])
                    elif isinstance(tag, TALB) and tag.text:
                        album = str(tag.text[0])
                    elif isinstance(tag, APIC):
                        art_image = tag.data
        except Exception:
            pass

        return title, artist, album, duration, art_image

    def load_song(self, index, start_playing=True):
        if not self.song_list:
            return

        self.current_index = index
        path = self.song_list[index]
        title, artist, album, duration, art_data = self.song_metadata[index]

        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        
        self.lbl_title.config(text=title)
        self.lbl_artist_album.config(text=f"Sanatçı: {artist}  •  Albüm: {album}")
        
        self.time_slider.config(to=duration if duration > 0 else 100)
        self.lbl_total_time.config(text=self.format_time(duration))

        if art_data:
            try:
                img = Image.open(io.BytesIO(art_data)).resize((180, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.art_label.config(image=photo)
                self.art_label.image = photo
            except Exception:
                self.create_default_art()
        else:
            self.create_default_art()

        if hasattr(self, 'song_widgets') and self.song_widgets:
            self.rebuild_playlist_ui()

        if start_playing:
            self.player.play()
            self.is_playing = True
            self.update_control_buttons_state()

    def toggle_play(self):
        if not self.song_list:
            return
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
        else:
            self.player.play()
            self.is_playing = True
        self.update_control_buttons_state()

    def stop_music(self):
        self.player.stop()
        self.is_playing = False
        self.lbl_title.config(text="Seçilen Şarkı Yok")
        self.lbl_artist_album.config(text="Sanatçı --- • Albüm ---")
        self.lbl_current_time.config(text="0:00")
        self.time_slider.config(value=0)
        self.create_default_art()
        if hasattr(self, 'song_widgets') and self.song_widgets:
            self.rebuild_playlist_ui()
        self.update_control_buttons_state()

    def next_song(self):
        if not self.song_list:
            return
        self.current_index = (self.current_index + 1) % len(self.song_list)
        self.load_song(self.current_index, start_playing=True)

    def prev_song(self):
        if not self.song_list:
            return
        self.current_index = (self.current_index - 1) % len(self.song_list)
        self.load_song(self.current_index, start_playing=True)

    def toggle_loop(self):
        self.is_looping = not self.is_looping
        self.update_control_buttons_state()

    def seek_relative(self, seconds):
        if not self.song_list:
            return
        current_ms = self.player.get_time()
        total_ms = self.player.get_length()
        target_ms = max(0, min(total_ms, current_ms + (seconds * 1000)))
        self.player.set_time(target_ms)

    def on_seek(self, val):
        if self.updating_slider:
            return
        if self.player.get_length() > 0:
            target_ms = float(val) * 1000
            self.player.set_time(int(target_ms))

    def format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m}:{s:02}"

    def check_playback_status(self):
        if self.is_playing and self.player.get_length() > 0:
            current_ms = self.player.get_time()
            
            self.updating_slider = True
            self.time_slider.config(value=current_ms / 1000.0)
            self.lbl_current_time.config(text=self.format_time(int(current_ms / 1000)))
            self.updating_slider = False

            state = self.player.get_state()
            if state == vlc.State.Ended:
                if self.is_looping:
                    self.player.set_time(0)
                    self.player.play()
                else:
                    self.next_song()

        self.root.after(500, self.check_playback_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedMP3Player(root)
    root.mainloop()
