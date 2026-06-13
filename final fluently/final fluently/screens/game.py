import tkinter as tk
from widgets import StyledButton
from config.config import (BG, CARD, CARD2, CARD3, ACCENT, ACCENT2,
                            SUCCESS, SUCCESS2, DANGER, GOLD, MUTED, TEXT,
                            POINTS, TIMER, TOTAL_QUESTIONS, MAX_LIVES)


class GameScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
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

        # --- Barre de timer ---
        self.timer_canvas = tk.Canvas(s, height=5, bg=CARD, highlightthickness=0)
        self.timer_canvas.pack(fill="x")
        self.timer_bar = self.timer_canvas.create_rectangle(
            0, 0, 0, 5, fill=ACCENT, outline="")

        # --- Carte du mot ---
        word_card = tk.Frame(s, bg=CARD, highlightthickness=1,
                             highlightbackground=ACCENT2)
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

        # --- Timer en secondes ---
        self.g_timer_lbl = tk.Label(s, text="", font=("Courier New", 16, "bold"),
                                     bg=BG, fg=ACCENT)
        self.g_timer_lbl.pack(pady=(4, 0))

        # --- Grille de 4 choix ---
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
                               command=lambda idx=i: self.app._check_answer(idx))
            btn.grid(row=r, column=c, padx=8, pady=6, sticky="ew")
            choices_f.columnconfigure(c, weight=1)
            self._choice_buttons.append(btn)

        # --- Feedback ---
        self.g_feedback = tk.Label(s, text="", font=("Georgia", 16, "bold"),
                                    bg=BG, fg=SUCCESS)
        self.g_feedback.pack(pady=4)

        # --- Barre de progression ---
        prog_f = tk.Frame(s, bg=BG)
        prog_f.pack(side="bottom", fill="x", padx=50, pady=12)

        tk.Label(prog_f, text="PROGRESSION",
                 font=("Courier New", 8), bg=BG, fg=MUTED).pack(anchor="w")

        self.prog_canvas = tk.Canvas(prog_f, height=6, bg=CARD2,
                                      highlightthickness=0)
        self.prog_canvas.pack(fill="x", pady=4)
        self.prog_bar = self.prog_canvas.create_rectangle(
            0, 0, 0, 6, fill=SUCCESS, outline="")