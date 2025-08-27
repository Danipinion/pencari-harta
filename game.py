import tkinter as tk
from tkinter import messagebox
import random
import time
import re


PAPAN_LEBAR, PAPAN_TINGGI = 10, 10
TILE_DINDING, TILE_JALUR = 0, 1
JARAK_MINIMAL_HARTA = 5
JARAK_MAKSIMAL_HARTA = 7

ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI = 'atas', 'kanan', 'bawah', 'kiri'
ARAH_LIST = [ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI]
PLAYER_ICONS = {
    ARAH_ATAS: '👆🏻',
    ARAH_KANAN: '👉🏻',
    ARAH_BAWAH: '👇🏻',
    ARAH_KIRI: '👈🏻',
}
TREASURE_CHAR = "💎"

PATH_COLOR = "#a0a0a0"
WALL_COLOR = "#34495e"
PLAYER_COLOR = "#4a90e2"
TREASURE_COLOR = "#f5a623"
WIN_COLOR = "#2ecc71"

root = tk.Tk()
root.title("Pencarian Harta Karun")
tile_labels = {}
entry_perintah = None
papan_permainan = []

posisi_pemain = (0, 0)
arah_pemain = ARAH_KANAN
posisi_harta_karun = (0, 0)

total_kemenangan = 0
total_percobaan = 0
percobaan_saat_ini = 0
label_statistik = None


