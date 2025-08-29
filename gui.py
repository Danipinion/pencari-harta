import tkinter
from tkinter import messagebox
import customtkinter
from config import *

class GameUI:
    """
    Mengelola semua elemen User Interface (UI) menggunakan customtkinter.
    """
    def __init__(self, root: customtkinter.CTk, controller):
        """
        Menginisialisasi UI.
        
        Args:
            root (customtkinter.CTk): Jendela utama aplikasi.
            controller: Referensi ke instance Application (controller) untuk callback.
        """
        self.root = root
        self.controller = controller
        self.tile_labels = {}
        
        self._setup_main_window()
        self._create_widgets()

    def _setup_main_window(self):
        """Mengatur properti jendela utama."""
        self.root.title("Pencarian Harta Karun")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0) 
        self.root.grid_columnconfigure(2, weight=1)

    def _create_widgets(self):
        """Membuat semua widget UI (papan, tombol, label)."""
        # Panel latar belakang di sisi
        left_panel = customtkinter.CTkFrame(self.root, corner_radius=0, fg_color="#1a1a1a")
        left_panel.grid(row=0, column=0, sticky="nsew")
        right_panel = customtkinter.CTkFrame(self.root, corner_radius=0, fg_color="#1a1a1a")
        right_panel.grid(row=0, column=2, sticky="nsew")

        main_container = customtkinter.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_container.grid(row=0, column=1, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Frame Permainan
        game_frame = customtkinter.CTkFrame(main_container, corner_radius=0, fg_color="transparent")
        game_frame.grid(row=0, column=0, padx=10, pady=10)

        for i in range(max(PAPAN_LEBAR, PAPAN_TINGGI)):
            game_frame.grid_rowconfigure(i, weight=1, uniform="group1")
            game_frame.grid_columnconfigure(i, weight=1, uniform="group1")

        for y in range(PAPAN_TINGGI):
            for x in range(PAPAN_LEBAR):
                label = customtkinter.CTkLabel(game_frame, text="", font=FONT_PAPAN, corner_radius=0)
                label.grid(row=y, column=x, padx=1, pady=1, sticky="nsew")
                self.tile_labels[(x, y)] = label
        
        
        bottom_panel = customtkinter.CTkFrame(self.root, corner_radius=0, border_width=2, border_color="#1F2A36")
        bottom_panel.grid(row=1, column=0, columnspan=3, sticky="ew")
        bottom_panel.grid_columnconfigure(0, weight=1)

        self.label_statistik = customtkinter.CTkLabel(bottom_panel, text="", font=FONT_STATS)
        self.label_statistik.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.entry_perintah = customtkinter.CTkEntry(bottom_panel, font=FONT_UI, height=40, placeholder_text="Ketik perintah di sini... (Contoh: maju(2), kiri)")
        self.entry_perintah.grid(row=1, column=0, padx=10, pady=(5,5), sticky="ew")
        self.entry_perintah.bind("<Return>", lambda event: self.controller.handle_run_command())

        button_frame = customtkinter.CTkFrame(bottom_panel, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=10, pady=(5,10)) 

        btn_jalankan = customtkinter.CTkButton(button_frame, text="Jalankan", font=FONT_UI, height=40, command=self.controller.handle_run_command)
        btn_jalankan.pack(side=tkinter.LEFT, padx=5)
        
        self.btn_hint = customtkinter.CTkButton(button_frame, text="Bantuan", font=FONT_UI, height=40, command=self.controller.handle_show_hint, fg_color="#D35400", hover_color="#E67E22")
        self.btn_hint.pack(side=tkinter.LEFT, padx=5)
        
        btn_panduan = customtkinter.CTkButton(button_frame, text="Panduan", font=FONT_UI, height=40, command=self.show_guide, fg_color="#7f8c8d", hover_color="#95a5a6")
        btn_panduan.pack(side=tkinter.LEFT, padx=5)

        btn_keluar = customtkinter.CTkButton(button_frame, text="Keluar", font=FONT_UI, height=40, command=self.controller.on_closing, fg_color="#c0392b", hover_color="#e74c3c")
        btn_keluar.pack(side=tkinter.LEFT, padx=0)

    def update_hint_button_state(self, game_state):
        """Mengaktifkan atau menonaktifkan tombol bantuan berdasarkan status permainan."""
        if game_state.hint_digunakan:
            self.btn_hint.configure(state=tkinter.DISABLED, fg_color="#566573")
        else:
            self.btn_hint.configure(state=tkinter.NORMAL, fg_color="#D35400", hover_color="#E67E22")

    def update_board(self, game_state):
        """
        Memperbarui tampilan papan permainan berdasarkan status permainan saat ini.
        
        Args:
            game_state (Game): Objek status permainan dari kelas Game.
        """
        for y in range(PAPAN_TINGGI):
            for x in range(PAPAN_LEBAR):
                pos = (x, y)
                label = self.tile_labels[pos]
                tile_type = game_state.papan_permainan[y][x]
                
                fg_color = COLOR_WALL
                if tile_type == TILE_JALUR: fg_color = COLOR_PATH
                elif tile_type == TILE_BOM: fg_color = COLOR_BOMB
                
                text_char = ""
                if tile_type == TILE_BOM: text_char = BOMB_CHAR
                if pos == game_state.posisi_harta_karun:
                    fg_color = COLOR_TREASURE
                    text_char = TREASURE_CHAR
                if pos == game_state.posisi_pemain:
                    fg_color = COLOR_PLAYER
                    text_char = PLAYER_ICONS[game_state.arah_pemain]
                if pos == game_state.posisi_pemain and pos == game_state.posisi_harta_karun:
                    fg_color = COLOR_WIN
                    text_char = "🏆"
                    
                label.configure(fg_color=fg_color, text=text_char)
        self.root.update_idletasks()
    
    def update_stats(self, game_state):
        """
        Memperbarui label statistik.
        
        Args:
            game_state (Game): Objek status permainan dari kelas Game.
        """
        teks = (f"🏆 Menang: {game_state.total_kemenangan} | "
                f"🎮 Total Coba: {game_state.total_percobaan} | "
                f"🎯 Coba Babak Ini: {game_state.percobaan_saat_ini} | "
            f"⚡ Sisa Langkah: {game_state.sisa_langkah:02d}")
        self.label_statistik.configure(text=teks)
        
    def get_command_text(self) -> str:
        """Mengambil teks dari kotak input perintah."""
        return self.entry_perintah.get()
    
    def clear_command_text(self):
        """Menghapus teks dari kotak input perintah."""
        self.entry_perintah.delete(0, tkinter.END)

    def show_guide(self):
        """Menampilkan popup panduan bermain."""
        self.controller.sound_manager.play('click')
        panduan_teks = f"""
        Selamat Datang di Pencarian Harta Karun!

        Tujuan:
        Capai harta karun ({TREASURE_CHAR}) sebelum kehabisan langkah.

        Perintah:
        - maju, kiri, kanan
        - Gunakan angka: maju(3), kanan(2)
        - Gabungkan perintah: maju(2), kiri, maju(4)
        """
        messagebox.showinfo("Panduan Bermain", panduan_teks)

    def show_hint_path(self, path: list, game_state):
        """
        Menyorot jalur bantuan (hint) di papan untuk sementara.
        """
        for pos in path:
            if pos != game_state.posisi_pemain and pos != game_state.posisi_harta_karun:
                self.tile_labels[pos].configure(fg_color=COLOR_HINT)
        
        def reset_color():
            for pos in path:
                if pos != game_state.posisi_pemain and pos != game_state.posisi_harta_karun:
                    y, x = pos[1], pos[0]
                    if game_state.papan_permainan[y][x] == TILE_JALUR:
                        self.tile_labels[pos].configure(fg_color=COLOR_PATH)
        self.root.after(2000, reset_color)

    def show_message(self, title: str, message: str, type: str = "info"):
        """
        Menampilkan popup pesan general.
        
        Args:
            title (str): Judul popup.
            message (str): Isi pesan.
            type (str): Jenis pesan ('info', 'warning', 'error').
        """
        if type == "info":
            messagebox.showinfo(title, message)
        elif type == "warning":
            messagebox.showwarning(title, message)
        elif type == "error":
            messagebox.showerror(title, message)
