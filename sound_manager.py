import pygame
from config import SOUND_FILES

class SoundManager:
    """
    Mengelola semua aspek suara dalam permainan.
    Menginisialisasi pygame.mixer, memuat file suara, dan memutarnya.
    """
    def __init__(self):
        """
        Menginisialisasi SoundManager dan memuat semua efek suara.
        """
        self.sound_effects = {}
        self.pygame_available = self._init_pygame_mixer()
        if self.pygame_available:
            self._load_sounds()

    def _init_pygame_mixer(self) -> bool:
        """
        Mencoba menginisialisasi pygame.mixer.
        
        Returns:
            bool: True jika berhasil, False jika gagal.
        """
        try:
            pygame.mixer.init()
            return True
        except pygame.error as e:
            print(f"Peringatan: Gagal menginisialisasi pygame mixer: {e}. Permainan akan berjalan tanpa suara.")
            return False

    def _load_sounds(self):
        """
        Memuat file suara yang ditentukan dalam config.py.
        Jika file tidak ditemukan, suara tersebut tidak akan dimainkan.
        """
        if not self.pygame_available: return
        
        for name, path in SOUND_FILES.items():
            try:
                self.sound_effects[name] = pygame.mixer.Sound(path)
            except pygame.error:
                print(f"Peringatan: File suara tidak ditemukan di '{path}'. Suara '{name}' tidak akan diputar.")
                self.sound_effects[name] = None
    
    def play(self, name: str):
        """
        Memainkan efek suara berdasarkan namanya.
        
        Args:
            name (str): Nama efek suara yang akan diputar (misal: 'move', 'win').
        """
        if self.pygame_available and name in self.sound_effects and self.sound_effects[name]:
            self.sound_effects[name].play()
