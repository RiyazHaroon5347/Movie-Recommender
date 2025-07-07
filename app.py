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


'''def load_data():
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

    return new_df'''

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
selected_movie = st.selectbox("Choose a movie", movie_list)


TMDB_API_KEY = "9b12d347b6ae32fa5fe10efc7d58c7a3"


if st.button("Recommend"):
    recommendations = recommend(selected_movie)

    if recommendations:
        st.subheader("🎯 Recommended Movies:")

        # Add custom style for movie titles
        st.markdown("""
        <style>
        .movie-title {
            font-size: 20px;
            font-weight: 600;
            text-align: center;
            color: #FFD700;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Group posters into rows of 3
        for i in range(0, len(recommendations), 3):
            cols = st.columns(3)

            for j in range(3):
                if i + j < len(recommendations):
                    movie = recommendations[i + j]
                    poster_url = fetch_poster(movie, TMDB_API_KEY)
                    with cols[j]:
                        st.image(poster_url, use_container_width=True)
                        st.markdown(f"<div class='movie-title'>🎬 {movie}</div>", unsafe_allow_html=True)
    else:
        st.warning("No recommendations found. Try another movie.")



