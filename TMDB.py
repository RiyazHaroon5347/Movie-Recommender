import requests
import pandas as pd

API_KEY = '9b12d347b6ae32fa5fe10efc7d58c7a3' 

def fetch_popular_movies(page=1):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    response = requests.get(url)
    return response.json()['results']

def fetch_credits(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    return requests.get(url).json()

def fetch_keywords(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={API_KEY}"
    return requests.get(url).json()

def build_movie_data(pages=1):
    movies_list = []
    credits_list = []

    for page in range(1, pages + 1):
        for movie in fetch_popular_movies(page):
            movie_id = movie['id']
            title = movie.get('title', '')
            overview = movie.get('overview', '')

            # Simulate genres structure (TMDB genre_ids don't include names)
            genres = [{"id": g, "name": ""} for g in movie.get('genre_ids', [])]

            # Fetch credits and keywords
            credit_data = fetch_credits(movie_id)
            cast = credit_data.get('cast', [])
            crew = credit_data.get('crew', [])

            keyword_data = fetch_keywords(movie_id)
            keywords = keyword_data.get('keywords', [])

            # Final format
            movie_row = {
                'movie_id': movie_id,
                'title': title,
                'overview': overview,
                'genres': str(genres),
                'keywords': str(keywords),
                'cast': str(cast),
                'crew': str(crew)
            }

            movies_list.append(movie_row)
            credits_list.append({
                'movie_id': movie_id,
                'title': title,
                'cast': str(cast),
                'crew': str(crew)
            })

    return pd.DataFrame(movies_list), pd.DataFrame(credits_list)

def merge_with_existing_data(new_movies_df, new_credits_df):
    try:
        movies_old = pd.read_csv("movies.csv")
        credits_old = pd.read_csv("credits.csv")
    except FileNotFoundError:
        movies_old = pd.DataFrame()
        credits_old = pd.DataFrame()

    movies_combined = pd.concat([movies_old, new_movies_df]).drop_duplicates(subset='movie_id')
    credits_combined = pd.concat([credits_old, new_credits_df]).drop_duplicates(subset='movie_id')

    movies_combined.to_csv("movies.csv", index=False)
    credits_combined.to_csv("credits.csv", index=False)
    print("✅ Movie and credits data updated successfully!")

if __name__ == "__main__":
    print("🚀 Fetching data from TMDB...")
    new_movies, new_credits = build_movie_data(pages=2)
    merge_with_existing_data(new_movies, new_credits)
