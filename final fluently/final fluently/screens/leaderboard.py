import tkinter as tk
from widgets import StyledButton, Divider
from data_manager import DataManager
from config.config import BG, CARD, CARD2, ACCENT, ACCENT2, BORDER, MUTED, TEXT, GOLD


class LeaderboardScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
        self._make_header(s, "CLASSEMENT", back_screen="menu")

        content = tk.Frame(s, bg=BG)
        content.pack(fill="both", expand=True, padx=60, pady=10)

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

        self.leaderboard_frame = tk.Frame(content, bg=BG)
        self.leaderboard_frame.pack(fill="both", expand=True)

    def refresh(self):
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
            is_me = entry["username"] == self.app.current_user
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