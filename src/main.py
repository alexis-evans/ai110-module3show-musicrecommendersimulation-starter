"""
Command line runner for the Music Recommender Simulation.

Demonstrates:
  Challenge 1 – Advanced song features (popularity, release_decade, mood_tags)
  Challenge 2 – Multiple scoring modes (genre-first / mood-first / energy-focused)
  Challenge 3 – Diversity penalty (no artist dominance, genre cap of 2)
  Challenge 4 – Formatted ASCII table output with reasons for every score
"""

from recommender import load_songs, recommend_songs, format_table, SCORING_MODES


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_profiles = [
        {
            "name": "High-Energy Pop",
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.9,
            "target_acousticness": 0.1,
            "target_valence": 0.95,
            "target_danceability": 0.85,
            # Challenge 1 – advanced preferences
            "preferred_decade": 2010,
            "preferred_mood_tags": ["uplifting", "danceable", "euphoric"],
        },
        {
            "name": "Chill Lofi",
            "favorite_genre": "lofi",
            "favorite_mood": "calm",
            "target_energy": 0.25,
            "target_acousticness": 0.75,
            "target_valence": 0.4,
            "target_danceability": 0.35,
            "preferred_decade": 2020,
            "preferred_mood_tags": ["calm", "dreamy", "focused", "peaceful"],
        },
        {
            "name": "Deep Intense Rock",
            "favorite_genre": "rock",
            "favorite_mood": "angry",
            "target_energy": 0.95,
            "target_acousticness": 0.05,
            "target_valence": 0.2,
            "target_danceability": 0.5,
            "preferred_decade": 1970,
            "preferred_mood_tags": ["aggressive", "powerful", "intense"],
        },
    ]

    # ── Challenge 2: Scoring Mode Demo ───────────────────────────────────────
    # Each user is shown across all 3 scoring modes so you can see how the
    # rankings shift when the strategy changes.  To hard-code a single mode,
    # replace the inner loop with a fixed string, e.g. mode = "mood-first".
    for user_prefs in user_profiles:
        print(f"\n{'=' * 80}")
        print(f"  USER PROFILE: {user_prefs['name']}")
        print(f"  Preferred decade: {user_prefs['preferred_decade']}s  |  "
              f"Mood tags: {user_prefs['preferred_mood_tags']}")
        print(f"{'=' * 80}")

        for mode in SCORING_MODES:
            recs = recommend_songs(user_prefs, songs, k=5, mode=mode)
            # Challenge 4 – formatted table with reasons column
            print(format_table(recs, mode=mode, user_name=user_prefs["name"]))


if __name__ == "__main__":
    main()
