# pip install streamlit
import streamlit as st 
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import altair as alt
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

movies = pd.read_csv('data/final_movie_data.csv').drop(columns=['rating_id', 'movie_id'])
movie_titles = movies['title'].tolist()

top_movies = movies.sort_values(by='box_office', ascending=False).head(50).drop(columns=['id']).reset_index()
movies_genres = pd.read_csv('data/final_movie_data_genres.csv').drop(columns=['rating_id'])

# st.write(top_movies)
# st.write(movies)

# Search bar
st.title('Movie Reception Analysis ')
st.subheader('Hello! :movie_camera:')

def search_movie(title):
    matched_title = process.extractOne(query=title, choices=movie_titles)
    return movies[movies['title'] == matched_title[0]].reset_index()

search_title = st.text_input('Search for a movie by entering the title (try to be as exact as possible): EX. Barbie')
movie_info = search_movie(search_title)
movie_info['score_difference'] = movie_info['score_difference'].abs()
#st.write(movie_info)

st.image(movie_info.iloc[0]['poster'])
st.markdown(f'**{movie_info.iloc[0]['title']} ({movie_info.iloc[0]['year']})** by *{movie_info.iloc[0]['director']}*', width='stretch')
st.text(f'{movie_info.iloc[0]['plot']}')
st.badge(f"Rotten Tomatoes: {movie_info.iloc[0]['rotten_tomatoes_score']}%", color='red')
st.badge(f"{movie_info.iloc[0]['class']}" + ("" if movie_info.iloc[0]['class'] == 'Both Enjoyed' else f" by {movie_info.iloc[0]['score_difference']} Points"), color="green" if movie_info.iloc[0]['class'] == 'Both Enjoyed' else ("blue" if movie_info.iloc[0]['class'] == 'Audience Enjoyed More' else "orange"))

# Top 10 Movies
st.divider()
st.header('50 Popular Box Office Movies :ticket:')

with st.container(height=480, border=True):
    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
    movie_cols = [col1, col2, col3, col4, col5]
    index = 0

    for col in movie_cols:
        with col:
            temp = index 
            for temp in range(temp, 50, 5):
                st.image(top_movies.loc[temp, 'poster'])
                st.markdown(f'**{top_movies.loc[temp, 'title']}**', width='stretch')
                st.badge(f"{top_movies.loc[temp, 'class']}", color="green" if top_movies.loc[temp, 'class'] == 'Both Enjoyed' else ("blue" if top_movies.loc[temp, 'class'] == 'Audience Enjoyed More' else "orange"))
        index = index+1

# Data Visualization
col01, col02 = st.columns(2, gap='large')

with col01:
    st.subheader('Score Difference over Time')
    timeAvg_diff = movies.groupby('year')['score_difference'].mean().to_frame().reset_index()
    timeAvg_diff['year'] = timeAvg_diff['year'].astype(str)
    st.line_chart(timeAvg_diff, x='year', y='score_difference', use_container_width=True)
    st.write('This graph shows the change in average score difference over time. Most movies in the dataset are from recent years (the 21th century), but the average score difference generally tends to increase over time.')

    st.subheader('Distribution of Audience-Critic Score Differences')
    fig, ax = plt.subplots()
    ax.hist(movies['score_difference'], bins=30, color='#0168c9', edgecolor='white')
    ax.set_xlabel('Letterboxd - Rotten Tomatoes')
    ax.set_ylabel('Count')
    mean_diff = movies['score_difference'].mean()
    median_diff = movies['score_difference'].median()
    std_diff = movies['score_difference'].std()
    ax.axvline(mean_diff, color='#f09fa2', linestyle='--', label=f'Mean: {mean_diff:.2f}')
    ax.axvline(median_diff, color='#ec838a', linestyle='--', label=f'Median: {median_diff:.2f}')
    ax.axvline(std_diff, color='#de425b', linestyle='--', label=f'Standard Deviation: {std_diff:.2f}')
    ax.legend()
    st.pyplot(fig, use_container_width=True)
    st.write('The mean indicates more than half of the movies were rated lower by audiences compared to critics. However since the score difference is only around 6, and below 10 points, movies on average are shown to be enjoyed by both the audience and critics. The standard deviation suggests audience and critic opinions tend to differ.')


with col02:
    st.subheader('Box Office vs. Score Difference')
    st.scatter_chart(movies, x='box_office', y='score_difference', color='class', use_container_width=True)
    st.write("The scatter plot compares a movie's score difference with their box office results. For movies that were box office hits, the chart shows that critics tend to have enjoyed them more. Looking at movies that did not make much at the box office, the largest gap in score difference is 64, with the audience enjoying it more.")

    st.subheader('Average Score Difference by Genre')
    genre_diff = movies_genres.groupby('name')['score_difference'].mean().sort_values().reset_index()
    st.write(alt.Chart(genre_diff).mark_bar().encode(
    y=alt.Y('name', sort=None),
    x='score_difference'
    ))
    st.write('The average score difference of each genre was calculated and shown on the graph in descending order. Short films tend to have a great difference in opinions between audiences and critics. The top movies are those that lean towards real life stories, such as documentaries, historic films, and biographies. Romance, fantasy, and family movies are more likely to be enjoyed by both the audience and critics.')

# Movies with Biggest Score Differences
st.header('Movies with Biggest Score Differences')
aud_movies = movies.sort_values(by='score_difference', ascending=False).head(25).drop(columns=['id']).reset_index()
crit_movies = movies.sort_values(by='score_difference').head(25).drop(columns=['id']).reset_index()

st.subheader('Enjoyed more by the Audience :popcorn: ')
with st.container(height=480, border=True):
    aud_movies['score_difference'] = aud_movies['score_difference'].abs()
    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
    aud_cols = [col1, col2, col3, col4, col5]
    index = 0

    for col in aud_cols:
        with col:
            temp = index 
            for temp in range(temp, 25, 5):
                st.image(aud_movies.loc[temp, 'poster'])
                st.markdown(f'**{aud_movies.loc[temp, 'title']}**', width='stretch')
                st.badge(f"Rotten Tomatoes: {aud_movies.loc[temp]['rotten_tomatoes_score']}%", color='red')
                st.badge(f"Audience Rated {aud_movies.loc[temp, 'score_difference']} Points More", color="blue")
        index = index+1

st.subheader('Enjoyed more by Critics :clapper:')
with st.container(height=480, border=True):
    crit_movies['score_difference'] = crit_movies['score_difference'].abs()
    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
    crit_cols = [col1, col2, col3, col4, col5]
    index = 0

    for col in crit_cols:
        with col:
            temp = index 
            for temp in range(temp, 25, 5):
                st.image(crit_movies.loc[temp, 'poster'])
                st.markdown(f'**{crit_movies.loc[temp, 'title']}**', width='stretch')
                st.badge(f"Letterboxd: {crit_movies.loc[temp]['letterboxd_score']}%", color='green')
                st.badge(f"Critics Rated {crit_movies.loc[temp, 'score_difference']} Points More", color="orange")
        index = index+1