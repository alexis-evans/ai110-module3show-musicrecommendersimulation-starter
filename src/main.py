"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


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
        },
        {
            "name": "Chill Lofi",
            "favorite_genre": "lofi",
            "favorite_mood": "calm",
            "target_energy": 0.25,
            "target_acousticness": 0.75,
            "target_valence": 0.4,
            "target_danceability": 0.35,
        },
        {
            "name": "Deep Intense Rock",
            "favorite_genre": "rock",
            "favorite_mood": "angry",
            "target_energy": 0.95,
            "target_acousticness": 0.05,
            "target_valence": 0.2,
            "target_danceability": 0.5,
        },
    ]

    for user_prefs in user_profiles:
        print(f"\n=== Recommendations for: {user_prefs['name']} ===\n")
        recommendations = recommend_songs(user_prefs, songs, k=5)

        if not recommendations:
            print("No recommendations returned yet.")
            continue

        for i, rec in enumerate(recommendations, 1):
            song, score, explanation = rec
            print(f"  {i}. {song['title']} by {song['artist']}")
            print(f"     Score: {score:.2f}")
            print(f"     → {explanation}\n")


if __name__ == "__main__":
    main()
