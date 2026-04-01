# coding = utf-8
import random
import math
import pymysql
from operator import itemgetter

class ItemBasedCF():
    def __init__(self):
        self.n_sim_movie = 8
        self.n_rec_movie = 4
        self.trainSet = {}
        self.testSet = {}
        self.movie_sim_matrix = {}
        self.movie_popular = {}
        self.movie_count = 0

    def get_dataset(self, pivot=0.75):
        trainSet_len = 0
        testSet_len = 0
        
        # 统一使用 3306 端口和标准配置
        cnn = pymysql.connect(
            host='127.0.0.1', 
            user='root', 
            password='123456', 
            port=3306, 
            database='flask_douban_comment',
            charset='utf8mb4'
        )
        cursor = cnn.cursor()
        sql = 'select * from tb_rate'
        cursor.execute(sql)
        for item in cursor.fetchall():
            user, movie, rating = item[1:]
            self.trainSet.setdefault(user, {})
            self.trainSet[user][movie] = rating
            trainSet_len += 1
            self.testSet.setdefault(user, {})
            self.testSet[user][movie] = rating
            testSet_len += 1
        cursor.close()
        cnn.close()

    def calc_movie_sim(self):
        for user, movies in self.trainSet.items():
            for movie in movies:
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1

        self.movie_count = len(self.movie_popular)

        for user, movies in self.trainSet.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2:
                        continue
                    self.movie_sim_matrix.setdefault(m1, {})
                    self.movie_sim_matrix[m1].setdefault(m2, 0)
                    self.movie_sim_matrix[m1][m2] += 1

        for m1, related_movies in self.movie_sim_matrix.items():
            for m2, count in related_movies.items():
                if self.movie_popular[m1] == 0 or self.movie_popular[m2] == 0:
                    self.movie_sim_matrix[m1][m2] = 0
                else:
                    self.movie_sim_matrix[m1][m2] = count / math.sqrt(self.movie_popular[m1] * self.movie_popular[m2])

    def recommend(self, user):
        K = self.n_sim_movie
        N = self.n_rec_movie
        rank = {}
        if user > len(self.trainSet) and len(self.trainSet) > 0:
            user = random.randint(1, len(self.trainSet))
        watched_movies = self.trainSet.get(user, {})

        for movie, rating in watched_movies.items():
            if movie in self.movie_sim_matrix:
                for related_movie, w in sorted(self.movie_sim_matrix[movie].items(), key=itemgetter(1), reverse=True)[:K]:
                    if related_movie in watched_movies:
                        continue
                    rank.setdefault(related_movie, 0)
                    rank[related_movie] += w * float(rating)
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    def rec_one(self, userId):
        print('推荐一个')
        return self.recommend(userId)

def recommend(userId):
    itemCF = ItemBasedCF()
    itemCF.get_dataset()
    itemCF.calc_movie_sim()
    return itemCF.rec_one(userId)