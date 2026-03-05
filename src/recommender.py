import csv
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    name: str
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_acousticness: float
    target_valence: float
    target_danceability: float

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            row["energy"] = float(row["energy"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def _genre_match(song_genre: str, user_genre: str) -> float:
    """Return 1.0 for exact genre match, 0.5 for partial overlap, 0.0 for no match."""
    if song_genre == user_genre:
        return 1.0
    if user_genre in song_genre or song_genre in user_genre:
        return 0.5
    return 0.0


def _proximity(song_val: float, user_target: float, sigma: float = 0.15) -> float:
    """Return a Gaussian proximity score (0.0–1.0) that peaks at 1.0 when song_val equals user_target."""
    return math.exp(-((song_val - user_target) ** 2) / (2 * sigma ** 2))


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    results = []
    for song in songs:
        genre_s = _genre_match(song["genre"], user_prefs["favorite_genre"])
        mood_s = 1.0 if song["mood"] == user_prefs["favorite_mood"] else 0.0
        energy_s = _proximity(song["energy"], user_prefs["target_energy"])
        valence_s = _proximity(song["valence"], user_prefs["target_valence"])
        dance_s = _proximity(song["danceability"], user_prefs["target_danceability"])
        acoustic_s = _proximity(song["acousticness"], user_prefs["target_acousticness"])

        score = (
            0.30 * genre_s
            + 0.25 * mood_s
            + 0.20 * energy_s
            + 0.10 * valence_s
            + 0.10 * dance_s
            + 0.05 * acoustic_s
        )

        reasons = []
        if genre_s == 1.0:
            reasons.append(f"genre match: {song['genre']} (+{0.30 * genre_s:.2f})")
        elif genre_s == 0.5:
            reasons.append(f"partial genre match: {song['genre']} ~ {user_prefs['favorite_genre']} (+{0.30 * genre_s:.2f})")
        else:
            reasons.append(f"genre mismatch: {song['genre']} (+0.00)")

        if mood_s == 1.0:
            reasons.append(f"mood match: {song['mood']} (+{0.25:.2f})")
        else:
            reasons.append(f"mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (+0.00)")

        reasons.append(f"energy {song['energy']} vs target {user_prefs['target_energy']} (+{0.20 * energy_s:.2f})")
        reasons.append(f"valence {song['valence']} vs target {user_prefs['target_valence']} (+{0.10 * valence_s:.2f})")
        reasons.append(f"danceability {song['danceability']} vs target {user_prefs['target_danceability']} (+{0.10 * dance_s:.2f})")
        reasons.append(f"acousticness {song['acousticness']} vs target {user_prefs['target_acousticness']} (+{0.05 * acoustic_s:.2f})")

        explanation = " | ".join(reasons)
        results.append((song, score, explanation))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]
