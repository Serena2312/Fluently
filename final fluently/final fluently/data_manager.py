import json
import os
import hashlib
import datetime


class DataManager:
    """
    Gère toutes les opérations de lecture et d'écriture des données utilisateurs.
    Les données sont stockées dans le fichier 'users.json'.
    """

    FILE = "users.json"

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def load() -> dict:
        if not os.path.exists(DataManager.FILE):
            return {}
        try:
            with open(DataManager.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    @staticmethod
    def save(data: dict) -> None:
        with open(DataManager.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def register(username: str, password: str) -> tuple:
        if not username.strip() or not password.strip():
            return False, "Les champs ne peuvent pas etre vides."
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit faire au moins 3 caracteres."
        if len(password) < 4:
            return False, "Le mot de passe doit faire au moins 4 caracteres."

        data = DataManager.load()
        if username in data:
            return False, "Ce nom d'utilisateur est deja utilise."

        data[username] = {
            "password":     DataManager._hash_password(password),
            "created_at":   datetime.datetime.now().strftime("%d/%m/%Y"),
            "high_score":   0,
            "total_games":  0,
            "total_wins":   0,
            "total_points": 0,
            "comments":     [],
        }
        DataManager.save(data)
        return True, "Inscription reussie !"

    @staticmethod
    def login(username: str, password: str) -> tuple:
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
        data = DataManager.load()
        data[username] = profile
        DataManager.save(data)

    @staticmethod
    def get_all_comments() -> list:
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
        all_comments.sort(key=lambda c: c["date"], reverse=True)
        return all_comments

    @staticmethod
    def get_leaderboard() -> list:
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