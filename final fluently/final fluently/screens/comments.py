import tkinter as tk
from tkinter import messagebox
import datetime
from widgets import StyledButton, StarRating, Divider
from data_manager import DataManager
from config.config import BG, CARD, CARD2, ACCENT, ACCENT2, BORDER, MUTED, TEXT, GOLD


class CommentsScreen:
    def __init__(self, parent_frame, app):
        self.app = app
        self._build(parent_frame)

    def _build(self, s):
        self._make_header(s, "COMMENTAIRES & AVIS", back_screen="menu")

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

        list_f = tk.Frame(s, bg=BG)
        list_f.pack(fill="both", expand=True, padx=40, pady=10)

        tk.Label(list_f, text="TOUS LES AVIS",
                 font=("Courier New", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w")

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

        comment = {
            "text":   text,
            "date":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "rating": rating,
        }
        if "comments" not in self.app.current_profile:
            self.app.current_profile["comments"] = []
        self.app.current_profile["comments"].append(comment)
        DataManager.update_user(self.app.current_user, self.app.current_profile)

        self.comment_entry.delete("1.0", "end")
        self.star_rating._set_rating(0)
        self.refresh()

    def refresh(self):
        for widget in self.comments_inner.winfo_children():
            widget.destroy()

        all_comments = DataManager.get_all_comments()

        if not all_comments:
            tk.Label(self.comments_inner,
                     text="Aucun commentaire pour l'instant. Soyez le premier !",
                     font=("Courier New", 10), bg=BG, fg=MUTED).pack(pady=20)
            return

        for comment in all_comments:
            card = tk.Frame(self.comments_inner, bg=CARD,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(fill="x", pady=4, padx=2)

            top = tk.Frame(card, bg=CARD)
            top.pack(fill="x", padx=14, pady=(10, 4))

            is_me = comment["author"] == self.app.current_user
            author_color = ACCENT2 if is_me else TEXT
            tk.Label(top, text=comment["author"] + (" (moi)" if is_me else ""),
                     font=("Courier New", 10, "bold"),
                     bg=CARD, fg=author_color).pack(side="left")

            stars = "*" * comment["rating"] + "-" * (5 - comment["rating"])
            tk.Label(top, text=stars, font=("Georgia", 11),
                     bg=CARD, fg=GOLD).pack(side="left", padx=10)

            tk.Label(top, text=comment["date"],
                     font=("Courier New", 8), bg=CARD, fg=MUTED).pack(side="right")

            tk.Label(card, text=comment["text"],
                     font=("Courier New", 10), bg=CARD, fg=TEXT,
                     wraplength=640, justify="left", anchor="w").pack(
                         fill="x", padx=14, pady=(0, 12))

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