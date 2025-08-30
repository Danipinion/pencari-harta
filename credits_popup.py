import customtkinter


class CreditsPopup(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        """
        Menginisialisasi jendela popup kredit.
        """
        super().__init__(*args, **kwargs)

        self.title("Credits")
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        self.geometry("450x350")
        self.resizable(False, False)
        self.after(50, self._center_window)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        credits_text = """
Pencarian Harta Karun

Dibuat oleh: Danipinion & Dzadafa

GitHub: 
@danipinion • @dzadafa 
Instagram: 
@danipinions • @dzadafa
"""

        label = customtkinter.CTkLabel(
            self, text=credits_text, font=("Segoe UI", 18, "bold"), justify="center"
        )
        label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        button = customtkinter.CTkButton(
            self,
            text="Mulai Permainan",
            command=self.destroy,
            font=("Segoe UI", 16, "bold"),
            height=40,
        )
        button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

    def _center_window(self):
        """Memusatkan jendela popup di tengah layar."""
        try:
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass
