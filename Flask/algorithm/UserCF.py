# coding = utf-8
import random
import math
from operator import itemgetter
import pymysql

class UserBasedCF():
    def __init__(self):
        self.n_sim_user = 4
        self.n_rec_movie = 4
        self.trainSet = {}
        self.testSet = {}
        self.user_sim_matrix = {}
        self.movie_count = 0
        print('Similar user number = %d' % self.n_sim_user)
        print('Recommneded movie number = %d' % self.n_rec_movie)

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
            if random.random() < pivot:
                self.trainSet.setdefault(user, {})
                self.trainSet[user][movie] = rating
                trainSet_len += 1
            else:
                self.testSet.setdefault(user, {})
                self.testSet[user][movie] = rating
                testSet_len += 1
        print('Split trainingSet and testSet success!')
        cursor.close()
        cnn.close()

    def calc_user_sim(self):
        movie_user = {}
        for user, movies in self.trainSet.items():
            for movie in movies:
                if movie not in movie_user:
                    movie_user[movie] = set()
                movie_user[movie].add(user)
        self.movie_count = len(movie_user)

        for movie, users in movie_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1

        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))

    def recommend(self, user):
        K = self.n_sim_user
        N = self.n_rec_movie
        rank = {}
        if user > len(self.trainSet) and len(self.trainSet) > 0:
            user = random.randint(1, len(self.trainSet))
        watched_movies = self.trainSet.get(user, {})

        if user in self.user_sim_matrix:
            for v, wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0:K]:
                for movie in self.trainSet.get(v, {}):
                    if movie in watched_movies:
                        continue
                    rank.setdefault(movie, 0)
                    rank[movie] += wuv
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    def rec_one(self, userId):
        print('推荐一个')
        return self.recommend(userId)

def recommend(userId):
    userCF = UserBasedCF()
    userCF.get_dataset()
    userCF.calc_user_sim()
    return userCF.rec_one(userId)