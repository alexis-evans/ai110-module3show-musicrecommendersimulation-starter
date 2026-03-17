import csv
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# ── Scoring Mode Configurations (Strategy Pattern) ───────────────────────────
# Each mode redistributes weights to prioritise different song attributes.
# Switch modes by passing mode="genre-first" | "mood-first" | "energy-focused"
# to recommend_songs() or the Recommender constructor.
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "genre-first": {
        # Heavily rewards genre alignment; good for genre-loyal listeners.
        "genre": 0.40, "mood": 0.10, "mood_tags": 0.10,
        "energy": 0.15, "valence": 0.07, "dance": 0.07,
        "acoustic": 0.04, "popularity": 0.04, "decade": 0.03,
    },
    "mood-first": {
        # Rewards detailed mood-tag overlap; good for emotion-driven listeners.
        "genre": 0.10, "mood": 0.20, "mood_tags": 0.30,
        "energy": 0.15, "valence": 0.08, "dance": 0.07,
        "acoustic": 0.04, "popularity": 0.04, "decade": 0.02,
    },
    "energy-focused": {
        # Rewards energy & danceability; good for workout / party playlists.
        "genre": 0.10, "mood": 0.10, "mood_tags": 0.08,
        "energy": 0.40, "valence": 0.10, "dance": 0.12,
        "acoustic": 0.04, "popularity": 0.04, "decade": 0.02,
    },
}

DEFAULT_MODE = "genre-first"


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
    # Challenge 1 — advanced features
    popularity: int = 50           # 0-100 chart score
    release_decade: int = 2020     # e.g. 1960, 1990, 2010, 2020
    mood_tags: List[str] = field(default_factory=list)  # e.g. ["euphoric","uplifting"]


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
    # Challenge 1 — advanced preferences
    preferred_decade: int = 2020
    preferred_mood_tags: List[str] = field(default_factory=list)