def hitung_jarak_manhattan(pos1, pos2):
    """Menghitung jarak langkah (bukan garis lurus) antara dua titik."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def buat_jalur_random():
    """Membuat papan baru dengan jalur acak yang memenuhi syarat jarak."""
    max_percobaan = 100
    for _ in range(max_percobaan):
        papan = [[TILE_DINDING for _ in range(PAPAN_LEBAR)] for _ in range(PAPAN_TINGGI)]
        
        x, y = random.randint(0, PAPAN_LEBAR - 1), random.randint(0, PAPAN_TINGGI - 1)
        start_pos = (x, y)
        papan[y][x] = TILE_JALUR
        
        langkah_jalur = (PAPAN_LEBAR * PAPAN_TINGGI) * 2 // 3
        for _ in range(langkah_jalur):
            gerakan_valid = []
            if x > 0: gerakan_valid.append((-1, 0))
            if x < PAPAN_LEBAR - 1: gerakan_valid.append((1, 0))
            if y > 0: gerakan_valid.append((0, -1))
            if y < PAPAN_TINGGI - 1: gerakan_valid.append((0, 1))
            
            if not gerakan_valid: break
            
            dx, dy = random.choice(gerakan_valid)
            x, y = x + dx, y + dy
            papan[y][x] = TILE_JALUR
        
        end_pos = (x, y)
        
        total_jalur = sum(row.count(TILE_JALUR) for row in papan)
        jarak = hitung_jarak_manhattan(start_pos, end_pos)

        if total_jalur > 25 and start_pos != end_pos and JARAK_MINIMAL_HARTA <= jarak <= JARAK_MAKSIMAL_HARTA:
            print(f"Jalur dibuat dengan jarak {jarak} (syarat: {JARAK_MINIMAL_HARTA}-{JARAK_MAKSIMAL_HARTA})")
            return papan, start_pos, end_pos
    
    print(f"Gagal memenuhi syarat jarak setelah {max_percobaan} percobaan. Menggunakan hasil terakhir.")
    return papan, start_pos, end_pos


def on_closing():
    if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar?"):
        root.destroy()

def setup_ui():
    root.attributes('-topmost', True)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    game_frame = tk.Frame(root, bg='black', padx=10, pady=10)
    game_frame.pack()
    for y in range(PAPAN_TINGGI):
        for x in range(PAPAN_LEBAR):
            label = tk.Label(
                game_frame, text="", font=("Arial", 20), width=2, height=1,
                borderwidth=2, relief="groove"
            )
            label.grid(row=y, column=x, padx=1, pady=1)
            tile_labels[(x, y)] = label
    

    stats_frame = tk.Frame(root, pady=5)
    stats_frame.pack()
    global label_statistik
    label_statistik = tk.Label(stats_frame, text="", font=("Segoe UI", 11))
    label_statistik.pack()

    control_frame = tk.Frame(root, pady=10)
    control_frame.pack()
    global entry_perintah
    tk.Label(control_frame, text="Perintah:").pack(side=tk.LEFT)
    entry_perintah = tk.Entry(control_frame, width=50)
    entry_perintah.pack(side=tk.LEFT, padx=5)
    entry_perintah.bind("<Return>", lambda event: jalankan_perintah_dari_ui())
    btn_jalankan = tk.Button(control_frame, text="Jalankan", command=jalankan_perintah_dari_ui)
    btn_jalankan.pack(side=tk.LEFT)

def update_statistik_ui():
    """Memperbarui teks pada label statistik."""
    if label_statistik:
        teks = (f"🏆 Kemenangan: {total_kemenangan}  |  "
                f"🎮 Total Percobaan: {total_percobaan}  |  "
                f"🎯 Percobaan Babak Ini: {percobaan_saat_ini}")
        label_statistik.config(text=teks)

def update_ui():
    """Menggambar ulang papan permainan dengan skema warna yang diperbarui."""
    for y in range(PAPAN_TINGGI):
        for x in range(PAPAN_LEBAR):
            pos = (x, y)
            label = tile_labels[pos]
            
            bg_color = WALL_COLOR if papan_permainan[y][x] == TILE_DINDING else PATH_COLOR
            text_char = ""
            
            if pos == posisi_harta_karun:
                bg_color = TREASURE_COLOR
                text_char = TREASURE_CHAR
            
            if pos == posisi_pemain:
                bg_color = PLAYER_COLOR
                text_char = PLAYER_ICONS[arah_pemain]

            if pos == posisi_pemain and pos == posisi_harta_karun:
                bg_color = WIN_COLOR
                text_char = "🏆"
            
            label.config(bg=bg_color, text=text_char)
    root.update()


def reset_game():
    """Memulai babak baru dengan jalur dan posisi acak."""
    global papan_permainan, posisi_pemain, posisi_harta_karun, arah_pemain

    global percobaan_saat_ini
    percobaan_saat_ini = 0

    papan_permainan, posisi_pemain, posisi_harta_karun = buat_jalur_random()
    arah_pemain = random.choice(ARAH_LIST)
    
    print("\n--- JALUR BARU TELAH DIBUAT! ---")
    print(f"Posisi awal kamu: {posisi_pemain}, Menghadap: {arah_pemain}")
    print(f"Temukan harta karun di: {posisi_harta_karun}")
    
    update_ui()

    update_statistik_ui()


def putar(arah_putar, jumlah=1):
    """Memutar orientasi pemain sebanyak 'jumlah' kali."""
    global arah_pemain
    
    print(f"-> Perintah: {arah_putar}({jumlah})")
    for i in range(jumlah):
        current_index = ARAH_LIST.index(arah_pemain)
        if arah_putar == 'kanan':
            new_index = (current_index + 1) % 4
        elif arah_putar == 'kiri':
            new_index = (current_index - 1 + 4) % 4
        else:
            return
            
        arah_pemain = ARAH_LIST[new_index]
        print(f"   Berputar... Arah sekarang: {arah_pemain}")
        update_ui()
        time.sleep(0.3)

def maju(langkah=1):
    """Mengerakkan pemain maju sesuai arah hadapnya."""
    global posisi_pemain
    
    arah_map = {ARAH_ATAS: (0, -1), ARAH_KANAN: (1, 0), ARAH_BAWAH: (0, 1), ARAH_KIRI: (-1, 0)}
    dx, dy = arah_map[arah_pemain]
    
    for _ in range(langkah):
        current_x, current_y = posisi_pemain
        target_x, target_y = current_x + dx, current_y + dy
        
        if 0 <= target_x < PAPAN_LEBAR and 0 <= target_y < PAPAN_TINGGI:
            if papan_permainan[target_y][target_x] == TILE_JALUR:
                posisi_pemain = (target_x, target_y)
                print(f"-> Maju satu langkah ke {arah_pemain}. Posisi: {posisi_pemain}")
                update_ui()
                time.sleep(0.3)
                if posisi_pemain == posisi_harta_karun:
                    return
            else:
                print(f"BUMP! Tidak bisa maju, di depan ada dinding.")
                break
        else:
            print(f"BUMP! Tidak bisa maju, sudah di tepi papan.")
            break


def jalankan_perintah_dari_ui():
    """
    Mensimulasikan perintah dari UI.
    Jika harta ditemukan, permainan menang.
    Jika tidak, pemain kembali ke posisi awal sebelum simulasi.
    """
    global posisi_pemain, arah_pemain

    global total_kemenangan, total_percobaan, percobaan_saat_ini
    
    perintah_user = entry_perintah.get()
    if not perintah_user: return
    

    total_percobaan += 1
    percobaan_saat_ini += 1
    update_statistik_ui()

    print(f"\n== Memulai Simulasi ke-{percobaan_saat_ini} untuk: '{perintah_user}' ==")
    
    posisi_awal = posisi_pemain
    arah_awal = arah_pemain
    harta_ditemukan = False

    perintah_list = [p.strip() for p in perintah_user.lower().split(',')]
    
    for perintah in perintah_list:
        if not perintah: continue
        
        match = re.match(r"(\w+)\s*\(\s*(\d+)\s*\)", perintah)
        if match:
            nama, arg = match.groups()
            try:
                if nama == "maju":
                    maju(int(arg))
                elif nama in ["kiri", "kanan"]:
                    putar(nama, int(arg))
                else:
                    print(f"Perintah '{nama}' tidak bisa menggunakan angka.")
            except ValueError:
                print(f"GAGAL! Angka tidak valid di '{perintah}'")
        
        elif re.match(r"^\w+$", perintah):
            if perintah == "maju":
                maju(1)
            elif perintah in ["kiri", "kanan"]:
                putar(perintah, 1)
            else:
                print(f"Perintah '{perintah}' tidak dikenali.")
        else:
            print(f"Format '{perintah}' salah.")
            
        if posisi_pemain == posisi_harta_karun:
            harta_ditemukan = True
            break 

    entry_perintah.delete(0, tk.END)

    if harta_ditemukan:
    
        total_kemenangan += 1
        print("\n🎉 SELAMAT! Kamu berhasil mencapai harta karun! 🎉")
        messagebox.showinfo("Menang!", "Kamu berhasil menemukan harta karun!")
        reset_game()
    else:
        print("-> Simulasi selesai. Harta tidak ditemukan, kembali ke posisi awal.")
        posisi_pemain = posisi_awal
        arah_pemain = arah_awal
        update_ui()


if __name__ == "__main__":
    setup_ui()
    reset_game()
    
    print("\nSelamat datang! Gunakan input box untuk mengontrol pemain.")
    print("Perintah: maju, kiri, kanan.")
    print("Semua perintah bisa memakai angka, contoh: maju(2), kanan(2), kiri")
    
    root.mainloop()
