import tkinter as tk
from widgets import StyledButton, Divider
from config.config import BG, CARD, CARD2, ACCENT, ACCENT2, BORDER, MUTED, TEXT, GOLD, SUCCESS


class ProfileScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
        self._make_header(s, "MON PROFIL", back_screen="menu")

        content = tk.Frame(s, bg=BG)
        content.pack(fill="both", expand=True, padx=60, pady=20)

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

    def refresh(self):
        if not self.app.current_profile:
            return
        initial = self.app.current_user[0].upper() if self.app.current_user else "?"
        self.prof_avatar.configure(text=initial)
        self.prof_name.configure(text=self.app.current_user)
        self.prof_since.configure(
            text=f"Membre depuis le {self.app.current_profile.get('created_at', '?')}")

        for key, label_widget in self._prof_stat_labels.items():
            val = self.app.current_profile.get(key, 0)
            suffix = " pts" if "score" in key or "points" in key else ""
            label_widget.configure(text=f"{val}{suffix}")

    def _make_header(self, screen, title: str, back_screen: str):
        tk.Frame(screen, bg=ACCENT, height=3).pack(fill="x")
        header = tk.Frame(screen, bg=CARD, pady=10)
        header.pack(fill="x")
        StyledButton(header, text="< Retour",
                     font=("Courier New", 9), bg=CARD, fg=MUTED,
                     hover_bg=CARD, hover_fg=ACCENT2,
                     padx=10, pady=4,
                     command=lambda: self.app.show(back_screen)).pack(side="left", padx=16)
        tk.Label(header, text=title, font=("Courier New", 12, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=10)
        Divider(screen, color=BORDER).pack(fill="x")