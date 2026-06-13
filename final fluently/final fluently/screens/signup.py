import tkinter as tk
from tkinter import messagebox
from widgets import StyledButton, StyledEntry, Divider
from data_manager import DataManager
from config.config import BG, CARD, ACCENT, ACCENT2, DANGER, BORDER, MUTED, TEXT


class SignupScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
        tk.Frame(s, bg=ACCENT, height=3).pack(fill="x")

        center = tk.Frame(s, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Rejoindre Fluently",
                 font=("Georgia", 26, "bold"), bg=BG, fg=TEXT).pack(pady=(0, 4))
        tk.Label(center, text="Creez votre compte gratuitement",
                 font=("Courrier New", 10), bg=BG, fg=MUTED).pack(pady=(0, 20))

        card = tk.Frame(center, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(ipadx=10, ipady=10)

        tk.Label(card, text="INSCRIPTION", font=("Courrier New", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(pady=(20, 10))

        self.signup_user = StyledEntry(card, label="Nom d'utilisateur (min. 3 caracteres)")
        self.signup_user.pack(fill="x", padx=30, pady=4)

        self.signup_pass = StyledEntry(card, label="Mot de passe (min. 4 caracteres)", show="*")
        self.signup_pass.pack(fill="x", padx=30, pady=4)

        self.signup_pass2 = StyledEntry(card, label="Confirmer le mot de passe", show="*")
        self.signup_pass2.pack(fill="x", padx=30, pady=4)

        self.signup_error = tk.Label(card, text="", font=("Courrier New", 9),
                                     bg=CARD, fg=DANGER)
        self.signup_error.pack(pady=(4, 0))

        StyledButton(card, text="CREER MON COMPTE",
                     font=("Courier New", 11, "bold"),
                     bg=ACCENT, fg="white",
                     hover_bg=ACCENT2, hover_fg="white",
                     padx=30, pady=10,
                     command=self._do_signup).pack(pady=(12, 6))

        Divider(card).pack(fill="x", padx=30, pady=10)

        tk.Label(card, text="Deja inscrit ?",
                 font=("Courier New", 9), bg=CARD, fg=MUTED).pack()
        StyledButton(card, text="SE CONNECTER",
                     font=("Courier New", 10, "bold"),
                     bg=CARD, fg=ACCENT2,
                     hover_bg=CARD, hover_fg=ACCENT,
                     padx=0, pady=8,
                     command=lambda: self.app.show("login")).pack(pady=(0, 16))

    def _do_signup(self):
        username = self.signup_user.get().strip()
        password = self.signup_pass.get()
        confirm = self.signup_pass2.get()

        if password != confirm:
            self.signup_error.configure(text="Les mots de passe ne correspondent pas.")
            return

        ok, message = DataManager.register(username, password)
        if ok:
            self.signup_error.configure(text="", fg=DANGER)
            self.signup_user.clear()
            self.signup_pass.clear()
            self.signup_pass2.clear()
            messagebox.showinfo("Bienvenue !", f"Compte cree avec succes !\nBienvenue {username} !")
            self.app.show("login")
        else:
            self.signup_error.configure(text=message)

