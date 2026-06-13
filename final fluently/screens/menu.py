import tkinter as tk
from widgets import StyledButton, Divider
from config.config import BG, CARD, CARD2, CARD3, ACCENT, ACCENT2, DANGER, BORDER, MUTED, TEXT, POINTS, TIMER
from config.Traductions import LANGUAGES


class MenuScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
        header = tk.Frame(s, bg=CARD, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="Fluently",
                 font=("Georgia", 16, "bold italic"), bg=CARD, fg=ACCENT2).pack(side="left", padx=20)

        StyledButton(header, text="Deconnexion",
                     font=("Courier New", 9), bg=CARD, fg=MUTED,
                     hover_bg=CARD, hover_fg=DANGER,
                     padx=10, pady=4,
                     command=self.app._do_logout).pack(side="right", padx=20)

        Divider(s, color=BORDER).pack(fill="x")

        main = tk.Frame(s, bg=BG)
        main.pack(fill="both", expand=True, padx=60, pady=20)

        self.menu_welcome = tk.Label(main, text="",
                                      font=("Georgia", 22, "bold"), bg=BG, fg=TEXT)
        self.menu_welcome.pack(anchor="w", pady=(0, 4))

        self.menu_sub = tk.Label(main, text="",
                                  font=("Courier New", 10), bg=BG, fg=MUTED)
        self.menu_sub.pack(anchor="w", pady=(0, 20))

        Divider(main).pack(fill="x", pady=10)

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

        Divider(main).pack(fill="x", pady=10)

        nav_grid = tk.Frame(main, bg=BG)
        nav_grid.pack(fill="x", pady=10)

        play_btn = StyledButton(nav_grid, text="JOUER",
                                font=("Courier New", 14, "bold"),
                                bg=ACCENT, fg="white",
                                hover_bg=ACCENT2, hover_fg="white",
                                padx=40, pady=16,
                                command=self.app._start_game)
        play_btn.grid(row=0, column=0, rowspan=2, padx=(0, 12), pady=4, sticky="ns")

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
                         command=lambda sc=screen: self.app.show(sc)).grid(
                             row=i // 2, column=1 + i % 2,
                             padx=4, pady=4, sticky="ew")

        for c in range(3):
            nav_grid.columnconfigure(c, weight=1 if c > 0 else 2)

        self.menu_score_label = tk.Label(main, text="",
                                          font=("Courier New", 10), bg=BG, fg=MUTED)
        self.menu_score_label.pack(anchor="w", pady=(16, 0))

    def refresh(self):
        if not self.app.current_user:
            return
        self.menu_welcome.configure(
            text=f"Bonjour, {self.app.current_user} !")
        self.menu_sub.configure(
            text=f"Membre depuis le {self.app.current_profile.get('created_at', '?')}  |  "
                 f"{self.app.current_profile.get('total_games', 0)} parties jouees")
        self.menu_score_label.configure(
            text=f"Meilleur score personnel : {self.app.current_profile.get('high_score', 0)} pts")

    def _select_lang(self, lang: str):
        self.app.language.set(lang)
        for l, b in self._lang_buttons.items():
            b.configure(bg=ACCENT if l == lang else CARD2,
                        fg="white" if l == lang else MUTED)

    def _select_diff(self, diff: str):
        self.app.difficulty.set(diff)
        for d, b in self._diff_buttons.items():
            b.configure(bg=ACCENT if d == diff else CARD2,
                        fg="white" if d == diff else MUTED)