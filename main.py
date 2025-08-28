# main.py

import customtkinter
import re
import time
import copy
from tkinter import messagebox
from config import *
from game_logic import Game
from gui import GameUI
from sound_manager import SoundManager

class Application:
    """
    Kelas utama aplikasi yang bertindak sebagai controller.
    Menghubungkan logika permainan (Game), antarmuka (GameUI), dan suara (SoundManager).
    """
    def __init__(self, root: customtkinter.CTk):
        """
        Menginisialisasi aplikasi.
        
        Args:
            root (customtkinter.CTk): Jendela utama aplikasi.
        """
        self.root = root
        self.game = Game()
        self.sound_manager = SoundManager()
        self.ui = GameUI(self.root, self)
        
        self.reset_full_game()

    def run(self):
        """Memulai loop utama aplikasi."""
        self.root.mainloop()

    def reset_full_game(self):
        """Mereset seluruh status permainan ke awal."""
        self.game.reset_round()
        self.refresh_ui()

    def refresh_ui(self):
        """Memperbarui semua komponen UI (papan dan statistik)."""
        self.ui.update_stats(self.game)
        self.ui.update_board(self.game)

    def on_closing(self):
        """Menangani event ketika jendela ditutup."""
        self.sound_manager.play('click')
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar?"):
            self.root.destroy()

    def handle_show_hint(self):
        """Menangani permintaan untuk menampilkan bantuan (hint)."""
        self.sound_manager.play('click')
        jalur_hint = self.game.cari_jalur_terpendek_bfs(self.game.posisi_pemain, self.game.posisi_harta_karun)
        if jalur_hint:
            self.ui.show_hint_path(jalur_hint, self.game)
        else:
            self.ui.show_message("Buntu!", "Tidak ada jalur yang bisa ditemukan dari posisimu!", "warning")

    def handle_run_command(self):
        """
        Menangani dan mengeksekusi perintah yang dimasukkan oleh pengguna.
        """
        self.sound_manager.play('click')
        perintah_user = self.ui.get_command_text()
        if not perintah_user:
            return

        self.game.total_percobaan += 1
        self.game.percobaan_saat_ini += 1
        self.refresh_ui()

        # Simpan state sebelum simulasi
        posisi_awal = self.game.posisi_pemain
        arah_awal = self.game.arah_pemain
        langkah_awal = self.game.sisa_langkah

        # Buat 'dummy' game state untuk simulasi
        sim_game_state = copy.deepcopy(self.game)
        
        harta_ditemukan = self._execute_commands(perintah_user, sim_game_state)
        
        self.ui.clear_command_text()
        
        if harta_ditemukan:
            self.sound_manager.play('win')
            self.game.total_kemenangan += 1
            self.ui.show_message("Menang!", "Kamu berhasil menemukan harta karun!")
            self.reset_full_game()
        elif sim_game_state.sisa_langkah <= 0:
            self.sound_manager.play('lose')
            self.ui.show_message("Kalah!", "Langkahmu sudah habis. Coba lagi di babak baru!", "error")
            self.reset_full_game()
        else:
            # Jika tidak menang/kalah, kembalikan state ke sebelum simulasi
            self.game.posisi_pemain = posisi_awal
            self.game.arah_pemain = arah_awal
            self.game.sisa_langkah = langkah_awal
            self.refresh_ui()

    def _execute_commands(self, commands_str: str, game_state: Game) -> bool:
        """
        Mengeksekusi serangkaian perintah pada game state yang diberikan.
        
        Args:
            commands_str (str): String perintah dari pengguna.
            game_state (Game): Objek game state untuk dimanipulasi.
        
        Returns:
            bool: True jika harta karun ditemukan, False jika tidak.
        """
        perintah_list = [p.strip() for p in commands_str.lower().split(',')]
        
        for perintah in perintah_list:
            if not perintah or game_state.sisa_langkah <= 0: continue
            
            match = re.match(r"(\w+)\s*\(\s*(\d+)\s*\)", perintah)
            nama, arg = (None, 1)

            if match:
                nama, arg_str = match.groups()
                try: arg = int(arg_str)
                except ValueError: continue
            elif re.match(r"^\w+$", perintah):
                nama = perintah
            
            if nama in ["kiri", "kanan"]:
                for _ in range(arg):
                    if game_state.sisa_langkah <= 0: break
                    self.sound_manager.play('move')
                    game_state.putar(nama)
                    self.ui.update_board(game_state)
                    self.ui.update_stats(game_state)
                    time.sleep(0.15)
            elif nama == "maju":
                for _ in range(arg):
                    if game_state.sisa_langkah <= 0: break
                    berhasil_maju = game_state.maju()
                    if berhasil_maju:
                        self.sound_manager.play('move')
                    else:
                        self.sound_manager.play('bump')

                    self.ui.update_board(game_state)
                    self.ui.update_stats(game_state)
                    time.sleep(0.15)
                    
                    if game_state.posisi_pemain == game_state.posisi_harta_karun:
                        return True
                    if not berhasil_maju:
                        break # Berhenti jika menabrak
            
        return game_state.posisi_pemain == game_state.posisi_harta_karun

if __name__ == "__main__":
    customtkinter.set_appearance_mode(APPEARANCE_MODE)
    customtkinter.set_default_color_theme(DEFAULT_COLOR_THEME)
    
    root = customtkinter.CTk()
    app = Application(root)
    app.run()
