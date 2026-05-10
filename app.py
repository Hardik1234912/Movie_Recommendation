import os
import streamlit as st
import pandas as pd
import pickle
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# -------------------------
# Config / small constants
# -------------------------
TMDB_API_KEY = "449aea0af72b41c172bba8696276444b"
TMDB_MOVIE_URL = f"https://api.themoviedb.org/3/movie/{{}}?api_key={TMDB_API_KEY}&language=en-US"

# Fallback placeholder
FALLBACK_POSTER = "data:image/svg+xml;utf8," + urllib.parse.quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='600'>"
    "<rect width='100%' height='100%' fill='#2a2a2a'/>"
    "<text x='50%' y='45%' dominant-baseline='middle' text-anchor='middle' fill='#888' font-size='18' font-weight='bold'>No Poster</text>"
    "<text x='50%' y='55%' dominant-baseline='middle' text-anchor='middle' fill='#666' font-size='14'>Available</text>"
    "</svg>"
)

# Session-based poster cache
if 'poster_cache' not in st.session_state:
    st.session_state.poster_cache = {}

def get_poster_url(movie_id):
    """Get poster URL from cache or fetch from TMDB"""
    if movie_id in st.session_state.poster_cache:
        return st.session_state.poster_cache[movie_id]
    
    try:
        session = requests.Session()
        retry_strategy = Retry(
            total=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=0.1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        response = session.get(TMDB_MOVIE_URL.format(movie_id), timeout=2)
        response.raise_for_status()
        data = response.json()
        
        if data.get('poster_path'):
            url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            st.session_state.poster_cache[movie_id] = url
            return url
    except Exception:
        pass
    
    st.session_state.poster_cache[movie_id] = FALLBACK_POSTER
    return FALLBACK_POSTER

# -------------------------
# Recommendation function with caching
# -------------------------
@st.cache_data
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    # top 5 similar movies (skip the movie itself)
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    movie_ids = []

    for idx_tuple in movie_list:
        idx = idx_tuple[0]
        recommended_movies.append(movies.iloc[idx].title)
        movie_ids.append(movies.iloc[idx].movie_id)

    return recommended_movies, movie_ids

# -------------------------
# Load data (pickles)
# -------------------------
try:
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"Failed to load 'movies_dict.pkl': {e}")
    raise

try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Failed to load 'similarity.pkl': {e}")
    raise

# Quick sanity check: ensure expected columns exist
if 'title' not in movies.columns:
    st.error("movies DataFrame has no 'title' column. Check your movies_dict.pkl structure.")
if 'movie_id' not in movies.columns:
    # allow common alternate names: 'id' or 'movieId'
    if 'id' in movies.columns:
        movies = movies.rename(columns={'id': 'movie_id'})
    elif 'movieId' in movies.columns:
        movies = movies.rename(columns={'movieId': 'movie_id'})
    else:
        st.error("movies DataFrame has no 'movie_id'/'id'/'movieId' column. Fix your data.")

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("Movie Recommender System")

selected_movie_name = st.selectbox('Select your preferred movie', movies['title'].values)

if st.button('Recommend'):
    with st.spinner('Finding recommendations...'):
        names, movie_ids = recommend(selected_movie_name)
    
    # Fetch all posters in parallel
    posters = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_poster_url, mid): i for i, mid in enumerate(movie_ids)}
        posters = [None] * len(movie_ids)
        for future in as_completed(futures):
            idx = futures[future]
            try:
                posters[idx] = future.result()
            except Exception:
                posters[idx] = FALLBACK_POSTER

    st.subheader("Top 5 Recommended Movies:")
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.image(poster, use_container_width=True)
            st.write(f"**{name}**", unsafe_allow_html=True)
