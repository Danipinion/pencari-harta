import customtkinter
import re
import time
import copy
from tkinter import messagebox
from config import *
from game_logic import Game
from gui import GameUI
from sound_manager import SoundManager
from credits_popup import CreditsPopup


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
        
        self._show_credits_popup()

        self.reset_full_game()

    def _show_credits_popup(self):
        """Membuat dan menampilkan popup kredit, lalu menunggu hingga ditutup."""
        credits_window = CreditsPopup(self.root)
        self.root.wait_window(credits_window)

    def run(self):
        """Memulai loop utama aplikasi."""
        self.root.mainloop()

    def reset_full_game(self):
        """Mereset seluruh status permainan ke awal."""
        self.game.reset_round()
        self.refresh_ui()

    def refresh_ui(self):
        """Memperbarui semua komponen UI (papan, statistik dan tombol)."""
        self.ui.update_stats(self.game)
        self.ui.update_board(self.game)
        self.ui.update_hint_button_state(self.game)

    def on_closing(self):
        """Menangani event ketika jendela ditutup."""
        self.sound_manager.play("click")
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar?"):
            self.root.destroy()

    def handle_show_hint(self):
        """Menangani permintaan untuk menampilkan bantuan (hint)."""
        self.sound_manager.play("click")
        if not self.game.hint_digunakan:
            jalur_hint = self.game.cari_jalur_terpendek_bfs(self.game.posisi_pemain, self.game.posisi_harta_karun)
            if jalur_hint:
                self.ui.show_hint_path(jalur_hint, self.game)
                self.game.hint_digunakan = True
                self.ui.update_hint_button_state(self.game)
            else:
                self.ui.show_message("Buntu!", "Tidak ada jalur aman yang bisa ditemukan dari posisimu!", "warning")
        else:
            self.ui.show_message("Bantuan Terkunci", "Kamu sudah menggunakan bantuan untuk babak ini.", "warning")


    def handle_run_command(self):
        """
        Menangani dan mengeksekusi perintah yang dimasukkan oleh pengguna.
        """
        self.sound_manager.play("click")
        perintah_user = self.ui.get_command_text()
        if not perintah_user:
            return

        self.game.total_percobaan += 1
        self.game.percobaan_saat_ini += 1
        self.refresh_ui()

        posisi_awal = self.game.posisi_pemain
        arah_awal = self.game.arah_pemain
        langkah_awal = self.game.sisa_langkah

        sim_game_state = copy.deepcopy(self.game)

        hasil_eksekusi, pesan_gagal = self._execute_commands(
            perintah_user, sim_game_state
        )

        self.ui.clear_command_text()

        if hasil_eksekusi == "menang":
            self.sound_manager.play("win")
            self.game.total_kemenangan += 1
            self.ui.show_message("Menang!", "Kamu berhasil menemukan harta karun!")
            self.reset_full_game()
        elif hasil_eksekusi == "kalah_langkah":
            self.sound_manager.play("lose")
            self.ui.show_message(
                "Kalah!", "Langkahmu sudah habis. Coba lagi di babak baru!", "error"
            )
            self.reset_full_game()
        else:  # "lanjut" atau "gagal"
            self.game.posisi_pemain = posisi_awal
            self.game.arah_pemain = arah_awal
            self.game.sisa_langkah = langkah_awal
            self.refresh_ui()

            if hasil_eksekusi == "gagal":
                self.ui.show_message(
                    "Gagal", f"Simulasi dibatalkan: {pesan_gagal}", "warning"
                )

    def _execute_commands(self, commands_str: str, game_state: Game) -> tuple[str, str]:
        """
        Mengeksekusi serangkaian perintah dan mengembalikan status akhir.

        Args:
            commands_str (str): String perintah dari pengguna.
            game_state (Game): Objek game state untuk dimanipulasi.

        Returns:
            Tuple[str, str]: (status ['menang', 'kalah', 'lanjut'], pesan)
        """
        perintah_list = [p.strip() for p in commands_str.lower().split(",")]

        for perintah in perintah_list:
            if not perintah:
                continue

            if game_state.sisa_langkah <= 0:
                return "gagal", "Langkahmu habis saat simulasi."

            match = re.match(r"(\w+)\s*\(\s*(\d+)\s*\)", perintah)
            nama, arg = (None, 1)

            if match:
                nama, arg_str = match.groups()
                try:
                    arg = int(arg_str)
                except ValueError:
                    continue
            elif re.match(r"^\w+$", perintah):
                nama = perintah

            if nama in ["kiri", "kanan"]:
                for _ in range(arg):
                    if game_state.sisa_langkah <= 0:
                        break
                    self.sound_manager.play("move")
                    game_state.putar(nama)
                    self.ui.update_board(game_state)
                    self.ui.update_stats(game_state)
                    time.sleep(0.1)
            elif nama == "maju":
                for i in range(arg):
                    if game_state.sisa_langkah <= 0:
                        break

                    berhasil_maju = game_state.maju()

                    if berhasil_maju:
                        self.sound_manager.play("move")
                    else:
                        self.sound_manager.play("bump")

                    self.ui.update_board(game_state)
                    self.ui.update_stats(game_state)
                    time.sleep(0.1)

                    pos_y, pos_x = (
                        game_state.posisi_pemain[1],
                        game_state.posisi_pemain[0],
                    )
                    tile_sekarang = game_state.papan_permainan[pos_y][pos_x]

                    if tile_sekarang == TILE_BOM:
                        self.sound_manager.play("lose")
                        return "gagal", "Kamu menginjak bom!"

                    if game_state.posisi_pemain == game_state.posisi_harta_karun:
                        return "menang", "Harta karun ditemukan!"

                    if not berhasil_maju:
                        return "lanjut", "Menabrak dinding!"

        if game_state.sisa_langkah <= 0:
            return "kalah_langkah", "Langkahmu sudah habis."

        return "lanjut", "Perintah selesai dieksekusi."


if __name__ == "__main__":
    customtkinter.set_appearance_mode(APPEARANCE_MODE)
    customtkinter.set_default_color_theme(DEFAULT_COLOR_THEME)

    root = customtkinter.CTk()
    app = Application(root)
    app.run()
