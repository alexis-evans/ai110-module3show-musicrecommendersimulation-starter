# 🎵 Music Recommender Simulation

## Screenshots
<img width="1140" height="1187" alt="Music Recommender Screenshot 1" src="https://github.com/user-attachments/assets/05a23a31-0764-4af8-a2af-bcb4f4951a2c" />

<img width="1112" height="524" alt="Music Recommender Screenshot 2" src="https://github.com/user-attachments/assets/424c11e5-63d7-4e29-aaf0-7f074a5e6405" />



## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

From what I can tell about real world recommendation-systems, there are two core approaches: content-based filtering and collaborative filtering. Content-based filtering recommends items that are similar to what you've already liked, and collaborative filtering recommends items that are similar to people who consume the same content you do. My system will prioritize a content-based filtering approach, because there are no other users to compare to. The features of each `Song` that my system will use will be: genre, mood, energy, valence, danceability, and acousticness. For now, my `UserProfile` will store favorite_genre, favorite_mood, target_energy, target_acousticness, target_valence, and target_danceability. These may be changed based on how the recommender does.

How the Recommender recommends songs:
1. `main.py` runs, loads songs intoa list of dictionaries if csv file exists, otherwise, returns an empty list.
2. Define user_prefs: Dict(name genre, songs, k=5)
3. For each song: score the song (user_prefs vs song attributes)
  * genre match
  * mood match
  * energy delta
  * acousticness delta
  * valence delta
  * danceability delta
4. Aggregate score
5. Build explanation

The recommender will use a Gaussian (bell-curve) proximity function that is centered on the user's preferred value. I chose to use a Gaussian bell curve over linear because it rewards being close more than being somewhat close, and it doesn't linearily punish mid-range misses.

For the categorical attributes (favorite genre and mood), favorite genre has the rule that an exact match will be weighted as 1.0, a partial match (indie pop contains pop) is a 0.5, and no match is 0.0. For mood, an exact match returns a weight of 1.0, and no match returns 0.0.

Each feature contributes to the final score through a weighted sum. The weights reflect how much each feature should influence the recommendation:

| Feature | Weight | Reason |
|---|---|---|
| Genre | 0.30 | Genre is the strongest filter — a mismatch is often a deal-breaker |
| Mood | 0.25 | Mood captures current emotional intent but is slightly more flexible than genre |
| Energy | 0.20 | Energy drives how a song feels, and the user provides an explicit target |
| Valence | 0.10 | Correlated with mood, but song-specific enough to matter |
| Danceability | 0.10 | Important for context (studying vs. working out), but secondary |
| Acousticness | 0.05 | More of a texture preference; lowest confidence in the user's signal |

The final score for a song is:

```
score = 0.30 × genre_match + 0.25 × mood_match + 0.20 × proximity(energy) + 0.10 × proximity(valence) + 0.10 × proximity(danceability) + 0.05 × proximity(acousticness)
```

All scores fall between 0.0 and 1.0. Songs are then sorted by score descending, and the top k are returned as recommendations.

Some biases:

1. Genre gatekeeping
Genre carries the highest weight (0.30) and uses hard string matching. A jazz song with a perfect mood, energy, and vibe match scores at most 0.70 against a user who prefers pop — it's penalized before the music itself is even evaluated. Great cross-genre discoveries get buried.

2. Partial match asymmetry
"indie pop" partially matches "pop" (scores 0.5), but "pop" does not partially match "indie pop". The direction of the substring check matters. A user who lists favorite_genre = "indie pop" will never get partial credit for a plain "pop" song, even though those genres heavily overlap.

3. Mood is all-or-nothing
Mood has no partial match — "relaxed" and "chill" score 0 against each other despite being semantically similar. A song that's clearly in the same emotional neighborhood gets no credit. The categorical boundary is arbitrary relative to how moods actually feel.

4. Catalog bias toward whatever moods are in the CSV
If the catalog only has "happy", "chill", and "intense", users who set favorite_mood = "melancholic" will never get a mood match. The system silently degrades for users whose preferences aren't well-represented in the data.

5. Gaussian σ is one-size-fits-all
The tolerance (σ = 0.15) is fixed for all numerical features. But a user might be very picky about energy (narrow preference) but totally flexible about acousticness. A single σ treats all features as equally tolerant, which misrepresents real preferences.

6. Weight assumptions don't generalize
The weights (genre 0.30, mood 0.25, etc.) were designed with a general listener in mind. A user who listens exclusively by energy level (e.g., workout playlists) is poorly served — energy is structurally limited to 0.20 no matter what.

7. Acousticness underweighted for acoustic listeners
target_acousticness carries only 0.05 weight. A user who deeply cares about acoustic vs. electric texture — a folk purist, for example — will get recommendations that ignore their strongest preference.

8. No diversity enforcement
The ranking rule is pure score-descending. If three lofi songs all score similarly high, a user gets three lofi songs. No mechanism prevents the top-k from being near-identical tracks from the same niche.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

1. I tested what a user with contradicting desires (i.e. high energy, but mood calm). The system prioritized mood over energy because it's weighted heavier, so the songs were lower on the scores, but mostly matched the mood.
2. I tested adding tempo to the score, but it didn't do much because the songs that had more subdued moods already had lower tempos and vice versa.
3. I tested making mood more important than genre, but the songs that it recommended were mostly the same, so it didn't do much.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

1. There are only some songs in the catalog, and they all must be manually assesed for every feature. This makes it hard to add new songs automatically.
2. Similar moods do not affect the system. It only looks for direct matches and has no way of knowing that too moods are basically synonyms of each other, so the weights for certain songs are off.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

In this project, I learned that recommenders turn data into predictions by comparing user preferences to song attributes using math. Each feature, like energy or mood, gets assigned a weight based on how important it is, and those weighted differences produce a score. The higher the score, the better the match. This showed me that the system is only as good as the features you pick and how much weight you give them. Small choices, like doubling the weight of mood, can change results in unexpected ways.

I also learned that bias can sneak into a system through the data and the design. My dataset had more pop and lofi songs than other genres, which means users with those preferences get better results than users with niche tastes. The mood matching was also unfair in a hidden way: two songs that feel very similar, like "chill" and "relaxed," got treated as completely different, which hurt scores for users who liked those moods. This taught me that bias does not always look obvious, and sometimes it is built into how categories are defined or what data was collected in the first place.

---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.
---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

