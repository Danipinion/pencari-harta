import tkinter as tk
from tkinter import messagebox
import random
import time
import re
from collections import deque

PAPAN_LEBAR, PAPAN_TINGGI = 10, 10
TILE_DINDING, TILE_JALUR, TILE_BOM = 0, 1, 2
JARAK_MINIMAL_HARTA = 5
JARAK_MAKSIMAL_HARTA = 7
JUMLAH_BOM = 5

ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI = 'atas', 'kanan', 'bawah', 'kiri'
ARAH_LIST = [ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI]
PLAYER_ICONS = {
    ARAH_ATAS: '👆🏻',
    ARAH_KANAN: '👉🏻',
    ARAH_BAWAH: '👇🏻',
    ARAH_KIRI: '👈🏻',
}
TREASURE_CHAR = "💎"
BOMB_CHAR = "💣"

PATH_COLOR = "#a0a0a0"
WALL_COLOR = "#34495e"
PLAYER_COLOR = "#4a90e2"
TREASURE_COLOR = "#f5a623"
BOMB_COLOR = "#e74c3c"
WIN_COLOR = "#2ecc71"
HINT_COLOR = "#3498db"

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
sisa_langkah = 0
label_statistik = None

def hitung_jarak_manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def cari_jalur_terpendek_bfs(papan, start, end):
    lebar, tinggi = len(papan[0]), len(papan)
    antrian = deque([(start, [start])])
    dikunjungi = {start}

    while antrian:
        (x, y), jalur = antrian.popleft()

        if (x, y) == end:
            return jalur

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx < lebar and 0 <= ny < tinggi and (nx, ny) not in dikunjungi:
                if papan[ny][nx] == TILE_JALUR:
                    dikunjungi.add((nx, ny))
                    antrian.append(((nx, ny), jalur + [(nx, ny)]))
    return None

def buat_jalur_random():
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

        if total_jalur > 25 + JUMLAH_BOM and start_pos != end_pos and JARAK_MINIMAL_HARTA <= jarak <= JARAK_MAKSIMAL_HARTA:
            jalur_awal = cari_jalur_terpendek_bfs(papan, start_pos, end_pos)
            if not jalur_awal: continue

            posisi_jalur_valid = []
            for y_jalur in range(PAPAN_TINGGI):
                for x_jalur in range(PAPAN_LEBAR):
                    if papan[y_jalur][x_jalur] == TILE_JALUR:
                        if (x_jalur, y_jalur) != start_pos and (x_jalur, y_jalur) != end_pos:
                            posisi_jalur_valid.append((x_jalur, y_jalur))
            
            papan_final = [row[:] for row in papan]
            if len(posisi_jalur_valid) >= JUMLAH_BOM:
                posisi_bom = random.sample(posisi_jalur_valid, JUMLAH_BOM)
                for bx, by in posisi_bom:
                    papan_final[by][bx] = TILE_BOM
                
                if cari_jalur_terpendek_bfs(papan_final, start_pos, end_pos):
                    return papan_final, start_pos, end_pos

    papan, start, end = buat_jalur_random() 
    return papan, start, end

def on_closing():
    if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar?"):
        root.destroy()

def tampilkan_panduan():
    panduan_teks = """
    Selamat Datang di Pencarian Harta Karun!

    Tujuan:
    Capai harta karun (💎) sebelum kehabisan langkah.

    Perintah:
    - maju, kiri, kanan
    - Gunakan angka: maju(3), kanan(2)
    - Gabungkan perintah: maju(2), kiri, maju(4)

    Aturan:
    - Batas Langkah: Setiap gerakan (maju/putar) mengurangi sisa langkahmu. Jika habis, kamu kalah!
    - Tombol Bantuan: Menunjukkan jalur terpendek selama 2 detik. Gunakan dengan bijak!

    Rintangan:
    - Dinding (⬛) dan Bom (💣) tidak bisa dilewati.
    """
    messagebox.showinfo("Panduan Bermain", panduan_teks)

def tampilkan_hint():
    jalur_hint = cari_jalur_terpendek_bfs(papan_permainan, posisi_pemain, posisi_harta_karun)
    
    if jalur_hint:
        for pos in jalur_hint:
            if pos != posisi_pemain and pos != posisi_harta_karun:
                tile_labels[pos].config(bg=HINT_COLOR)
        
        def reset_warna_jalur():
            for pos in jalur_hint:
                 if pos != posisi_pemain and pos != posisi_harta_karun:
                    y, x = pos[1], pos[0]
                    if papan_permainan[y][x] == TILE_JALUR:
                        tile_labels[pos].config(bg=PATH_COLOR)

        root.after(2000, reset_warna_jalur)
    else:
        messagebox.showwarning("Buntu!", "Tidak ada jalur yang bisa ditemukan dari posisimu!")

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
    
    btn_hint = tk.Button(control_frame, text="Bantuan", command=tampilkan_hint, bg="#f1c40f")
    btn_hint.pack(side=tk.LEFT, padx=5)
    btn_panduan = tk.Button(control_frame, text="Panduan", command=tampilkan_panduan)
    btn_panduan.pack(side=tk.LEFT)

