import tkinter as tk
import random

from data_manager import DataManager
from config.config import (BG, CARD, ACCENT, ACCENT2, SUCCESS, SUCCESS2,
                            DANGER, GOLD, MUTED, TEXT,
                            POINTS, TIMER, COMBO_BONUS, TOTAL_QUESTIONS, MAX_LIVES)
from config.Traductions import LANGUAGES

from screens.login       import LoginScreen
from screens.signup      import SignupScreen
from screens.menu        import MenuScreen
from screens.profile     import ProfileScreen
from screens.leaderboard import LeaderboardScreen
from screens.comments    import CommentsScreen
from screens.game        import GameScreen
from screens.result      import ResultScreen


class Fluently(tk.Tk):
    """
    Classe principale : gère la navigation entre les écrans
    et l'état global de la session (utilisateur, variables de jeu).
    """

    def __init__(self):
        super().__init__()

        self.title("Fluently — Apprends les langues")
        self.geometry("840x680")
        self.minsize(760, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        # --- Session ---
        self.current_user    = None
        self.current_profile = None

        # --- Variables de jeu ---
        self.language   = tk.StringVar(value="Anglais")
        self.difficulty = tk.StringVar(value="Facile")
        self.score      = 0
        self.combo      = 0
        self.max_combo  = 0
        self.lives      = MAX_LIVES
        self.question_n = 0
        self.correct_n  = 0
        self.questions  = []
        self.current_q  = None
        self.answered   = False
        self.timer_val  = 0
        self._timer_job = None

        self._build_all_screens()
        self.show("login")

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def show(self, name: str):
        """Affiche l'écran demandé et appelle refresh() si disponible."""
        self.screens[name].lift()
        screen_obj = self.screen_objects.get(name)
        if screen_obj and hasattr(screen_obj, "refresh"):
            screen_obj.refresh()

    # ------------------------------------------------------------------ #
    #  Construction de tous les écrans                                     #
    # ------------------------------------------------------------------ #

    def _build_all_screens(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)

        self.screens       = {}
        self.screen_objects = {}

        screen_defs = [
            ("login",       LoginScreen),
            ("signup",      SignupScreen),
            ("menu",        MenuScreen),
            ("profile",     ProfileScreen),
            ("leaderboard", LeaderboardScreen),
            ("comments",    CommentsScreen),
            ("game",        GameScreen),
            ("result",      ResultScreen),
        ]

        for name, ScreenClass in screen_defs:
            frame = tk.Frame(container, bg=BG)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.screens[name]        = frame
            self.screen_objects[name] = ScreenClass(frame, self)

    # ------------------------------------------------------------------ #
    #  Authentification                                                    #
    # ------------------------------------------------------------------ #

    def _do_logout(self):
        self.current_user    = None
        self.current_profile = None
        self.show("login")

    # ------------------------------------------------------------------ #
    #  Logique de jeu                                                      #
    # ------------------------------------------------------------------ #

    def _start_game(self):
        """Initialise et démarre une nouvelle partie."""
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

        self.questions = random.sample(pool, min(TOTAL_QUESTIONS, len(pool)))
        if len(self.questions) < TOTAL_QUESTIONS:
            extra = random.choices(pool, k=TOTAL_QUESTIONS - len(self.questions))
            self.questions += extra
        random.shuffle(self.questions)

        gs = self.screen_objects["game"]
        gs.g_info.configure(text=f"{lang}  |  {diff}")
        self.show("game")
        self._next_question()

    def _next_question(self):
        """Passe à la question suivante ou termine la partie."""
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        self.answered = False
        gs = self.screen_objects["game"]
        gs.g_feedback.configure(text="")

        for btn in gs._choice_buttons:
            btn.configure(bg=CARD, fg=TEXT, state="normal",
                          activebackground=CARD)

        if self.question_n >= TOTAL_QUESTIONS:
            self._end_game(victory=True)
            return

        self.question_n += 1
        gs.g_qcount.configure(text=f"Q {self.question_n}/{TOTAL_QUESTIONS}")
        self._update_lives_display()
        self._update_score_display()
        self._update_progress()

        word_src, word_fr = self.questions[self.question_n - 1]
        self.current_q = (word_src, word_fr)

        lang = self.language.get()
        gs.g_word.configure(text=word_src)
        gs.g_lang_tag.configure(text=f"EN {lang.upper()}")

        diff = self.difficulty.get()
        all_words = [w[1] for w in LANGUAGES[lang][diff] if w[0] != word_src]
        wrongs = random.sample(all_words, min(3, len(all_words)))
        choices = wrongs + [word_fr]
        random.shuffle(choices)

        self.correct_idx = choices.index(word_fr)

        for i, btn in enumerate(gs._choice_buttons):
            btn.configure(text=choices[i], bg=CARD, fg=TEXT)

        self.timer_val = TIMER[self.difficulty.get()]
        self._tick_timer()

    def _tick_timer(self):
        gs = self.screen_objects["game"]
        gs.g_timer_lbl.configure(text=f"{self.timer_val}s")

        total = TIMER[self.difficulty.get()]
        ratio = self.timer_val / total

        gs.timer_canvas.update_idletasks()
        w = gs.timer_canvas.winfo_width()
        bar_w = int(w * ratio)

        color = SUCCESS if ratio > 0.5 else (GOLD if ratio > 0.25 else DANGER)
        gs.timer_canvas.itemconfig(gs.timer_bar, fill=color)
        gs.timer_canvas.coords(gs.timer_bar, 0, 0, bar_w, 5)

        if self.timer_val <= 0:
            self._time_up()
            return

        self.timer_val -= 1
        self._timer_job = self.after(1000, self._tick_timer)

    def _time_up(self):
        if self.answered:
            return
        self.answered = True

        self.combo = 0
        gs = self.screen_objects["game"]
        gs.g_combo.configure(text="")
        self.lives -= 1
        self._update_lives_display()

        gs._choice_buttons[self.correct_idx].configure(bg=SUCCESS2, fg="white")
        gs.g_feedback.configure(text="Temps ecoule !", fg=DANGER)

        if self.lives <= 0:
            self.after(1400, lambda: self._end_game(victory=False))
        else:
            self.after(1500, self._next_question)

    def _check_answer(self, idx: int):
        if self.answered:
            return
        self.answered = True

        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        gs = self.screen_objects["game"]
        gs.timer_canvas.coords(gs.timer_bar, 0, 0, 0, 5)
        gs.g_timer_lbl.configure(text="")

        for btn in gs._choice_buttons:
            btn.configure(state="disabled")

        if idx == self.correct_idx:
            pts = POINTS[self.difficulty.get()]
            self.combo += 1

            if self.combo > 1:
                bonus = (self.combo - 1) * COMBO_BONUS
                pts  += bonus
                gs.g_combo.configure(
                    text=f"COMBO x{self.combo}  +{bonus} bonus", fg=GOLD)
            else:
                gs.g_combo.configure(text="")

            if self.combo > self.max_combo:
                self.max_combo = self.combo

            self.score     += pts
            self.correct_n += 1

            gs._choice_buttons[idx].configure(bg=SUCCESS2, fg="white")
            gs.g_feedback.configure(text=f"Correct !  +{pts} pts", fg=SUCCESS)

            self._update_score_display()
            self.after(1000, self._next_question)

        else:
            self.combo = 0
            gs.g_combo.configure(text="")
            self.lives -= 1
            self._update_lives_display()

            gs._choice_buttons[idx].configure(bg=DANGER, fg="white")
            gs._choice_buttons[self.correct_idx].configure(bg=SUCCESS2, fg="white")
            gs.g_feedback.configure(text="Mauvaise reponse...", fg=DANGER)

            if self.lives <= 0:
                self.after(1400, lambda: self._end_game(victory=False))
            else:
                self.after(1500, self._next_question)

    def _end_game(self, victory: bool):
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        old_record = self.current_profile.get("high_score", 0)
        new_record  = self.score > old_record

        self.current_profile["total_games"]  = self.current_profile.get("total_games", 0) + 1
        self.current_profile["total_points"] = self.current_profile.get("total_points", 0) + self.score

        if victory:
            self.current_profile["total_wins"] = self.current_profile.get("total_wins", 0) + 1

        if new_record:
            self.current_profile["high_score"] = self.score

        DataManager.update_user(self.current_user, self.current_profile)

        rs = self.screen_objects["result"]

        if victory:
            rs.res_title.configure(text="Victoire !", fg=SUCCESS)
            rs.res_sub.configure(text="Toutes les questions reussies — bien joue !")
        else:
            rs.res_title.configure(text="Game Over", fg=DANGER)
            rs.res_sub.configure(text="Vous avez perdu toutes vos vies.")

        rs._res_labels["score"].configure(text=f"{self.score} pts")
        rs._res_labels["record"].configure(text=f"{self.current_profile['high_score']} pts")
        rs._res_labels["correct"].configure(text=f"{self.correct_n} / {self.question_n}")
        rs._res_labels["combo"].configure(text=f"x{self.max_combo}")
        rs._res_labels["lives"].configure(text=str(self.lives))

        rs.res_record_msg.configure(
            text="** Nouveau record personnel ! **" if new_record else "")

        self.show("result")

    # ------------------------------------------------------------------ #
    #  Mise à jour des éléments UI de jeu                                 #
    # ------------------------------------------------------------------ #

    def _update_lives_display(self):
        gs = self.screen_objects["game"]
        full  = "|" * self.lives
        empty = "." * (MAX_LIVES - self.lives)
        color = DANGER if self.lives == 1 else TEXT
        gs.g_lives.configure(
            text=f"[{full}{empty}]  {self.lives}/{MAX_LIVES}", fg=color)

    def _update_score_display(self):
        self.screen_objects["game"].g_score.configure(text=f"{self.score} pts")

    def _update_progress(self):
        gs = self.screen_objects["game"]
        gs.prog_canvas.update_idletasks()
        w = gs.prog_canvas.winfo_width()
        ratio = (self.question_n - 1) / TOTAL_QUESTIONS
        gs.prog_canvas.coords(gs.prog_bar, 0, 0, int(w * ratio), 6)