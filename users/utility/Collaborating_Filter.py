import os
import pandas as pd
from django.conf import settings
import numpy as np
import matplotlib.pyplot as plt


def start_collaborating(movieName):
    movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
    rating = os.path.join(settings.MEDIA_ROOT, "leadcopy", "ratings.csv")
    movies = pd.read_csv(movies)
    ratings = pd.read_csv(rating)

    ratings.describe()
    dataset = pd.merge(movies, ratings, how='left', on='movieId')
    print(dataset.tail())

    unique_user = ratings.userId.nunique(dropna=True)
    unique_movie = ratings.movieId.nunique(dropna=True)
    print("number of unique user:")
    print(unique_user)
    print("number of unique movies:")
    print(unique_movie)
    # for creating item user matrix  .. we need to check how many ratings we have here or how many are absent .
    total_ratings = unique_user * unique_movie
    rating_present = ratings.shape[0]

    ratings_not_provided = total_ratings - rating_present

    print("ratings not provided means some user have not watched some movies and its given by")
    print(ratings_not_provided)
    print("sparsity of user-item matrix is :")
    print(ratings_not_provided / total_ratings)
    # 2) plot rating frequency of each movie(how many time a movie has been rated)

    movie_freq = pd.DataFrame(ratings.groupby('movieId').size(), columns=['count'])
    movie_freq.head()
    # we can see that most of the movies are rated very rarely ..
    # so we can remove those movies which are rated less than 50 times.

    threshold_rating_freq = 10
    # first take out the movie id  for which movie is rated more than threshold value than keep only this movies in our original ratings dataframe
    # movie_freq.query('count>= @threshold_rating_freq').shape = (13360,1)
    # our original movie_freq has shape of (9724 ,1) and now its reduce to (2269,1)
    # so now lets reduce the size of ratings dataframe

    popular_movies_id = list(set(movie_freq.query('count>=@threshold_rating_freq').index))

    # ratings df after dropping non popular movies
    ratings_with_popular_movies = ratings[ratings.movieId.isin(popular_movies_id)]

    print('shape of ratings:')
    print(ratings.shape)

    print('shape of ratings_with_popular_movies:')
    print(ratings_with_popular_movies.shape)

    print("no of movies which are rated more than 50 times:")
    print(len(popular_movies_id))

    print("no of unique movies present in dataset:")
    print(unique_movie)

    user_cnt = pd.DataFrame(ratings.groupby('userId').size(), columns=['count'])
    user_cnt_copy = user_cnt
    user_cnt.head()

    # you cans see tha rating frequency vs users characterstics is tail - like structure which is similar to previous plot.
    # generally there are just few user who are interseted in giving rating to movies
    # lets find the user who gives rating more than 30 times
    threshold_val = 30
    active_user = list(set(user_cnt.query('count>=@threshold_val').index))

    # upadte your ratings_with_popular_movies
    ratings_with_popular_movies_with_active_user = ratings_with_popular_movies[
        ratings_with_popular_movies.userId.isin(active_user)]

    print('shape of ratings_with_popular_movies:')
    print(ratings_with_popular_movies.shape)

    print('shape of ratings_with_popular_movies_with_active_user:')
    print(ratings_with_popular_movies_with_active_user.shape)

    print("unique_user:")
    print(unique_user)

    print("active_user")
    print(len(active_user))

    print("unique_movies")
    print(unique_movie)

    print("popular_movies")
    print(len(popular_movies_id))

    print("sparsity of final ratings df:")
    print((428 * 2269 - 76395) / (428 * 2269))

    final_ratings = ratings_with_popular_movies_with_active_user
    # final_ratings.shape
    item_user_mat = final_ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)
    # create a mapper which maps movie index and its title
    movie_to_index = {
        movie: i for i, movie in enumerate(list(movies.set_index('movieId').loc[item_user_mat.index].title))
    }
    # (movie_to_index)

    # create a sparse matrix for more efficient calculations
    from scipy.sparse import csr_matrix
    item_user_mat_sparse = csr_matrix(item_user_mat.values)

    # fuzzy_movie_name_matching
    from fuzzywuzzy import fuzz

    def fuzzy_movie_name_matching(input_str, mapper, print_matches):
        # match_movie is list of tuple of 3 values(movie_name,index,fuzz_ratio)
        match_movie = []
        for movie, ind in mapper.items():
            current_ratio = fuzz.ratio(movie.lower(), input_str.lower())
            if (current_ratio >= 50):
                match_movie.append((movie, ind, current_ratio))

        # sort the match_movie with respect to ratio

        match_movie = sorted(match_movie, key=lambda x: x[2])[::-1]

        if len(match_movie) == 0:
            print("Oops..! no such movie is present here\n")
            return -1
        if print_matches == True:
            print("some matching of input_str are\n")
            for title, ind, ratio in match_movie:
                print(title, ind, '\n')

        return match_movie[0][1]

    # define the model
    from sklearn.neighbors import NearestNeighbors
    recommendation_model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)

    # create a function which takes a movie name and make recommedation for it
    def make_recommendation(input_str, data, model, mapper, n_recommendation):
        my_recom = []
        print("system is working....\n")
        model.fit(data)

        index = fuzzy_movie_name_matching(input_str, mapper, print_matches=False)

        if index == -1:
            print("pls enter a valid movie name\n")
            return

        index_list = model.kneighbors(data[index], n_neighbors=n_recommendation + 1, return_distance=False)
        # now we ind of all recommendation
        # build mapper index->title
        index_to_movie = {
            ind: movie for movie, ind in mapper.items()
        }

        print("Viewer who watches this movie ", input_str, "also watches following movies.")
        # print(index_list[0][2])
        for i in range(1, index_list.shape[1]):
            rcom = index_to_movie[index_list[0][i]]
            my_recom.append(rcom)
            print(rcom)

        return my_recom

    recom_movie = make_recommendation(movieName, item_user_mat_sparse, recommendation_model, movie_to_index, 10)
    return recom_movie