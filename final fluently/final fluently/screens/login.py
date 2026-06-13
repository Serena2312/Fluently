import tkinter as tk
from widgets import StyledButton, StyledEntry, Divider
from data_manager import DataManager
from config.config import BG, CARD, ACCENT, ACCENT2, DANGER, BORDER, MUTED, TEXT


class LoginScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
        tk.Frame(s, bg=ACCENT, height=3).pack(fill="x")

        center = tk.Frame(s, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Fluently", font=("Georgia", 44 , "bold italic"),
                 bg=BG, fg=ACCENT2).pack()
        tk.Label(center, text="Connectez-vous pour continuer",
                 font=("Courrier New", 10), bg=BG, fg=MUTED).pack(pady=(4, 20))

        card = tk.Frame(center, bg=CARD, highlightthickness=1, highlightbackground=BORDER)

        card.pack(padx=0, pady=0, ipadx=10, ipady=10)

        tk.Label(card, text="CONNEXION", font=("Courrier New", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(pady=(20, 10))

        self.login_user = StyledEntry(card, label="Nom d'utilisateur")
        self.login_user.pack(fill="x", padx=30, pady=4)

        self.login_pass = StyledEntry(card, label="Mot de passe", show="*")
        self.login_pass.pack(fill="x", padx=30, pady=4)

        self.login_error = tk.Label(card, text="", font=("Courrier New", 9),
                                    bg=CARD, fg=DANGER)
        self.login_error.pack(pady=(4, 0))

        StyledButton(card, text="SE CONNECTER",
                     font=("Courrier New", 11, "bold"),
                     bg=ACCENT, fg="white",
                     hover_bg=ACCENT2, hover_fg="white",
                     padx=30, pady=10,
                     command=self._do_login).pack(pady=(12, 6))

        Divider(card).pack(fill="x", padx=30, pady=10)

        tk.Label(card, text="Pas encore de compte ?",
                 font=("Courrier New", 9), bg=CARD, fg=MUTED).pack()
        StyledButton(card, text="S'INSCRIRE ICI",
                     font=("Courrier New", 10, "bold"),
                     bg=CARD, fg=ACCENT2,
                     hover_bg=CARD, hover_fg=ACCENT,
                     padx=0, pady=8,
                     command=lambda: self.app.show("signup")).pack(pady=(0, 16))

    def _do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        ok, result = DataManager.login(username, password)
        if ok:
            self.app.current_user = username
            self.app.current_profile = result
            self.login_error.configure(text="")
            self.login_user.clear()
            self.login_pass.clear()
            self.app.show("menu")
        else:
            self.login_error.configure(text=result)

