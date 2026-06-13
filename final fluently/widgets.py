import tkinter as tk
import config.config as cfg


class StyledButton(tk.Button):
    """Bouton personnalisé avec effets de survol intégrés."""

    def __init__(self, parent, hover_bg=None, hover_fg="white", **kwargs):
        if hover_bg is None:
            hover_bg = cfg.ACCENT2
        self._normal_bg = kwargs.get("bg", cfg.CARD2)
        self._normal_fg = kwargs.get("fg", cfg.TEXT)
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg

        super().__init__(parent, **kwargs)
        self.configure(relief="flat", bd=0, cursor="hand2", activebackground=hover_bg, activeforeground=hover_fg)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        self.configure(bg=self._hover_bg, fg=self._hover_fg)

    def _on_leave(self, _event):
        self.configure(bg=self._normal_bg, fg=self._normal_fg)



class StyledEntry(tk.Frame):
    """Champ de saisi stylisé avec label intégré et bordure coloréer."""

    def __init__(self, parent, label="", show="", **kwargs):
        super().__init__(parent, bg=cfg.CARD, highlightthickness=1,
                         highlightbackground=cfg.BORDER)

        if label:
            tk.Label(self, text=label, font=("Courier New", 9),
                      bg=cfg.CARD, fg=cfg.MUTED).pack(anchor="w", padx=10, pady=(8, 0))

        self.entry = tk.Entry(self, show=show,
                               font=("Courier New", 12),
                               bg=cfg.CARD, fg=cfg.TEXT, insertbackground=cfg.ACCENT,
                               relief="flat", bd=0)
        self.entry.pack(fill="x", padx=10, pady=(2, 10))

        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def _focus_in(self, _event):
        self.configure(highlightbackground=cfg.ACCENT)

    def _focus_out(self, _event):
        self.configure(highlightbackground=cfg.BORDER)

    def get(self) -> str:
        return self.entry.get()

    def clear(self):
        self.entry.delete(0, tk.END)

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class Divider(tk.Frame):
    """Ligne de séparation horizontale."""

    def __init__(self, parent, color=None, **kwargs):
        def __init__(self, parent, color=None, **kwargs):
            if color is None:
                color = cfg.BORDER
        super().__init__(parent, bg=color, height=1, **kwargs)


class StarRating(tk.Frame):
    """Widget de notation par étoiles (1 à 5)."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=cfg.CARD, **kwargs)
        self.rating = tk.IntVar(value=0)
        self._stars = []
        for i in range(1, 6):
            btn = tk.Button(self, text="*", font=("Georgia", 18),
                            bg=cfg.CARD, fg=cfg.MUTED, relief="flat", bd=0,
                            cursor="hand2",
                            command=lambda v=i: self._set_rating(v))
            btn.pack(side="left", padx=2)
            self._stars.append(btn)

    def _set_rating(self, value: int):
        self.rating.set(value)
        for i, btn in enumerate(self._stars):
            btn.configure(fg=cfg.GOLD if i < value else cfg.MUTED)

    def get(self) -> int:
        return self.rating.get()
