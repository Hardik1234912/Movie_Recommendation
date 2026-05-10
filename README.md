🎬 Movie Recommendation System

A Machine Learning based Movie Recommendation System that suggests similar movies using the TMDB Top 5000 Movies Dataset and Cosine Similarity.

This project analyzes movie metadata such as genres, keywords, cast, crew, and overview to recommend movies similar to the user's selected movie.

---

 🚀 Features

- Recommend similar movies instantly
- Uses Content-Based Filtering
- Cosine Similarity algorithm
- TMDB Top 5000 Movies Dataset
- Clean and interactive UI
- Fast recommendation engine

---

🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- NLTK
- Streamlit / Flask
- Pickle

---

 📂 Dataset

Dataset Used: TMDB Top 5000 Movies Dataset

The dataset contains:
- Movie titles
- Genres
- Cast
- Crew
- Keywords
- Overview
- Popularity ratings

 ⚙️ How It Works

1. Data preprocessing and cleaning
2. Feature extraction from movie metadata
3. Combining important tags
4. Text vectorization
5. Similarity calculation using Cosine Similarity
6. Recommend top similar movies


 ▶️ Run the Project


pip install -r requirements.txt

streamlit run app.py