class Recommender:
    """
    OOP wrapper around the recommendation logic (Strategy pattern).
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], mode: str = DEFAULT_MODE):
        self.songs = songs
        self.mode = mode

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        song_dicts = [s.__dict__ for s in self.songs]
        results = recommend_songs(user.__dict__, song_dicts, k, mode=self.mode)
        return [r[0] for r in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        weights = SCORING_MODES.get(self.mode, SCORING_MODES[DEFAULT_MODE])
        _, _, explanation = _score_song(song.__dict__, user.__dict__, weights)
        return explanation


# ── Data Loading ─────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file, including advanced features.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]           = int(row["id"].strip())
            row["tempo_bpm"]    = int(row["tempo_bpm"].strip())
            row["energy"]       = float(row["energy"].strip())
            row["valence"]      = float(row["valence"].strip())
            row["danceability"] = float(row["danceability"].strip())
            row["acousticness"] = float(row["acousticness"].strip())
            row["popularity"]     = int(row.get("popularity", "50").strip())
            row["release_decade"] = int(row.get("release_decade", "2020").strip())
            tags_raw = row.get("mood_tags", "").strip().strip('"')
            row["mood_tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
            row["title"]  = row["title"].strip()
            row["artist"] = row["artist"].strip()
            row["genre"]  = row["genre"].strip()
            row["mood"]   = row["mood"].strip()
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


# ── Scoring Helpers ───────────────────────────────────────────────────────────

def _genre_match(song_genre: str, user_genre: str) -> float:
    """1.0 for exact match, 0.5 for partial overlap, 0.0 for none."""
    if song_genre == user_genre:
        return 1.0
    if user_genre in song_genre or song_genre in user_genre:
        return 0.5
    return 0.0


def _proximity(song_val: float, user_target: float, sigma: float = 0.15) -> float:
    """Gaussian proximity score peaking at 1.0 when song_val == user_target."""
    return math.exp(-((song_val - user_target) ** 2) / (2 * sigma ** 2))


def _decade_score(song_decade: int, preferred_decade: int) -> float:
    """
    Era-proximity score:
      exact decade  → 1.0
      1 decade away → 0.7
      2 decades     → 0.4
      3+ decades    → 0.1
    Encourages songs from the user's preferred musical era.
    """
    gap = abs(song_decade - preferred_decade) // 10
    return [1.0, 0.7, 0.4, 0.1][min(gap, 3)]


def _mood_tags_score(song_tags: List[str], preferred_tags: List[str]) -> float:
    """
    Fraction of the user's preferred mood tags found in the song's tags.
    Each matching tag contributes 1/len(preferred_tags) to the score, capped at 1.0.
    Returns 0.5 (neutral) when the user has no tag preferences.
    """
    if not preferred_tags:
        return 0.5
    matches = sum(1 for t in preferred_tags if t in song_tags)
    return min(matches / len(preferred_tags), 1.0)


def _score_song(
    song: Dict, user_prefs: Dict, weights: Dict[str, float]
) -> Tuple[Dict, float, str]:
    """Compute a weighted score and human-readable explanation for a song."""
    genre_s   = _genre_match(song["genre"], user_prefs["favorite_genre"])
    mood_s    = 1.0 if song["mood"] == user_prefs["favorite_mood"] else 0.0
    tags_s    = _mood_tags_score(
        song.get("mood_tags", []), user_prefs.get("preferred_mood_tags", [])
    )
    energy_s  = _proximity(song["energy"],       user_prefs["target_energy"])
    valence_s = _proximity(song["valence"],      user_prefs["target_valence"])
    dance_s   = _proximity(song["danceability"], user_prefs["target_danceability"])
    acoustic_s = _proximity(song["acousticness"], user_prefs["target_acousticness"])
    pop_s     = song.get("popularity", 50) / 100.0
    decade_s  = _decade_score(
        song.get("release_decade", 2020), user_prefs.get("preferred_decade", 2020)
    )

    w = weights
    score = (
        w["genre"]      * genre_s
        + w["mood"]       * mood_s
        + w["mood_tags"]  * tags_s
        + w["energy"]     * energy_s
        + w["valence"]    * valence_s
        + w["dance"]      * dance_s
        + w["acoustic"]   * acoustic_s
        + w["popularity"] * pop_s
        + w["decade"]     * decade_s
    )

    reasons = []
    if genre_s == 1.0:
        reasons.append(f"genre✓ {song['genre']} (+{w['genre'] * genre_s:.2f})")
    elif genre_s == 0.5:
        reasons.append(f"genre~ {song['genre']} (+{w['genre'] * genre_s:.2f})")
    else:
        reasons.append(f"genre✗ {song['genre']} (+0.00)")

    if mood_s == 1.0:
        reasons.append(f"mood✓ {song['mood']} (+{w['mood']:.2f})")
    else:
        reasons.append(f"mood✗ {song['mood']} (+0.00)")

    matched = [t for t in user_prefs.get("preferred_mood_tags", []) if t in song.get("mood_tags", [])]
    reasons.append(f"tags{matched} (+{w['mood_tags'] * tags_s:.2f})")
    reasons.append(f"energy {song['energy']}→{user_prefs['target_energy']} (+{w['energy'] * energy_s:.2f})")
    reasons.append(f"pop {song.get('popularity', 50)} (+{w['popularity'] * pop_s:.2f})")
    reasons.append(f"decade {song.get('release_decade', 2020)} (+{w['decade'] * decade_s:.2f})")

    return song, score, " | ".join(reasons)


# ── Challenge 3: Diversity & Fairness ────────────────────────────────────────

def _apply_diversity_penalty(
    scored: List[Tuple[Dict, float, str]],
    k: int,
    artist_penalty: float = 0.15,
    genre_penalty: float = 0.10,
    max_per_genre: int = 2,
) -> List[Tuple[Dict, float, str]]:
    """
    Greedy diverse selection that prevents artist/genre monopolies.

    At each step the algorithm picks the highest adjusted-score candidate.
    A candidate's score is penalised if:
      - Its artist already appears in the selected list  → -0.15
      - Its genre already fills the max_per_genre quota  → -0.10

    This ensures variety without completely excluding repeated artists/genres.
    """
    candidates = list(scored)
    selected: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts:  Dict[str, int] = {}

    while len(selected) < k and candidates:
        best_idx, best_adj, best_notes = 0, -9999.0, []

        for i, (song, base_score, _) in enumerate(candidates):
            penalty = 0.0
            notes: List[str] = []
            if artist_counts.get(song["artist"], 0) >= 1:
                penalty += artist_penalty
                notes.append(f"artist-dup -{artist_penalty:.2f}")
            if genre_counts.get(song["genre"], 0) >= max_per_genre:
                penalty += genre_penalty
                notes.append(f"genre-sat -{genre_penalty:.2f}")
            adj = base_score - penalty
            if adj > best_adj:
                best_adj, best_idx, best_notes = adj, i, notes

        song, base_score, explanation = candidates.pop(best_idx)
        if best_notes:
            explanation += " | diversity: " + ", ".join(best_notes)
        selected.append((song, best_adj, explanation))
        artist_counts[song["artist"]] = artist_counts.get(song["artist"], 0) + 1
        genre_counts[song["genre"]]   = genre_counts.get(song["genre"], 0) + 1

    return selected


# ── Public API ────────────────────────────────────────────────────────────────

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = DEFAULT_MODE,
) -> List[Tuple[Dict, float, str]]:
    """
    Score all songs with the selected mode, apply diversity penalty, return top-k.

    mode options:
      "genre-first"    – prioritises genre alignment
      "mood-first"     – prioritises detailed mood-tag overlap
      "energy-focused" – prioritises energy & danceability
    Required by src/main.py
    """
    weights = SCORING_MODES.get(mode, SCORING_MODES[DEFAULT_MODE])
    scored = [_score_song(song, user_prefs, weights) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return _apply_diversity_penalty(scored, k)


# ── Challenge 4: Visual Summary Table ────────────────────────────────────────

def format_table(
    recommendations: List[Tuple[Dict, float, str]],
    mode: str = DEFAULT_MODE,
    user_name: str = "",
) -> str:
    """
    Render recommendations as a formatted ASCII table.
    Columns: rank | title | artist | score | reasons
    Reasons column is truncated to fit terminal width but always present.
    """
    C_RANK   = 4
    C_TITLE  = 22
    C_ARTIST = 18
    C_SCORE  = 7
    C_REASON = 58

    def trunc(s: str, n: int) -> str:
        return s if len(s) <= n else s[: n - 1] + "…"

    sep = (
        "+" + "-" * (C_RANK   + 2)
        + "+" + "-" * (C_TITLE  + 2)
        + "+" + "-" * (C_ARTIST + 2)
        + "+" + "-" * (C_SCORE  + 2)
        + "+" + "-" * (C_REASON + 2)
        + "+"
    )
    header = "| {:<{}} | {:<{}} | {:<{}} | {:<{}} | {:<{}} |".format(
        "#",       C_RANK,
        "Title",   C_TITLE,
        "Artist",  C_ARTIST,
        "Score",   C_SCORE,
        "Reasons", C_REASON,
    )

    lines = [
        f"\n  Mode: [{mode.upper()}]  |  User: {user_name}",
        sep, header, sep,
    ]
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        lines.append(
            "| {:<{}} | {:<{}} | {:<{}} | {:<{}} | {:<{}} |".format(
                i,                              C_RANK,
                trunc(song["title"],  C_TITLE), C_TITLE,
                trunc(song["artist"], C_ARTIST),C_ARTIST,
                f"{score:.3f}",                 C_SCORE,
                trunc(explanation,    C_REASON), C_REASON,
            )
        )
    lines.append(sep)
    return "\n".join(lines)
