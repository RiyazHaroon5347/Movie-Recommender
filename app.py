import streamlit as st
import pandas as pd
import ast
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://i.etsystatic.com/23423883/r/il/3866e3/4528785581/il_fullxfull.4528785581_o0dr.jpg");
             background-attachment: fixed;
             background-size: cover;
             background-position: center;
             background-color: rgba(0, 0, 0, 0.6);
             background-blend-mode: darken;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


@st.cache_data


def load_data():
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')
    movies = movies.merge(credits, on='title')
    movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    movies.dropna(inplace=True)

    def convert(obj):
        return [i['name'] for i in ast.literal_eval(obj)]

    def get_top_cast(obj):
        return [i['name'] for i in ast.literal_eval(obj)[:3]]

    def get_director(obj):
        return [i['name'] for i in ast.literal_eval(obj) if i['job'] == 'Director'][:1]

    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(get_top_cast)
    movies['crew'] = movies['crew'].apply(get_director)
    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

    new_df = movies[['movie_id', 'title', 'tags']]
    new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x)).str.lower()

     try:
        extra1 = pd.read_csv('movies_metadata')[['movie_id', 'title', 'tags']]
        extra2 = pd.read_csv('netflix_data')[['movie_id', 'title', 'tags']]
        new_df = pd.concat([new_df, extra1, extra2], ignore_index=True)
        new_df.drop_duplicates(subset='title', inplace=True)
    except Exception as e:
        print(f"⚠️ Error loading extra files: {e}")

    # Save to CSV
    new_df.to_csv("final_movies.csv", index=False)

    return new_df

new_df = load_data()

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

def recommend(movie):
    movie = movie.lower()
    if movie not in new_df['title'].str.lower().values:
        return []
    index = new_df[new_df['title'].str.lower() == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
    return [new_df.iloc[i[0]].title for i in movie_list]

def fetch_poster(movie_title, api_key):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    return "https://via.placeholder.com/300x450?text=No+Image"

# ---------- Streamlit UI ----------
add_bg_from_url()

import streamlit as st
import requests

API_KEY = '9b12d347b6ae32fa5fe10efc7d58c7a3'


st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap" rel="stylesheet">
<style>
.title-container {
    font-family: 'Montserrat', sans-serif;
    font-size: 40px;
    text-align: center;
    color: white;
    padding: 30px;
    margin-top: 20px;
    margin-bottom: 30px;

    background: rgba(0, 0, 0, 0.3);           /* semi-transparent black */
    border: 2px solid rgba(255, 255, 255, 0.2); /* light transparent border */
    border-radius: 20px;
    backdrop-filter: blur(3px);               /* blur effect */
    -webkit-backdrop-filter: blur(3px);       /* Safari support */
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.5); /* golden glow */
}
</style>

<div class="title-container">
    🎬 Movie Recommender 🍿
</div>
""", unsafe_allow_html=True)

movie_list = new_df['title'].sort_values().tolist()
movie_list.insert(0, "--- Select a Movie ---")

selected_movie = st.selectbox("Choose a movie", movie_list)

if selected_movie != "--- Select a Movie ---" and st.button("Recommend"):
    recommendations = recommend(selected_movie)
    if recommendations:
        st.subheader("Recommended Movies:")
        for i in recommendations:
            st.write("✅", i)
    else:
        st.warning("No recommendations found. Try another movie.")


API_KEY = '9b12d347b6ae32fa5fe10efc7d58c7a3'

def fetch_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

# Initialize session state
if 'show_trending' not in st.session_state:
    st.session_state.show_trending = False

# Main page layout

if not st.session_state.show_trending:
    # Home Page
    st.write("Welcome to the Movie Recommendation System!")
    st.write("Click the button below to view the latest trending movies.")

    if st.button("🔥 Show Trending Movies"):
        st.session_state.show_trending = True

else:
    # Trending Movies Page
    st.header("🔥 Top Trending Movies This Week")

    trending = fetch_trending_movies()

    if trending:
        col1, col2 = st.columns(2)

        for i, movie in enumerate(trending):
            title = movie.get('title', 'No Title')
            poster_path = movie.get('poster_path')
            if poster_path:
                full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
                col = col1 if i % 2 == 0 else col2
                with col:
                    st.image(full_path, use_container_width=True)
                    st.caption(title)
    else:
        st.error("Failed to load trending movies. Please try again later.")

    if st.button("⬅️ Back to Home"):
        st.session_state.show_trending = False

