# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Model Name: **YouLikeThatSong 1.0**

---

## 2. Intended Use  

The recommender is designed to generate music recommendations for users of a music streaming platform. Users enter their preferences, and the recommender finds songs similar to their preferred listening profile. The model assumes that the user only wants to hear music similar to their defined preferences, and does not give the user songs outside of those preferences. This is not implemented for real users; it is a school project for exploration of recommender algorithms.

---

## 3. How the Model Works  

The model takes in certain preferences from a user. It looks at the user's favorite genre and mood of songs, and their preferred levels of energy, acousticness, valence (how happy or sad a song is) and danceability. The last four features are numbers on a scale from 0.0 to 1.0. The model then compares this to a list of 50 songs in a data file. For each song, it compares how different the values are for the user's targets and the song's actual values. If a song is in the same genre or mood as the user's favorite, that has a higher sway on if the song is recommended. For the other features, it looks at how close the song and the user's values are using a math function. It then gives each comparison a weight, or how important it is to the final recommendation. The weights are multiplied by the differences found before, and then added together. This produces a score between 0.0 and 1.0 of how much the user will like a song, with 0 being not at all and 1 being a perfect match. It then recommends however many songs were requested with the highest scores.

Changes I made from the starter logic was implementing all the function stubs, and using a more complex formula for calculating difference. My method has drawbacks, but I think that it makes a better estimate than a linear function would.

---

## 4. Data    

The model uses a dataset of 50 songs with a wide range of genres and moods. Some genres have subgenres represented as well--for example, "pop" also shows up as "indie pop" or "country pop". The most common genres are pop (and variations) and lofi. For moods, there are multiple positive moods (like happy, euphoric, triumphant), neutral/subdued moods (like focused, relaxed, dreamy, nostalgic, peaceful), and negative moods (like intense, melancholy, angry, sad, anxious). There are many musical preferences not represented/recorded in the dataset, like the release year/decade, language, how much talking/lyrics are in the song, or volume of the song.

---

## 5. Strengths  

The model seems to work well for users that don't have very niche preferences, and their genre, mood, and other attributes all make sense together and are consistent. It will also work well for users who only want one, broad genre. It catches that users with high energy targets get high energy genres, like metal, pop, and electronic, and low energy target users get lofi or ambient tracks.

---

## 6. Limitations and Bias  

One weakness that the system has is that it only matches moods directly and does not account for similar/semantically close moods. For example, mood_s will be 1.0 or 0.0. chill, relaxed, peaceful, dreamy are all similar moods, but because they are technically different strings, the system does not account for that at all. A user that likes chill songs will never see a relaxed song if there are other chill songs, even though it could be a close or an even better match.

---

## 7. Evaluation  

I tested three different user profiles: High-Energy Pop, Chill Lofi, and Deep Intense Rock. What I looked for in the recommendations when evaluating how well the model was performing was looking at the scores it gave, and comparing the different attributes for each song (energy, valence, mood, etc.). What suprised me was how bad the model was at identifying similar songs that just had different mood words. For example, for the Chill Lofi profile, it correctly identified 5 songs that would fit with what the user would like, but the scores were so low just because the mood words were different. This showed me that the mood was a lot more important than I origianlly thought or anticipated. One of my experiments was doubling the weight of mood and halving the weight of genre. I thought genre was having too much of a pull on the recommendations, so I wanted to see how this would change the recommendations. To my surprise, for High-Energy Pop, 4 out of 5 recommended songs were exactly the same, and for the others, all of the songs were the same. I thought this was very interesting, because perhaps I could infer that mood was actually more important than genre. 

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Some more preferences that I would add could be the era or year the song is/user's preference, language preference or explicit-content filter, popular vs. niche songs, negative preferences (less of this artist/genre/mood), and favorite artists. For better ways to explain recommendations, I could add plain-language reasoning templates that explain in regular English why a song was recommended to a user. It could also show trade-offs, or add confidence labels.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps

I learned that recommender systems use user preferences and listening history and compare with their entire base of songs to find potential matches. I discovered that Spotify recommends songs from different artists so that one artist does not overwhelm every recommended song, which is not a feature that I implemented in my recommender. When I think about music recommendation apps, I wonder if songs that I listen to only one time influence my future recommendations, or if songs I listen to a lot matter more.

My biggest learning moment was learning how to choose the different features that would most likely create good recommendations for a user based on their profile. AI tools helped me a lot; they helped me choose good features to evaluate and how to find a function and weights that would appropriately distribute recommendations to choose good songs. Some areas where the AI struggled was making things either too simple, too complex, or too arbitrary. For example, with the features, it slimmed down the attributes to just three features, but then through going through the rest of the project I was learning that those three features were not enough and I actually needed to add more. The simple algorithm surprised me; I definitely thought it was not going to be enough to actually make good recommendations, but just using the features and some weights, it was able to parse together what would be some good songs for the user. Some things I would try next to extend this project would be to try out a ML/LLM model to see how much more consistent or advanced it can go. I imagine this is what Google and Spotify use for their recommenders, so I would like to see how it looks on a much smaller scale.
