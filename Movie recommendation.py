import requests
import pandas as pd

API_KEY = 'YOUR_TMDB_API_KEY_HERE'

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
            title = movie['title']
            overview = movie.get('overview', '')

            # Genres
            genres = [{'id': g['id'], 'name': g['name']} for g in movie.get('genre_ids', [])]

            # Credits
            credit_data = fetch_credits(movie_id)
            cast = credit_data.get('cast', [])
            crew = credit_data.get('crew', [])

            # Keywords
            keyword_data = fetch_keywords(movie_id)
            keywords = keyword_data.get('keywords', [])

            # Format
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

movies_df, credits_df = build_movie_data(pages=2)  # 2 pages = 40 movies
movies_df.to_csv("new_movies.csv", index=False)
credits_df.to_csv("new_credits.csv", index=False)
