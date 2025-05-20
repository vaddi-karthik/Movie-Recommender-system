import os
import pandas as pd
from django.conf import settings
import numpy as np
import matplotlib.pyplot as plt


def start_content_Based(movieName):
    movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
    rating = os.path.join(settings.MEDIA_ROOT, "leadcopy", "ratings.csv")
    movies = pd.read_csv(movies)
    ratings = pd.read_csv(rating)
    dataset = pd.merge(movies, ratings, how='left', on='movieId')

    table = dataset.pivot_table(index='title', columns='userId', values='rating')
    table = table.fillna(0)
    from scipy.sparse import csr_matrix

    matrix = csr_matrix(table.values)
    user_query_index = np.random.choice(table.shape[1])
    user_query_index
    from sklearn.metrics.pairwise import linear_kernel

    cosine = linear_kernel(matrix, matrix)

    def recommendations(name, cosine=cosine):
        recommended_list = []
        idx = user_query_index
        score = pd.Series(cosine[idx]).sort_values(ascending=False)

        top_10 = list(score.iloc[0:10].index)
        for each in top_10:
            recommended_list.append(list(table.index)[each])
        return recommended_list

    print('Recommendation for {0} :\n'.format(table.index[user_query_index]))
    return recommendations(table.index[user_query_index])
