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

    def reset_round(self):
        """
        Mereset papan permainan untuk babak baru.
        Membuat labirin baru, menempatkan pemain dan harta, serta menghitung langkah.
        """
        self.percobaan_saat_ini = 0
        self.papan_permainan, self.posisi_pemain, self.posisi_harta_karun = self._buat_jalur_random()
        self.arah_pemain = random.choice(ARAH_LIST)
        
        jalur_optimal = self.cari_jalur_terpendek_bfs(self.posisi_pemain, self.posisi_harta_karun)
        if jalur_optimal:
            langkah_optimal = len(jalur_optimal) - 1
            self.sisa_langkah = int(langkah_optimal * 1.5) + 5
        else:
            # Fallback jika karena suatu alasan tidak ada jalur
            self.sisa_langkah = (PAPAN_LEBAR * PAPAN_TINGGI) // 2
    
    def _hitung_jarak_manhattan(self, pos1: tuple, pos2: tuple) -> int:
        """Menghitung jarak manhattan antara dua titik."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def cari_jalur_terpendek_bfs(self, start: tuple, end: tuple) -> list | None:
        """
        Mencari jalur terpendek dari start ke end menggunakan algoritma Breadth-First Search (BFS).
        
        Args:
            start (tuple): Koordinat (x, y) titik awal.
            end (tuple): Koordinat (x, y) titik akhir.
        
        Returns:
            list | None: Daftar koordinat jalur jika ditemukan, jika tidak None.
        """
        antrian = deque([(start, [start])])
        dikunjungi = {start}

        while antrian:
            (x, y), jalur = antrian.popleft()
            if (x, y) == end:
                return jalur
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < PAPAN_LEBAR and 0 <= ny < PAPAN_TINGGI and (nx, ny) not in dikunjungi:
                    if self.papan_permainan[ny][nx] != TILE_DINDING:
                        dikunjungi.add((nx, ny))
                        antrian.append(((nx, ny), jalur + [(nx, ny)]))
        return None

    def _buat_jalur_random(self) -> tuple:
        """
        Membuat papan permainan (labirin) secara acak hingga memenuhi kriteria.
        
        Returns:
            tuple: Berisi (papan_final, posisi_awal, posisi_akhir).
        """
        max_percobaan = 100
        for _ in range(max_percobaan):
            papan = [[TILE_DINDING for _ in range(PAPAN_LEBAR)] for _ in range(PAPAN_TINGGI)]
            x, y = random.randint(0, PAPAN_LEBAR - 1), random.randint(0, PAPAN_TINGGI - 1)
            start_pos = (x, y)
            papan[y][x] = TILE_JALUR
            
            # Random walk untuk membuat jalur
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

            # Validasi papan
            total_jalur = sum(row.count(TILE_JALUR) for row in papan)
            jarak = self._hitung_jarak_manhattan(start_pos, end_pos)

            if total_jalur > 25 + JUMLAH_BOM and start_pos != end_pos and JARAK_MINIMAL_HARTA <= jarak <= JARAK_MAKSIMAL_HARTA:
                if not self.cari_jalur_terpendek_bfs_internal(papan, start_pos, end_pos): continue
                
                # Tempatkan bom
                posisi_jalur_valid = [(ix, iy) for iy in range(PAPAN_TINGGI) for ix in range(PAPAN_LEBAR) if papan[iy][ix] == TILE_JALUR and (ix, iy) != start_pos and (ix, iy) != end_pos]
                
                if len(posisi_jalur_valid) >= JUMLAH_BOM:
                    papan_final = [row[:] for row in papan]
                    posisi_bom = random.sample(posisi_jalur_valid, JUMLAH_BOM)
                    for bx, by in posisi_bom:
                        papan_final[by][bx] = TILE_BOM
                    
                    # Pastikan masih ada jalur setelah bom ditempatkan
                    if self.cari_jalur_terpendek_bfs_internal(papan_final, start_pos, end_pos):
                        return papan_final, start_pos, end_pos

        # Fallback jika gagal setelah banyak percobaan
        print("Gagal membuat papan yang valid, mencoba lagi...")
        return self._buat_jalur_random()

    def cari_jalur_terpendek_bfs_internal(self, papan: list, start: tuple, end: tuple) -> list | None:
        """Versi internal BFS untuk digunakan dalam pembuatan papan."""
        lebar, tinggi = len(papan[0]), len(papan)
        antrian = deque([(start, [start])])
        dikunjungi = {start}
        while antrian:
            (x, y), jalur = antrian.popleft()
            if (x, y) == end: return jalur
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < lebar and 0 <= ny < tinggi and (nx, ny) not in dikunjungi and papan[ny][nx] != TILE_DINDING:
                    dikunjungi.add((nx, ny))
                    antrian.append(((nx, ny), jalur + [(nx, ny)]))
        return None
    
    def putar(self, arah_putar: str):
        """
        Memutar pemain ke kiri atau kanan dan mengurangi sisa langkah.
        
        Args:
            arah_putar (str): 'kiri' atau 'kanan'.
        """
        if self.sisa_langkah <= 0: return
        self.sisa_langkah -= 1
        current_index = ARAH_LIST.index(self.arah_pemain)
        if arah_putar == 'kanan':
            new_index = (current_index + 1) % 4
        else:
            new_index = (current_index - 1 + 4) % 4
        self.arah_pemain = ARAH_LIST[new_index]
    
    def maju(self) -> bool:
        """
        Menggerakkan pemain maju satu langkah sesuai arahnya.
        
        Returns:
            bool: True jika gerakan berhasil, False jika menabrak dinding.
        """
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
