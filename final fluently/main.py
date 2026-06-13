#  Fluently — Jeu d'apprentissage des langues
#  Auteur      : Mancuso Serena 6TT4
#  Description : Jeu termine avec inscription + connexion, jeu de traduction,
#                partie commentaires, classement et profil de l'utilisateur.


import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import hashlib
import datetime

from config.Traductions import LANGUAGES
from config.config import BG, CARD2, CARD, CARD3, ACCENT, ACCENT2, ACCENT3, SUCCESS, SUCCESS2, DANGER, DANGER2, GOLD, GOLD2, TEXT, MUTED, BORDER, POINTS, TIMER, COMBO_BONUS, TOTAL_QUESTIONS, MAX_LIVES

#  gestion de données (Lecture/Écriture JSON)

class DataManager:
    """
    Gère toutes les opérations de lecture et d'écriture des données utilisateurs.
    Les données sont stockées dans le fichier 'users.json'.
    """

    FILE = "users.json"

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hache le mot de passe avec SHA-256 pour plus de sécurité."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def load() -> dict:
        """Charge les données depuis le fichier JSON. Retourne un dict vide si absent."""
        if not os.path.exists(DataManager.FILE):
            return {}
        try:
            with open(DataManager.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    @staticmethod
    def save(data: dict) -> None:
        """Sauvegarde les données dans le fichier JSON."""
        with open(DataManager.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def register(username: str, password: str) -> tuple:
        """
        Inscrit un nouvel utilisateur.
        Retourne (True, 'message') si succès, (False, 'erreur') sinon.
        """
        if not username.strip() or not password.strip():
            return False, "Les champs ne peuvent pas etre vides."
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit faire au moins 3 caracteres."
        if len(password) < 4:
            return False, "Le mot de passe doit faire au moins 4 caracteres."

        data = DataManager.load()
        if username in data:
            return False, "Ce nom d'utilisateur est deja utilise."

        # Créer le profil utilisateur complet
        data[username] = {
            "password":     DataManager._hash_password(password),
            "created_at":   datetime.datetime.now().strftime("%d/%m/%Y"),
            "high_score":   0,
            "total_games":  0,
            "total_wins":   0,
            "total_points": 0,
            "comments":     [],   # Liste des commentaires postés par l'utilisateur
        }
        DataManager.save(data)
        return True, "Inscription reussie !"

    @staticmethod
    def login(username: str, password: str) -> tuple:
        """
        Vérifie les identifiants.
        Retourne (True, profil_dict) si succès, (False, 'erreur') sinon.
        """
        if not username.strip() or not password.strip():
            return False, "Les champs ne peuvent pas etre vides."

        data = DataManager.load()
        if username not in data:
            return False, "Nom d'utilisateur introuvable."
        if data[username]["password"] != DataManager._hash_password(password):
            return False, "Mot de passe incorrect."

        return True, data[username]

    @staticmethod
    def update_user(username: str, profile: dict) -> None:
        """Met à jour le profil d'un utilisateur dans le fichier JSON."""
        data = DataManager.load()
        data[username] = profile
        DataManager.save(data)

    @staticmethod
    def get_all_comments() -> list:
        """
        Récupère tous les commentaires de tous les utilisateurs.
        Retourne une liste triée du plus récent au plus ancien.
        """
        data = DataManager.load()
        all_comments = []
        for username, profile in data.items():
            for comment in profile.get("comments", []):
                all_comments.append({
                    "author": username,
                    "text":   comment["text"],
                    "date":   comment["date"],
                    "rating": comment.get("rating", 0),
                })
        # Trier par date décroissante
        all_comments.sort(key=lambda c: c["date"], reverse=True)
        return all_comments

    @staticmethod
    def get_leaderboard() -> list:
        """
        Retourne le classement des joueurs trié par meilleur score.
        Chaque entrée : {"rank": int, "username": str, "high_score": int, ...}
        """
        data = DataManager.load()
        board = []
        for username, profile in data.items():
            board.append({
                "username":    username,
                "high_score":  profile.get("high_score", 0),
                "total_games": profile.get("total_games", 0),
                "total_wins":  profile.get("total_wins", 0),
            })
        board.sort(key=lambda x: x["high_score"], reverse=True)
        for i, entry in enumerate(board):
            entry["rank"] = i + 1
        return board


# WIDGETS RÉUTILISABLES (Composants UI personnalisés)

class StyledButton(tk.Button):
    """
    Bouton personnalisé avec effets de survol (hover) intégrés.
    Paramètres supplémentaires : hover_bg, hover_fg.
    """
    def __init__(self, parent, hover_bg=ACCENT2, hover_fg="white", **kwargs):
        # Couleurs normales (on les sauvegarde pour le retour hover)
        self._normal_bg = kwargs.get("bg", CARD2)
        self._normal_fg = kwargs.get("fg", TEXT)
        self._hover_bg  = hover_bg
        self._hover_fg  = hover_fg

        super().__init__(parent, **kwargs)
        self.configure(relief="flat", bd=0, cursor="hand2",
                       activebackground=hover_bg, activeforeground=hover_fg)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        self.configure(bg=self._hover_bg, fg=self._hover_fg)

    def _on_leave(self, _event):
        self.configure(bg=self._normal_bg, fg=self._normal_fg)


class StyledEntry(tk.Frame):
    """
    Champ de saisie stylisé avec label intégré, bordure colorée et gestion du focus.
    """
    def __init__(self, parent, label="", show="", **kwargs):
        super().__init__(parent, bg=CARD, highlightthickness=1,
                         highlightbackground=BORDER)

        # Label du champ (ex: "Nom d'utilisateur")
        if label:
            tk.Label(self, text=label, font=("Courier New", 9),
                     bg=CARD, fg=MUTED).pack(anchor="w", padx=10, pady=(8, 0))

        # Champ de saisie
        self.entry = tk.Entry(self, show=show,
                               font=("Courier New", 12),
                               bg=CARD, fg=TEXT, insertbackground=ACCENT,
                               relief="flat", bd=0)
        self.entry.pack(fill="x", padx=10, pady=(2, 10))

        # Changer la couleur de bordure au focus
        self.entry.bind("<FocusIn>",  self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def _focus_in(self, _event):
        self.configure(highlightbackground=ACCENT)

    def _focus_out(self, _event):
        self.configure(highlightbackground=BORDER)

    def get(self) -> str:
        return self.entry.get()

    def clear(self):
        self.entry.delete(0, tk.END)

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class Divider(tk.Frame):
    """Ligne de séparation horizontale."""
    def __init__(self, parent, color=BORDER, **kwargs):
        super().__init__(parent, bg=color, height=1, **kwargs)


class StarRating(tk.Frame):
    """Widget de notation par étoiles (1 à 5)."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=CARD, **kwargs)
        self.rating = tk.IntVar(value=0)
        self._stars = []
        for i in range(1, 6):
            btn = tk.Button(self, text="*", font=("Georgia", 18),
                            bg=CARD, fg=MUTED, relief="flat", bd=0,
                            cursor="hand2",
                            command=lambda v=i: self._set_rating(v))
            btn.pack(side="left", padx=2)
            self._stars.append(btn)

    def _set_rating(self, value: int):
        self.rating.set(value)
        for i, btn in enumerate(self._stars):
            btn.configure(fg=GOLD if i < value else MUTED)

    def get(self) -> int:
        return self.rating.get()



#  jeu principal


class Fluently(tk.Tk):
    """
    Classe principale de l'application.
    Gère la navigation entre les différents écrans et l'état global de session.
    """

    def __init__(self):
        super().__init__()

        # --- Configuration de la fenêtre principale ---
        self.title("Fluently — Apprends les langues")
        self.geometry("840x680")
        self.minsize(760, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        # --- État de la session en cours ---
        self.current_user    = None    # Nom d'utilisateur connecté
        self.current_profile = None    # Dictionnaire du profil utilisateur

        # --- Variables de jeu (initialisées dans _reset_game) ---
        self.language    = tk.StringVar(value="Anglais")
        self.difficulty  = tk.StringVar(value="Facile")
        self.score       = 0
        self.combo       = 0
        self.max_combo   = 0
        self.lives       = MAX_LIVES
        self.question_n  = 0
        self.correct_n   = 0
        self.questions   = []
        self.current_q   = None
        self.answered    = False
        self.timer_val   = 0
        self._timer_job  = None

        # --- Construction de l'interface ---
        self._build_all_screens()
        self.show("login")

    #  affichage de l'écran avec le nom

    def show(self, name: str):
        """Affiche l'écran demandé et masque les autres. Appelle le hook de refresh si défini."""
        self.screens[name].lift()
        refresh_hook = getattr(self, f"_refresh_{name}", None)
        if refresh_hook:
            refresh_hook()


    #  mise en place de tous les ecrans

    def _build_all_screens(self):
        """Crée le conteneur principal et construit chaque écran."""
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)

        self.screens = {}
        screen_names = ["login", "signup", "menu", "profile",
                        "leaderboard", "comments", "game", "result"]

        for name in screen_names:
            frame = tk.Frame(container, bg=BG)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.screens[name] = frame

        # Construire chaque écran dans l'ordre
        self._build_login_screen()
        self._build_signup_screen()
        self._build_menu_screen()
        self._build_profile_screen()
        self._build_leaderboard_screen()
        self._build_comments_screen()
        self._build_game_screen()
        self._build_result_screen()

    #  connexion

    def _build_login_screen(self):
        s = self.screens["login"]

        # Bande décorative en haut
        tk.Frame(s, bg=ACCENT, height=3).pack(fill="x")

        # Zone centrale
        center = tk.Frame(s, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Titre
        tk.Label(center, text="Fluently", font=("Georgia", 44, "bold italic"),
                 bg=BG, fg=ACCENT2).pack()
        tk.Label(center, text="Connectez-vous pour continuer",
                 font=("Courier New", 10), bg=BG, fg=MUTED).pack(pady=(4, 20))

        # Carte de connexion
        card = tk.Frame(center, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(padx=0, pady=0, ipadx=10, ipady=10)

        tk.Label(card, text="CONNEXION", font=("Courier New", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(pady=(20, 10))

        # Champs de saisie
        self.login_user = StyledEntry(card, label="Nom d'utilisateur")
        self.login_user.pack(fill="x", padx=30, pady=4)

        self.login_pass = StyledEntry(card, label="Mot de passe", show="*")
        self.login_pass.pack(fill="x", padx=30, pady=4)

        # Label pour afficher les erreurs
        self.login_error = tk.Label(card, text="", font=("Courier New", 9),
                                     bg=CARD, fg=DANGER)
        self.login_error.pack(pady=(4, 0))

        # Bouton Se connecter
        StyledButton(card, text="SE CONNECTER",
                     font=("Courier New", 11, "bold"),
                     bg=ACCENT, fg="white",
                     hover_bg=ACCENT2, hover_fg="white",
                     padx=30, pady=10,
                     command=self._do_login).pack(pady=(12, 6))

        Divider(card).pack(fill="x", padx=30, pady=10)

        # Lien vers inscription
        tk.Label(card, text="Pas encore de compte ?",
                 font=("Courier New", 9), bg=CARD, fg=MUTED).pack()
        StyledButton(card, text="S'INSCRIRE ICI",
                     font=("Courier New", 10, "bold"),
                     bg=CARD, fg=ACCENT2,
                     hover_bg=CARD, hover_fg=ACCENT,
                     padx=0, pady=8,
                     command=lambda: self.show("signup")).pack(pady=(0, 16))

    def _do_login(self):
        """Tente de connecter l'utilisateur avec les informations saisies."""
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        ok, result = DataManager.login(username, password)
        if ok:
            self.current_user    = username
            self.current_profile = result
            self.login_error.configure(text="")
            self.login_user.clear()
            self.login_pass.clear()
            self.show("menu")
        else:
            self.login_error.configure(text=result)

    #  inscription

    def _build_signup_screen(self):
        s = self.screens["signup"]

        tk.Frame(s, bg=ACCENT, height=3).pack(fill="x")

        center = tk.Frame(s, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Rejoindre Fluently",
                 font=("Georgia", 26, "bold"), bg=BG, fg=TEXT).pack(pady=(0, 4))
        tk.Label(center, text="Creez votre compte gratuitement",
                 font=("Courier New", 10), bg=BG, fg=MUTED).pack(pady=(0, 20))

        card = tk.Frame(center, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(ipadx=10, ipady=10)

        tk.Label(card, text="INSCRIPTION", font=("Courier New", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(pady=(20, 10))

        self.signup_user = StyledEntry(card, label="Nom d'utilisateur (min. 3 caracteres)")
        self.signup_user.pack(fill="x", padx=30, pady=4)

        self.signup_pass = StyledEntry(card, label="Mot de passe (min. 4 caracteres)", show="*")
        self.signup_pass.pack(fill="x", padx=30, pady=4)

        self.signup_pass2 = StyledEntry(card, label="Confirmer le mot de passe", show="*")
        self.signup_pass2.pack(fill="x", padx=30, pady=4)

        self.signup_error = tk.Label(card, text="", font=("Courier New", 9),
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
                     command=lambda: self.show("login")).pack(pady=(0, 16))

    def _do_signup(self):
        """Tente d'inscrire un nouvel utilisateur."""
        username = self.signup_user.get().strip()
        password = self.signup_pass.get()
        confirm  = self.signup_pass2.get()

        # Vérification de la confirmation du mot de passe
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
            self.show("login")
        else:
            self.signup_error.configure(text=message)

    #  menu principal

    def _build_menu_screen(self):
        s = self.screens["menu"]

        # En-tête avec logo et bouton déconnexion
        header = tk.Frame(s, bg=CARD, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="Fluently",
                 font=("Georgia", 16, "bold italic"), bg=CARD, fg=ACCENT2).pack(side="left", padx=20)

        StyledButton(header, text="Deconnexion",
                     font=("Courier New", 9), bg=CARD, fg=MUTED,
                     hover_bg=CARD, hover_fg=DANGER,
                     padx=10, pady=4,
                     command=self._do_logout).pack(side="right", padx=20)

        Divider(s, color=BORDER).pack(fill="x")

        # Zone principale
        main = tk.Frame(s, bg=BG)
        main.pack(fill="both", expand=True, padx=60, pady=20)

        # Message de bienvenue (mis à jour au refresh)
        self.menu_welcome = tk.Label(main, text="",
                                      font=("Georgia", 22, "bold"), bg=BG, fg=TEXT)
        self.menu_welcome.pack(anchor="w", pady=(0, 4))

        self.menu_sub = tk.Label(main, text="",
                                  font=("Courier New", 10), bg=BG, fg=MUTED)
        self.menu_sub.pack(anchor="w", pady=(0, 20))

        Divider(main).pack(fill="x", pady=10)

        # ---- Sélection de la langue ----
        tk.Label(main, text="LANGUE A APPRENDRE",
                 font=("Courier New", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w")

        lang_row = tk.Frame(main, bg=BG)
        lang_row.pack(anchor="w", pady=(6, 16))

        self._lang_buttons = {}
        for lang in LANGUAGES:
            btn = StyledButton(lang_row, text=lang,
                               font=("Courier New", 10, "bold"),
                               bg=CARD2, fg=MUTED,
                               hover_bg=ACCENT, hover_fg="white",
                               padx=16, pady=8,
                               command=lambda l=lang: self._select_lang(l))
            btn.pack(side="left", padx=4)
            self._lang_buttons[lang] = btn
        self._select_lang("Anglais")

        # ---- Sélection de la difficulté ----
        tk.Label(main, text="DIFFICULTE",
                 font=("Courier New", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w")

        diff_row = tk.Frame(main, bg=BG)
        diff_row.pack(anchor="w", pady=(6, 24))

        diff_info = {
            "Facile":    f"+{POINTS['Facile']} pts  |  {TIMER['Facile']}s",
            "Moyen":     f"+{POINTS['Moyen']} pts  |  {TIMER['Moyen']}s",
            "Difficile": f"+{POINTS['Difficile']} pts  |  {TIMER['Difficile']}s",
        }

        self._diff_buttons = {}
        for diff, info in diff_info.items():
            btn = StyledButton(diff_row, text=f"{diff}   {info}",
                               font=("Courier New", 10, "bold"),
                               bg=CARD2, fg=MUTED,
                               hover_bg=ACCENT, hover_fg="white",
                               padx=16, pady=8,
                               command=lambda d=diff: self._select_diff(d))
            btn.pack(side="left", padx=4)
            self._diff_buttons[diff] = btn
        self._select_diff("Facile")

        # ---- Boutons de navigation ----
        Divider(main).pack(fill="x", pady=10)

        nav_grid = tk.Frame(main, bg=BG)
        nav_grid.pack(fill="x", pady=10)

        # Bouton JOUER (grand, central)
        play_btn = StyledButton(nav_grid, text="JOUER",
                                font=("Courier New", 14, "bold"),
                                bg=ACCENT, fg="white",
                                hover_bg=ACCENT2, hover_fg="white",
                                padx=40, pady=16,
                                command=self._start_game)
        play_btn.grid(row=0, column=0, rowspan=2, padx=(0, 12), pady=4, sticky="ns")

        # Boutons secondaires
        btns_right = [
            ("Mon Profil",    "profile"),
            ("Classement",    "leaderboard"),
            ("Commentaires",  "comments"),
        ]
        for i, (label, screen) in enumerate(btns_right):
            StyledButton(nav_grid, text=label,
                         font=("Courier New", 10, "bold"),
                         bg=CARD2, fg=TEXT,
                         hover_bg=CARD3, hover_fg=ACCENT2,
                         padx=20, pady=10,
                         command=lambda sc=screen: self.show(sc)).grid(
                             row=i // 2, column=1 + i % 2,
                             padx=4, pady=4, sticky="ew")

        for c in range(3):
            nav_grid.columnconfigure(c, weight=1 if c > 0 else 2)

        # Score du jour
        self.menu_score_label = tk.Label(main, text="",
                                          font=("Courier New", 10), bg=BG, fg=MUTED)
        self.menu_score_label.pack(anchor="w", pady=(16, 0))

    def _refresh_menu(self):
        """Met à jour les informations affichées dans le menu."""
        if not self.current_user:
            return
        self.menu_welcome.configure(
            text=f"Bonjour, {self.current_user} !")
        self.menu_sub.configure(
            text=f"Membre depuis le {self.current_profile.get('created_at', '?')}  |  "
                 f"{self.current_profile.get('total_games', 0)} parties jouees")
        self.menu_score_label.configure(
            text=f"Meilleur score personnel : {self.current_profile.get('high_score', 0)} pts")

    def _select_lang(self, lang: str):
        """Met en surbrillance le bouton de langue sélectionné."""
        self.language.set(lang)
        for l, b in self._lang_buttons.items():
            b.configure(bg=ACCENT if l == lang else CARD2,
                        fg="white" if l == lang else MUTED)

    def _select_diff(self, diff: str):
        """Met en surbrillance le bouton de difficulté sélectionné."""
        self.difficulty.set(diff)
        for d, b in self._diff_buttons.items():
            b.configure(bg=ACCENT if d == diff else CARD2,
                        fg="white" if d == diff else MUTED)

    def _do_logout(self):
        """Déconnecte l'utilisateur et retourne à l'écran de connexion."""
        self.current_user    = None
        self.current_profile = None
        self.show("login")

    #  profil de l'utilisateur

    def _build_profile_screen(self):
        s = self.screens["profile"]

        self._make_header(s, "MON PROFIL", back_screen="menu")

        content = tk.Frame(s, bg=BG)
        content.pack(fill="both", expand=True, padx=60, pady=20)

        # Avatar textuel
        avatar_f = tk.Frame(content, bg=CARD, highlightthickness=1,
                            highlightbackground=BORDER)
        avatar_f.pack(fill="x", pady=(0, 16), ipady=20)

        self.prof_avatar = tk.Label(avatar_f, text="?",
                                     font=("Georgia", 42, "bold"),
                                     bg=CARD, fg=ACCENT2)
        self.prof_avatar.pack()

        self.prof_name = tk.Label(avatar_f, text="",
                                   font=("Georgia", 18, "bold"), bg=CARD, fg=TEXT)
        self.prof_name.pack()

        self.prof_since = tk.Label(avatar_f, text="",
                                    font=("Courier New", 9), bg=CARD, fg=MUTED)
        self.prof_since.pack()

        # Statistiques
        stats_f = tk.Frame(content, bg=BG)
        stats_f.pack(fill="x")

        self._prof_stat_labels = {}
        stat_defs = [
            ("high_score",   "Meilleur score",    GOLD),
            ("total_games",  "Parties jouees",    TEXT),
            ("total_wins",   "Victoires",          SUCCESS),
            ("total_points", "Points totaux",     ACCENT2),
        ]

        for i, (key, label, color) in enumerate(stat_defs):
            box = tk.Frame(stats_f, bg=CARD, highlightthickness=1,
                           highlightbackground=BORDER)
            box.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="ew", ipadx=10, ipady=12)
            stats_f.columnconfigure(i % 2, weight=1)

            tk.Label(box, text=label, font=("Courier New", 9),
                     bg=CARD, fg=MUTED).pack()
            lv = tk.Label(box, text="—", font=("Georgia", 22, "bold"),
                          bg=CARD, fg=color)
            lv.pack()
            self._prof_stat_labels[key] = lv

    def _refresh_profile(self):
        """Met à jour les données du profil affichées."""
        if not self.current_profile:
            return
        initial = self.current_user[0].upper() if self.current_user else "?"
        self.prof_avatar.configure(text=initial)
        self.prof_name.configure(text=self.current_user)
        self.prof_since.configure(
            text=f"Membre depuis le {self.current_profile.get('created_at', '?')}")

        for key, label_widget in self._prof_stat_labels.items():
            val = self.current_profile.get(key, 0)
            suffix = " pts" if "score" in key or "points" in key else ""
            label_widget.configure(text=f"{val}{suffix}")

    #  Leaderboard

    def _build_leaderboard_screen(self):
        s = self.screens["leaderboard"]

        self._make_header(s, "CLASSEMENT", back_screen="menu")

        content = tk.Frame(s, bg=BG)
        content.pack(fill="both", expand=True, padx=60, pady=10)

        # En-tête du tableau
        header = tk.Frame(content, bg=CARD2)
        header.pack(fill="x", pady=(0, 2))

        for col, (label, w) in enumerate([
            ("#",           3),
            ("Joueur",      12),
            ("Meill. score",8),
            ("Parties",     6),
            ("Victoires",   6),
        ]):
            tk.Label(header, text=label, font=("Courier New", 9, "bold"),
                     bg=CARD2, fg=MUTED, width=w, anchor="w").grid(
                         row=0, column=col, padx=8, pady=8, sticky="w")

        # Conteneur scrollable pour les lignes
        self.leaderboard_frame = tk.Frame(content, bg=BG)
        self.leaderboard_frame.pack(fill="both", expand=True)

    def _refresh_leaderboard(self):
        """Recharge et affiche le classement depuis le fichier JSON."""
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()

        board = DataManager.get_leaderboard()

        if not board:
            tk.Label(self.leaderboard_frame, text="Aucun joueur pour l'instant.",
                     font=("Courier New", 11), bg=BG, fg=MUTED).pack(pady=30)
            return

        rank_colors = {1: GOLD, 2: "#C0C0C0", 3: "#CD7F32"}

        for entry in board:
            rank = entry["rank"]
            is_me = entry["username"] == self.current_user
            row_bg = CARD if is_me else (BG if rank % 2 == 0 else CARD)

            row = tk.Frame(self.leaderboard_frame, bg=row_bg,
                           highlightthickness=1 if is_me else 0,
                           highlightbackground=ACCENT)
            row.pack(fill="x", pady=1)

            rank_color = rank_colors.get(rank, TEXT)
            rank_text  = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"{rank}th")

            for col, (val, w) in enumerate([
                (rank_text,                   3),
                (entry["username"] + (" (moi)" if is_me else ""), 12),
                (f"{entry['high_score']} pts", 8),
                (str(entry["total_games"]),    6),
                (str(entry["total_wins"]),     6),
            ]):
                color = rank_color if col == 0 else (ACCENT2 if is_me else TEXT)
                tk.Label(row, text=val, font=("Courier New", 10,
                          "bold" if col == 0 or is_me else "normal"),
                         bg=row_bg, fg=color, width=w, anchor="w").grid(
                             row=0, column=col, padx=8, pady=8, sticky="w")

    #  partie commentaire

    def _build_comments_screen(self):
        s = self.screens["comments"]

        self._make_header(s, "COMMENTAIRES & AVIS", back_screen="menu")

        # Zone de saisie d'un nouveau commentaire
        post_f = tk.Frame(s, bg=CARD, highlightthickness=1,
                          highlightbackground=BORDER)
        post_f.pack(fill="x", padx=40, pady=(10, 0))

        tk.Label(post_f, text="LAISSER UN COMMENTAIRE",
                 font=("Courier New", 9, "bold"), bg=CARD, fg=MUTED).pack(
                     anchor="w", padx=16, pady=(12, 6))

        self.comment_entry = tk.Text(post_f, height=3,
                                      font=("Courier New", 11),
                                      bg=CARD2, fg=TEXT, insertbackground=ACCENT,
                                      relief="flat", bd=0, padx=10, pady=8,
                                      wrap="word")
        self.comment_entry.pack(fill="x", padx=16, pady=(0, 6))

        bottom_bar = tk.Frame(post_f, bg=CARD)
        bottom_bar.pack(fill="x", padx=16, pady=(0, 12))

        # Widget de notation par étoiles
        tk.Label(bottom_bar, text="Note : ",
                 font=("Courier New", 10), bg=CARD, fg=MUTED).pack(side="left")
        self.star_rating = StarRating(bottom_bar)
        self.star_rating.pack(side="left")

        StyledButton(bottom_bar, text="PUBLIER",
                     font=("Courier New", 10, "bold"),
                     bg=ACCENT, fg="white",
                     hover_bg=ACCENT2, hover_fg="white",
                     padx=16, pady=6,
                     command=self._post_comment).pack(side="right")

        # Zone d'affichage des commentaires (avec scrollbar)
        list_f = tk.Frame(s, bg=BG)
        list_f.pack(fill="both", expand=True, padx=40, pady=10)

        tk.Label(list_f, text="TOUS LES AVIS",
                 font=("Courier New", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w")

        # Canvas + scrollbar pour liste scrollable
        canvas = tk.Canvas(list_f, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_f, orient="vertical",
                                 command=canvas.yview)
        self.comments_inner = tk.Frame(canvas, bg=BG)

        self.comments_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.comments_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    def _post_comment(self):
        """Publie le commentaire saisi par l'utilisateur."""
        text   = self.comment_entry.get("1.0", "end").strip()
        rating = self.star_rating.get()

        if not text:
            messagebox.showwarning("Commentaire vide",
                                   "Veuillez ecrire quelque chose !")
            return
        if rating == 0:
            messagebox.showwarning("Note manquante",
                                   "Veuillez attribuer une note (1 a 5 etoiles).")
            return

        # Ajouter le commentaire au profil
        comment = {
            "text":   text,
            "date":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "rating": rating,
        }
        if "comments" not in self.current_profile:
            self.current_profile["comments"] = []
        self.current_profile["comments"].append(comment)
        DataManager.update_user(self.current_user, self.current_profile)

        # Réinitialiser le champ
        self.comment_entry.delete("1.0", "end")
        self.star_rating._set_rating(0)

        # Rafraîchir la liste
        self._refresh_comments()

    def _refresh_comments(self):
        """Recharge et affiche tous les commentaires."""
        for widget in self.comments_inner.winfo_children():
            widget.destroy()

        all_comments = DataManager.get_all_comments()

        if not all_comments:
            tk.Label(self.comments_inner, text="Aucun commentaire pour l'instant. Soyez le premier !",
                     font=("Courier New", 10), bg=BG, fg=MUTED).pack(pady=20)
            return

        for comment in all_comments:
            card = tk.Frame(self.comments_inner, bg=CARD,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(fill="x", pady=4, padx=2)

            # En-tête du commentaire
            top = tk.Frame(card, bg=CARD)
            top.pack(fill="x", padx=14, pady=(10, 4))

            is_me = comment["author"] == self.current_user
            author_color = ACCENT2 if is_me else TEXT
            tk.Label(top, text=comment["author"] + (" (moi)" if is_me else ""),
                     font=("Courier New", 10, "bold"),
                     bg=CARD, fg=author_color).pack(side="left")

            # Étoiles
            stars = "*" * comment["rating"] + "-" * (5 - comment["rating"])
            tk.Label(top, text=stars, font=("Georgia", 11),
                     bg=CARD, fg=GOLD).pack(side="left", padx=10)

            # Date
            tk.Label(top, text=comment["date"],
                     font=("Courier New", 8), bg=CARD, fg=MUTED).pack(side="right")

            # Texte du commentaire
            tk.Label(card, text=comment["text"],
                     font=("Courier New", 10), bg=CARD, fg=TEXT,
                     wraplength=640, justify="left", anchor="w").pack(
                         fill="x", padx=14, pady=(0, 12))

    #  JEU

    def _build_game_screen(self):
        s = self.screens["game"]

        # --- Barre d'infos en haut ---
        top_bar = tk.Frame(s, bg=CARD, pady=10)
        top_bar.pack(fill="x")

        self.g_lives  = tk.Label(top_bar, text="", font=("Courier New", 12, "bold"),
                                  bg=CARD, fg=DANGER)
        self.g_lives.pack(side="left", padx=16)

        self.g_qcount = tk.Label(top_bar, text="", font=("Courier New", 10),
                                  bg=CARD, fg=MUTED)
        self.g_qcount.pack(side="left")

        self.g_combo  = tk.Label(top_bar, text="", font=("Courier New", 10, "bold"),
                                  bg=CARD, fg=GOLD)
        self.g_combo.pack(side="left", padx=12)

        self.g_score  = tk.Label(top_bar, text="0 pts",
                                  font=("Georgia", 14, "bold"),
                                  bg=CARD, fg=ACCENT2)
        self.g_score.pack(side="right", padx=16)

        self.g_info   = tk.Label(top_bar, text="", font=("Courier New", 9),
                                  bg=CARD, fg=MUTED)
        self.g_info.pack(side="right", padx=8)

        # --- Barre de timer (canvas pour animation fluide) ---
        self.timer_canvas = tk.Canvas(s, height=5, bg=CARD, highlightthickness=0)
        self.timer_canvas.pack(fill="x")
        self.timer_bar = self.timer_canvas.create_rectangle(
            0, 0, 0, 5, fill=ACCENT, outline="")

        # --- Carte du mot à traduire ---
        word_card = tk.Frame(s, bg=CARD, highlightthickness=1,
                             highlightbackground=BORDER)
        word_card.pack(fill="x", padx=50, pady=(20, 8))

        tk.Label(word_card, text="TRADUIS CE MOT EN FRANCAIS",
                 font=("Courier New", 9), bg=CARD, fg=MUTED).pack(pady=(14, 6))

        self.g_word = tk.Label(word_card, text="",
                                font=("Georgia", 30, "bold italic"),
                                bg=CARD, fg=TEXT, wraplength=600)
        self.g_word.pack(pady=(0, 4))

        self.g_lang_tag = tk.Label(word_card, text="",
                                    font=("Courier New", 9), bg=CARD, fg=ACCENT2)
        self.g_lang_tag.pack(pady=(0, 14))

        # --- Affichage du timer en secondes ---
        self.g_timer_lbl = tk.Label(s, text="", font=("Courier New", 16, "bold"),
                                     bg=BG, fg=ACCENT)
        self.g_timer_lbl.pack(pady=(4, 0))

        # --- Grille de 4 choix de réponse ---
        choices_f = tk.Frame(s, bg=BG)
        choices_f.pack(fill="x", padx=50, pady=12)

        self._choice_buttons = []
        for i in range(4):
            r, c = divmod(i, 2)
            btn = StyledButton(choices_f, text="",
                               font=("Courier New", 12),
                               bg=CARD2, fg=TEXT,
                               hover_bg=CARD3, hover_fg=ACCENT2,
                               padx=0, pady=14,
                               wraplength=280,
                               justify="center",
                               command=lambda idx=i: self._check_answer(idx))
            btn.grid(row=r, column=c, padx=8, pady=6, sticky="ew")
            choices_f.columnconfigure(c, weight=1)
            self._choice_buttons.append(btn)

        # --- Label de feedback (Correct ! / Mauvaise réponse) ---
        self.g_feedback = tk.Label(s, text="", font=("Georgia", 16, "bold"),
                                    bg=BG, fg=SUCCESS)
        self.g_feedback.pack(pady=4)

        # --- Barre de progression en bas ---
        prog_f = tk.Frame(s, bg=BG)
        prog_f.pack(side="bottom", fill="x", padx=50, pady=12)

        tk.Label(prog_f, text="PROGRESSION",
                 font=("Courier New", 8), bg=BG, fg=MUTED).pack(anchor="w")

        self.prog_canvas = tk.Canvas(prog_f, height=6, bg=CARD2,
                                      highlightthickness=0)
        self.prog_canvas.pack(fill="x", pady=4)
        self.prog_bar = self.prog_canvas.create_rectangle(
            0, 0, 0, 6, fill=SUCCESS, outline="")

    #  résultat

    def _build_result_screen(self):
        s = self.screens["result"]

        tk.Frame(s, bg=ACCENT, height=3).pack(fill="x")

        center = tk.Frame(s, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        self.res_title = tk.Label(center, text="",
                                   font=("Georgia", 40, "bold"),
                                   bg=BG, fg=TEXT)
        self.res_title.pack(pady=(0, 4))

        self.res_sub = tk.Label(center, text="",
                                 font=("Courier New", 11), bg=BG, fg=MUTED)
        self.res_sub.pack(pady=(0, 20))

        Divider(center, color=BORDER).pack(fill="x", pady=10)

        # Grille de statistiques
        stats_f = tk.Frame(center, bg=CARD, highlightthickness=1,
                           highlightbackground=BORDER)
        stats_f.pack(ipadx=10, ipady=10, pady=10)

        self._res_labels = {}
        stat_defs = [
            ("score",   "Score de la partie",    ACCENT2),
            ("record",  "Meilleur score",        GOLD),
            ("correct", "Bonnes reponses",       SUCCESS),
            ("combo",   "Meilleur combo",        GOLD),
            ("lives",   "Vies restantes",        DANGER),
        ]

        for i, (key, label, color) in enumerate(stat_defs):
            r, c = divmod(i, 2)
            box = tk.Frame(stats_f, bg=CARD2)
            box.grid(row=r, column=c, padx=8, pady=6, sticky="ew", ipadx=12, ipady=8)
            stats_f.columnconfigure(c, weight=1)

            tk.Label(box, text=label, font=("Courier New", 9),
                     bg=CARD2, fg=MUTED).pack()
            lv = tk.Label(box, text="—", font=("Georgia", 20, "bold"),
                          bg=CARD2, fg=color)
            lv.pack()
            self._res_labels[key] = lv

        # Message nouveau record
        self.res_record_msg = tk.Label(center, text="",
                                        font=("Georgia", 13, "bold italic"),
                                        bg=BG, fg=GOLD)
        self.res_record_msg.pack(pady=(4, 10))

        # Boutons
        btn_row = tk.Frame(center, bg=BG)
        btn_row.pack(pady=10)

        StyledButton(btn_row, text="REJOUER",
                     font=("Courier New", 11, "bold"),
                     bg=ACCENT, fg="white",
                     hover_bg=ACCENT2, hover_fg="white",
                     padx=24, pady=12,
                     command=self._start_game).pack(side="left", padx=8)

        StyledButton(btn_row, text="MENU PRINCIPAL",
                     font=("Courier New", 11, "bold"),
                     bg=CARD2, fg=TEXT,
                     hover_bg=CARD3, hover_fg=ACCENT2,
                     padx=24, pady=12,
                     command=lambda: self.show("menu")).pack(side="left", padx=8)

    #  LOGIQUE DE JEU

    def _start_game(self):
        """Initialise et démarre une nouvelle partie."""
        # Réinitialisation complète de l'état
        self.score      = 0
        self.combo      = 0
        self.max_combo  = 0
        self.lives      = MAX_LIVES
        self.question_n = 0
        self.correct_n  = 0
        self.answered   = False

        lang = self.language.get()
        diff = self.difficulty.get()
        pool = LANGUAGES[lang][diff]

        # Sélectionner et mélanger les questions
        self.questions = random.sample(pool, min(TOTAL_QUESTIONS, len(pool)))
        if len(self.questions) < TOTAL_QUESTIONS:
            extra = random.choices(pool, k=TOTAL_QUESTIONS - len(self.questions))
            self.questions += extra
        random.shuffle(self.questions)

        self.g_info.configure(text=f"{lang}  |  {diff}")
        self.show("game")
        self._next_question()

    def _next_question(self):
        """Passe à la question suivante ou termine la partie."""
        # Annuler le timer précédent
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        self.answered = False
        self.g_feedback.configure(text="")

        # Réactiver et réinitialiser les boutons de réponse
        for btn in self._choice_buttons:
            btn.configure(bg=CARD2, fg=TEXT, state="normal",
                          activebackground=CARD3)

        # Fin de partie : toutes les questions épuisées
        if self.question_n >= TOTAL_QUESTIONS:
            self._end_game(victory=True)
            return

        self.question_n += 1

        # Mise à jour des indicateurs
        self.g_qcount.configure(text=f"Q {self.question_n}/{TOTAL_QUESTIONS}")
        self._update_lives_display()
        self._update_score_display()
        self._update_progress()

        # Question courante
        word_src, word_fr = self.questions[self.question_n - 1]
        self.current_q = (word_src, word_fr)

        lang = self.language.get()
        self.g_word.configure(text=word_src)
        self.g_lang_tag.configure(text=f"EN {lang.upper()}")

        # Générer 3 mauvaises réponses + la bonne
        diff = self.difficulty.get()
        all_words = [w[1] for w in LANGUAGES[lang][diff] if w[0] != word_src]
        wrongs = random.sample(all_words, min(3, len(all_words)))
        choices = wrongs + [word_fr]
        random.shuffle(choices)

        self.correct_idx = choices.index(word_fr)

        for i, btn in enumerate(self._choice_buttons):
            btn.configure(text=choices[i], bg=CARD2, fg=TEXT)

        # Démarrer le timer
        self.timer_val = TIMER[self.difficulty.get()]
        self._tick_timer()

    def _tick_timer(self):
        """Décrémente le timer chaque seconde et met à jour la barre visuelle."""
        self.g_timer_lbl.configure(text=f"{self.timer_val}s")

        total = TIMER[self.difficulty.get()]
        ratio = self.timer_val / total

        self.timer_canvas.update_idletasks()
        w = self.timer_canvas.winfo_width()
        bar_w = int(w * ratio)

        # Couleur dynamique selon le temps restant
        color = SUCCESS if ratio > 0.5 else (GOLD if ratio > 0.25 else DANGER)
        self.timer_canvas.itemconfig(self.timer_bar, fill=color)
        self.timer_canvas.coords(self.timer_bar, 0, 0, bar_w, 5)

        if self.timer_val <= 0:
            self._time_up()
            return

        self.timer_val -= 1
        self._timer_job = self.after(1000, self._tick_timer)

    def _time_up(self):
        """Le joueur n'a pas répondu à temps."""
        if self.answered:
            return
        self.answered = True

        self.combo = 0
        self.g_combo.configure(text="")
        self.lives -= 1
        self._update_lives_display()

        # Afficher la bonne réponse
        self._choice_buttons[self.correct_idx].configure(bg=SUCCESS2, fg="white")
        self.g_feedback.configure(text="Temps ecoule !", fg=DANGER)

        if self.lives <= 0:
            self.after(1400, lambda: self._end_game(victory=False))
        else:
            self.after(1500, self._next_question)

    def _check_answer(self, idx: int):
        """Vérifie si la réponse choisie est correcte."""
        if self.answered:
            return
        self.answered = True

        # Stopper le timer
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None
        self.timer_canvas.coords(self.timer_bar, 0, 0, 0, 5)
        self.g_timer_lbl.configure(text="")

        # Désactiver tous les boutons
        for btn in self._choice_buttons:
            btn.configure(state="disabled")

        if idx == self.correct_idx:
            # --- Bonne réponse ---
            pts = POINTS[self.difficulty.get()]
            self.combo += 1

            if self.combo > 1:
                bonus = (self.combo - 1) * COMBO_BONUS
                pts  += bonus
                self.g_combo.configure(
                    text=f"COMBO x{self.combo}  +{bonus} bonus", fg=GOLD)
            else:
                self.g_combo.configure(text="")

            if self.combo > self.max_combo:
                self.max_combo = self.combo

            self.score    += pts
            self.correct_n += 1

            self._choice_buttons[idx].configure(bg=SUCCESS2, fg="white")
            self.g_feedback.configure(text=f"Correct !  +{pts} pts", fg=SUCCESS)

            self._update_score_display()
            self.after(1000, self._next_question)

        else:
            # --- Mauvaise réponse ---
            self.combo = 0
            self.g_combo.configure(text="")
            self.lives -= 1
            self._update_lives_display()

            self._choice_buttons[idx].configure(bg=DANGER, fg="white")
            self._choice_buttons[self.correct_idx].configure(bg=SUCCESS2, fg="white")
            self.g_feedback.configure(text="Mauvaise reponse...", fg=DANGER)

            if self.lives <= 0:
                self.after(1400, lambda: self._end_game(victory=False))
            else:
                self.after(1500, self._next_question)

    def _end_game(self, victory: bool):
        """Termine la partie, sauvegarde les stats et affiche l'écran résultat."""
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        # --- Mise à jour du profil utilisateur ---
        old_record = self.current_profile.get("high_score", 0)
        new_record = self.score > old_record

        self.current_profile["total_games"]  = self.current_profile.get("total_games", 0) + 1
        self.current_profile["total_points"] = self.current_profile.get("total_points", 0) + self.score

        if victory:
            self.current_profile["total_wins"] = self.current_profile.get("total_wins", 0) + 1

        if new_record:
            self.current_profile["high_score"] = self.score

        DataManager.update_user(self.current_user, self.current_profile)

        # --- Affichage des résultats ---
        if victory:
            self.res_title.configure(text="Victoire !", fg=SUCCESS)
            self.res_sub.configure(text="Toutes les questions reussies — bien joue !")
        else:
            self.res_title.configure(text="Game Over", fg=DANGER)
            self.res_sub.configure(text="Vous avez perdu toutes vos vies.")

        self._res_labels["score"].configure(text=f"{self.score} pts")
        self._res_labels["record"].configure(
            text=f"{self.current_profile['high_score']} pts")
        self._res_labels["correct"].configure(
            text=f"{self.correct_n} / {self.question_n}")
        self._res_labels["combo"].configure(text=f"x{self.max_combo}")
        self._res_labels["lives"].configure(text=str(self.lives))

        if new_record:
            self.res_record_msg.configure(
                text="** Nouveau record personnel ! **")
        else:
            self.res_record_msg.configure(text="")

        self.show("result")

    #  Mises à jour des éléments de l'interface en jeu

    def _update_lives_display(self):
        """Affiche les vies sous forme de barres."""
        full  = "|" * self.lives
        empty = "." * (MAX_LIVES - self.lives)
        color = DANGER if self.lives == 1 else TEXT
        self.g_lives.configure(
            text=f"[{full}{empty}]  {self.lives}/{MAX_LIVES}", fg=color)

    def _update_score_display(self):
        """Met à jour l'affichage du score."""
        self.g_score.configure(text=f"{self.score} pts")

    def _update_progress(self):
        """Met à jour la barre de progression des questions."""
        self.prog_canvas.update_idletasks()
        w = self.prog_canvas.winfo_width()
        ratio = (self.question_n - 1) / TOTAL_QUESTIONS
        self.prog_canvas.coords(self.prog_bar, 0, 0, int(w * ratio), 6)


    # Construction d'UI réutilisable


    def _make_header(self, screen: tk.Frame, title: str, back_screen: str):
        """Crée un en-tête standard avec titre et bouton retour."""
        tk.Frame(screen, bg=ACCENT, height=3).pack(fill="x")

        header = tk.Frame(screen, bg=CARD, pady=10)
        header.pack(fill="x")

        StyledButton(header, text="< Retour",
                     font=("Courier New", 9), bg=CARD, fg=MUTED,
                     hover_bg=CARD, hover_fg=ACCENT2,
                     padx=10, pady=4,
                     command=lambda: self.show(back_screen)).pack(side="left", padx=16)

        tk.Label(header, text=title,
                 font=("Courier New", 12, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=10)

        Divider(screen, color=BORDER).pack(fill="x")



# Lancement du jeu

if __name__ == "__main__":
    app = (Fluently())
    app.mainloop()
