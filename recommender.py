# The __init__() function loaded and converted movie data sets to numerical vectors by employing TF-IDF in the representation vectors of movie genres and descriptions. 
# The recommend() function produced similarity scores, applied genre filters, took into account user feedback and ranked movie recommendations.

# Importing the required libraries
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Creating the movie recommendation class
class MovieRecommender:

    # Initializing the recommendation model
    def __init__(self, path=Path(__file__).with_name("movies.csv")):

        # Loading the dataset and handling missing values
        self.movies = pd.read_csv(path).fillna("")

        # Combining movie genres and descriptions
        features = (
            self.movies["genre"].str.replace("|", " ", regex=False)
            + " "
            + self.movies["description"]
        )

        # Creating the TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        # Converting movie features into numerical vectors
        self.matrix = self.vectorizer.fit_transform(features)

    # Defining the movie recommendation function
    def recommend(self, title, genre="All",
                  limit=5, feedback=None):

        # Finding the selected movie in the dataset
        matches = self.movies.index[
            self.movies.title == title
        ]

        # Handling invalid movie titles
        if len(matches) == 0:
            raise ValueError("Unknown movie title")

        # Retrieving the selected movie index
        idx = matches[0]

        # Calculating cosine similarity scores
        scores = cosine_similarity(
            self.matrix[idx], self.matrix
        ).ravel()

        # Initializing user feedback
        feedback = feedback or {}

        # Creating an empty recommendation list
        candidates = []

        # Iterating through the available movies
        for i, movie in self.movies.iterrows():

            # Excluding the selected movie
            if i == idx:
                continue

            # Filtering movies based on the selected genre
            if genre != "All" and genre not in movie.genre.split("|"):
                continue

            # Excluding movies with negative feedback
            if feedback.get(movie.title) == -1:
                continue

            # Retrieving the movie similarity score
            score = float(scores[i])

            # Removing movies with zero or negative similarity
            if score <= 0:
                continue

            # Storing movie details and adjusting ranking scores
            candidates.append({
                "title": movie.title,
                "genre": movie.genre,
                "description": movie.description,
                "similarity": score,
                "rank_score": score + 0.1 * feedback.get(
                    movie.title, 0
                )
            })

        # Sorting movies based on ranking scores and returning the requested number of recommendations
        return sorted(
            candidates,
            key=lambda x: (-x["rank_score"], x["title"])
        )[:limit]