def update_statistik_ui():
    if label_statistik:
        teks = (f"🏆 Menang: {total_kemenangan} | "
                f"🎮 Total Coba: {total_percobaan} | "
                f"🎯 Coba Babak Ini: {percobaan_saat_ini} | "
                f"⚡ Sisa Langkah: {sisa_langkah}")
        label_statistik.config(text=teks)

def update_ui():
    for y in range(PAPAN_TINGGI):
        for x in range(PAPAN_LEBAR):
            pos = (x, y)
            label = tile_labels[pos]
            tile_type = papan_permainan[y][x]
            
            bg_color = WALL_COLOR
            if tile_type == TILE_JALUR:
                bg_color = PATH_COLOR
            elif tile_type == TILE_BOM:
                bg_color = BOMB_COLOR

            text_char = ""
            if tile_type == TILE_BOM:
                text_char = BOMB_CHAR
            
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
    global papan_permainan, posisi_pemain, posisi_harta_karun, arah_pemain
    global percobaan_saat_ini, sisa_langkah

    percobaan_saat_ini = 0
    papan_permainan, posisi_pemain, posisi_harta_karun = buat_jalur_random()
    arah_pemain = random.choice(ARAH_LIST)

    jalur_optimal = cari_jalur_terpendek_bfs(papan_permainan, posisi_pemain, posisi_harta_karun)
    if jalur_optimal:
        langkah_optimal = len(jalur_optimal) - 1
        sisa_langkah = int(langkah_optimal * 1.5) + 5
    else:
        sisa_langkah = 50
    
    update_ui()
    update_statistik_ui()

def putar(arah_putar, jumlah=1):
    global arah_pemain, sisa_langkah
    
    for i in range(jumlah):
        if sisa_langkah <= 0: return
        sisa_langkah -= 1
        
        current_index = ARAH_LIST.index(arah_pemain)
        if arah_putar == 'kanan': new_index = (current_index + 1) % 4
        else: new_index = (current_index - 1 + 4) % 4
        arah_pemain = ARAH_LIST[new_index]
        
        update_statistik_ui()
        update_ui()
        time.sleep(0.3)

def maju(langkah=1):
    global posisi_pemain, sisa_langkah
    
    arah_map = {ARAH_ATAS: (0, -1), ARAH_KANAN: (1, 0), ARAH_BAWAH: (0, 1), ARAH_KIRI: (-1, 0)}
    dx, dy = arah_map[arah_pemain]
    
    for _ in range(langkah):
        if sisa_langkah <= 0: return
        sisa_langkah -= 1
        update_statistik_ui()

        current_x, current_y = posisi_pemain
        target_x, target_y = current_x + dx, current_y + dy
        
        if 0 <= target_x < PAPAN_LEBAR and 0 <= target_y < PAPAN_TINGGI:
            tile_tujuan = papan_permainan[target_y][target_x]
            if tile_tujuan == TILE_JALUR:
                posisi_pemain = (target_x, target_y)
                update_ui()
                time.sleep(0.3)
                if posisi_pemain == posisi_harta_karun:
                    return
            else:
                break
        else:
            break

def jalankan_perintah_dari_ui():
    global posisi_pemain, arah_pemain, total_kemenangan, total_percobaan, percobaan_saat_ini, sisa_langkah
    
    perintah_user = entry_perintah.get()
    if not perintah_user: return
    
    total_percobaan += 1
    percobaan_saat_ini += 1
    
    posisi_awal_simulasi = posisi_pemain
    arah_awal_simulasi = arah_pemain
    langkah_awal_simulasi = sisa_langkah
    
    harta_ditemukan = False
    perintah_list = [p.strip() for p in perintah_user.lower().split(',')]
    
    for perintah in perintah_list:
        if not perintah or sisa_langkah <= 0: continue
        
        match = re.match(r"(\w+)\s*\(\s*(\d+)\s*\)", perintah)
        if match:
            nama, arg = match.groups()
            try:
                if nama == "maju": maju(int(arg))
                elif nama in ["kiri", "kanan"]: putar(nama, int(arg))
            except ValueError:
                pass
        
        elif re.match(r"^\w+$", perintah):
            if perintah == "maju": maju(1)
            elif perintah in ["kiri", "kanan"]: putar(perintah, 1)

        if posisi_pemain == posisi_harta_karun:
            harta_ditemukan = True
            break 
    
    entry_perintah.delete(0, tk.END)

    if harta_ditemukan:
        total_kemenangan += 1
        messagebox.showinfo("Menang!", "Kamu berhasil menemukan harta karun!")
        reset_game()
    elif sisa_langkah <= 0:
        messagebox.showerror("Kalah!", "Langkahmu sudah habis. Coba lagi di babak baru!")
        reset_game()
    else:
        posisi_pemain = posisi_awal_simulasi
        arah_pemain = arah_awal_simulasi
        sisa_langkah = langkah_awal_simulasi
        update_statistik_ui()
        update_ui()

if __name__ == "__main__":
    setup_ui()
    reset_game()
    tampilkan_panduan() 
    root.mainloop()
