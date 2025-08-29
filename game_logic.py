import random
import time
from collections import deque
from config import (PAPAN_LEBAR, PAPAN_TINGGI, TILE_DINDING, TILE_JALUR, TILE_BOM, 
                    JARAK_MINIMAL_HARTA, JARAK_MAKSIMAL_HARTA, JUMLAH_BOM, ARAH_LIST,
                    ARAH_ATAS, ARAH_KANAN, ARAH_BAWAH, ARAH_KIRI)

class Game:
    """
    Mengelola semua logika dan status permainan Pencarian Harta Karun.
    """
    def __init__(self):
        """
        Menginisialisasi status awal permainan.
        """
        self.papan_permainan = []
        self.posisi_pemain = (0, 0)
        self.arah_pemain = ARAH_KANAN
        self.posisi_harta_karun = (0, 0)
        self.sisa_langkah = 0
        self.total_kemenangan = 0
        self.total_percobaan = 0
        self.percobaan_saat_ini = 0
        self.hint_digunakan = False

    def _hitung_aksi_di_jalur(self, jalur: list, arah_awal: str) -> int:
        """
        Menghitung total aksi (maju dan putar) yang dibutuhkan untuk melewati sebuah jalur.
        Setiap gerakan maju dan setiap putaran dihitung sebagai 1 aksi.
        """
        if not jalur or len(jalur) < 2:
            return 0

        total_aksi = 0
        arah_sekarang = arah_awal
        
        arah_map_angka = {ARAH_ATAS: 0, ARAH_KANAN: 1, ARAH_BAWAH: 2, ARAH_KIRI: 3}

        for i in range(len(jalur) - 1):
            pos_awal = jalur[i]
            pos_tujuan = jalur[i+1]
            
            dx = pos_tujuan[0] - pos_awal[0]
            dy = pos_tujuan[1] - pos_awal[1]
            
            arah_dibutuhkan = ""
            if dx == 1: arah_dibutuhkan = ARAH_KANAN
            elif dx == -1: arah_dibutuhkan = ARAH_KIRI
            elif dy == 1: arah_dibutuhkan = ARAH_BAWAH
            elif dy == -1: arah_dibutuhkan = ARAH_ATAS

            if arah_sekarang != arah_dibutuhkan:
                indeks_awal = arah_map_angka[arah_sekarang]
                indeks_tujuan = arah_map_angka[arah_dibutuhkan]
                
                selisih = abs(indeks_awal - indeks_tujuan)
                
                jumlah_putar = selisih
                if selisih == 3: # putaran dari kiri ke atas
                    jumlah_putar = 1
                if selisih == 2: # putaran 180 derajat
                    jumlah_putar = 2
                
                total_aksi += jumlah_putar
                arah_sekarang = arah_dibutuhkan

            total_aksi += 1
            
        return total_aksi

    def reset_round(self):
        """
        Mereset papan permainan untuk babak baru.
        Fungsi ini sekarang menggunakan loop 'while' untuk memastikan papan yang valid
        selalu berhasil dibuat tanpa risiko rekursi.
        """
        self.percobaan_saat_ini = 0
        self.hint_digunakan = False
        
        while True:
            papan_data = self._buat_jalur_random()
            
            if papan_data is None:
                print("Gagal membuat papan, mencoba lagi...")
                continue

            self.papan_permainan, self.posisi_pemain, self.posisi_harta_karun = papan_data
            
            jalur_optimal = self.cari_jalur_terpendek_bfs(self.posisi_pemain, self.posisi_harta_karun)
            
            if jalur_optimal:
                self.arah_pemain = random.choice(ARAH_LIST)
                aksi_optimal = self._hitung_aksi_di_jalur(jalur_optimal, self.arah_pemain)
                self.sisa_langkah = aksi_optimal + 1
                break  # Berhasil, keluar dari loop while
            else:
                print("PERINGATAN: Tidak ditemukan jalur aman setelah pembuatan papan. Mereset ulang.")

    
    def _hitung_jarak_manhattan(self, pos1: tuple, pos2: tuple) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def cari_jalur_terpendek_bfs(self, start: tuple, end: tuple) -> list | None:
        antrian = deque([(start, [start])])
        dikunjungi = {start}
        while antrian:
            (x, y), jalur = antrian.popleft()
            if (x, y) == end:
                return jalur
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < PAPAN_LEBAR and 0 <= ny < PAPAN_TINGGI and (nx, ny) not in dikunjungi:
                    tile_tujuan = self.papan_permainan[ny][nx]
                    if tile_tujuan not in [TILE_DINDING, TILE_BOM]:
                        dikunjungi.add((nx, ny))
                        antrian.append(((nx, ny), jalur + [(nx, ny)]))
        return None

    def _buat_jalur_random(self) -> tuple | None:
        """
        Mencoba membuat papan yang valid. Mengembalikan data papan jika berhasil,
        atau None jika gagal setelah jumlah percobaan maksimum.
        Rekursi di akhir fungsi dihilangkan.
        """
        max_percobaan = 200
        for _ in range(max_percobaan):
            papan = [[TILE_DINDING for _ in range(PAPAN_LEBAR)] for _ in range(PAPAN_TINGGI)]
            x, y = random.randint(0, PAPAN_LEBAR - 1), random.randint(0, PAPAN_TINGGI - 1)
            start_pos = (x, y)
            papan[y][x] = TILE_JALUR
            
            for _ in range((PAPAN_LEBAR * PAPAN_TINGGI) * 2 // 3):
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
            jarak = self._hitung_jarak_manhattan(start_pos, end_pos)

            if total_jalur > 25 + JUMLAH_BOM and start_pos != end_pos and JARAK_MINIMAL_HARTA <= jarak <= JARAK_MAKSIMAL_HARTA:
                if not self._cari_jalur_internal(papan, start_pos, end_pos, [TILE_DINDING]): continue
                
                posisi_jalur_valid = [(ix, iy) for iy in range(PAPAN_TINGGI) for ix in range(PAPAN_LEBAR) if papan[iy][ix] == TILE_JALUR and (ix, iy) != start_pos and (ix, iy) != end_pos]
                
                if len(posisi_jalur_valid) >= JUMLAH_BOM:
                    papan_final = [row[:] for row in papan]
                    posisi_bom = random.sample(posisi_jalur_valid, JUMLAH_BOM)
                    for bx, by in posisi_bom:
                        papan_final[by][bx] = TILE_BOM
                    
                    if self._cari_jalur_internal(papan_final, start_pos, end_pos, [TILE_DINDING, TILE_BOM]):
                        return papan_final, start_pos, end_pos

        return None

    def _cari_jalur_internal(self, papan: list, start: tuple, end: tuple, halangan: list) -> list | None:
        lebar, tinggi = len(papan[0]), len(papan)
        antrian = deque([(start, [start])])
        dikunjungi = {start}
        while antrian:
            (x, y), jalur = antrian.popleft()
            if (x, y) == end: return jalur
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < lebar and 0 <= ny < tinggi and (nx, ny) not in dikunjungi and papan[ny][nx] not in halangan:
                    dikunjungi.add((nx, ny))
                    antrian.append(((nx, ny), jalur + [(nx, ny)]))
        return None
    
    def putar(self, arah_putar: str):
        if self.sisa_langkah <= 0: return
        self.sisa_langkah -= 1
        current_index = ARAH_LIST.index(self.arah_pemain)
        if arah_putar == 'kanan':
            new_index = (current_index + 1) % 4
        else:
            new_index = (current_index - 1 + 4) % 4
        self.arah_pemain = ARAH_LIST[new_index]
    
    def maju(self) -> bool:
        if self.sisa_langkah <= 0: return False
        self.sisa_langkah -= 1
        
        arah_map = {ARAH_ATAS: (0, -1), ARAH_KANAN: (1, 0), ARAH_BAWAH: (0, 1), ARAH_KIRI: (-1, 0)}
        dx, dy = arah_map[self.arah_pemain]
        
        current_x, current_y = self.posisi_pemain
        target_x, target_y = current_x + dx, current_y + dy

        if 0 <= target_x < PAPAN_LEBAR and 0 <= target_y < PAPAN_TINGGI:
            tile_tujuan = self.papan_permainan[target_y][target_x]
            if tile_tujuan != TILE_DINDING:
                self.posisi_pemain = (target_x, target_y)
                return True
        return False
