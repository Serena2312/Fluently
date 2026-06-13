import tkinter as tk
from widgets import StyledButton, Divider
from config.config import BG, CARD, CARD2, ACCENT, ACCENT2, SUCCESS, DANGER, GOLD, BORDER, MUTED, TEXT


class ResultScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
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

        self.res_record_msg = tk.Label(center, text="",
                                        font=("Georgia", 13, "bold italic"),
                                        bg=BG, fg=GOLD)
        self.res_record_msg.pack(pady=(4, 10))

        btn_row = tk.Frame(center, bg=BG)
        btn_row.pack(pady=10)

        StyledButton(btn_row, text="REJOUER",
                     font=("Courier New", 11, "bold"),
                     bg=ACCENT, fg="white",
                     hover_bg=ACCENT2, hover_fg="white",
                     padx=24, pady=12,
                     command=self.app._start_game).pack(side="left", padx=8)

        StyledButton(btn_row, text="MENU PRINCIPAL",
                     font=("Courier New", 11, "bold"),
                     bg=CARD2, fg=TEXT,
                     hover_bg=CARD2, hover_fg=ACCENT2,
                     padx=24, pady=12,
                     command=lambda: self.app.show("menu")).pack(side="left", padx=8)