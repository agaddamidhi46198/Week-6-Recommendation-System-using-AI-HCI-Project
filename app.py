# The Streamlit interface has been created to load the recommendation model with the load_model() function and to recommend movies with the recommend() function. 
# Genre filtering, similarity scores, user feedback, and proactive suggestions were included to improve user interaction.

# Importing the required libraries
import streamlit as st
from recommender import MovieRecommender

# Setting the application title and icon
st.set_page_config(
    page_title="MovieMatch AI",
    page_icon="🎬"
)

# Loading and caching the recommendation model
@st.cache_resource
def load_model():
    return MovieRecommender()

# Creating the recommendation model
model = load_model()

# Initializing user feedback
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Initializing movie selection history
if "history" not in st.session_state:
    st.session_state.history = []

# Displaying the application title
st.title("🎬 MovieMatch AI")

# Displaying the application introduction
st.write(
    "Discover movies similar to your favorites."
    " You control the suggestions."
)

# Creating the sidebar for user preferences
with st.sidebar:

    st.header("Preferences")

    # Providing movie selection options
    title = st.selectbox(
        "Choose a movie you like",
        model.movies.title.tolist()
    )

    # Collecting and sorting available movie genres
    genres = sorted({
        g for value in model.movies.genre
        for g in value.split("|")
    })

    # Providing genre filtering options
    genre = st.selectbox(
        "Filter by genre",
        ["All"] + genres
    )

    # Setting the number of movie recommendations
    limit = st.slider(
        "Maximum recommendations", 1, 10, 5
    )

    # Providing an option for proactive suggestions
    proactive = st.checkbox(
        "Enable proactive suggestions",
        value=False
    )

    # Clearing stored feedback and movie history
    if st.button("Clear feedback and history"):
        st.session_state.feedback = {}
        st.session_state.history = []

# Creating the recommendation button
if st.button("Recommend movies", type="primary"):

    # Storing the selected movie in history
    st.session_state.history.append(title)

    # Activating the recommendation process
    st.session_state.active = True

# Checking the recommendation status
if st.session_state.get("active", False):

    # Generating movie recommendations based on user preferences
    results = model.recommend(
        title,
        genre,
        limit,
        st.session_state.feedback
    )

    # Displaying the recommendation heading
    st.subheader("Recommended for you")

    # Handling unavailable movie recommendations
    if not results:
        st.info(
            "No matching movies."
            " Try another genre or movie."
        )

    # Iterating through the recommended movies
    for movie in results:

        # Creating a separate container for each movie
        with st.container(border=True):

            # Displaying movie details
            st.markdown("**" + movie["title"] + "**")
            st.caption(movie["genre"])
            st.write(movie["description"])

            # Displaying the movie similarity score
            st.write(
                f"Content similarity: "
                f"{movie['similarity']:.1%}"
            )

            # Explaining the meaning of the similarity score
            st.caption(
                "Based on shared words in genres and "
                "descriptions; not a probability of enjoyment."
            )

            # Creating columns for feedback buttons
            a, b = st.columns(2)

            # Collecting positive user feedback
            if a.button(
                "Like",
                key="like_" + movie["title"]
            ):
                st.session_state.feedback[
                    movie["title"]
                ] = 1

                # Refreshing the recommendation interface
                st.rerun()

            # Collecting negative user feedback
            if b.button(
                "Dislike",
                key="dislike_" + movie["title"]
            ):
                st.session_state.feedback[
                    movie["title"]
                ] = -1

                # Refreshing the recommendation interface
                st.rerun()

# Checking the proactive suggestion option and movie history
if proactive and st.session_state.history:

    # Retrieving the most recently selected movie
    recent = st.session_state.history[-1]

    # Generating proactive movie suggestions
    suggestions = model.recommend(
        recent,
        limit=1,
        feedback=st.session_state.feedback
    )

    # Displaying the proactive movie suggestion
    if suggestions:
        st.info(
            f"Proactive suggestion based on your "
            f"last request ({recent}): "
            f"{suggestions[0]['title']}"
        )

# Displaying feedback storage and privacy information
st.caption(
    "Feedback stays in this browser session."
    " No external AI API or account is required."
)