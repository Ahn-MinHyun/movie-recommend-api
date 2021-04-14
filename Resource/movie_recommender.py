import pandas as pd
import numpy as np
from flask_restful import Resource
from flask import request
from http import HTTPStatus
from db.db import get_mysql_connection
import json, decimal

# 유저인증을 위한 JWT 라이브러리 import 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

class MovieRecommendation(Resource) :

    # 영화를 조회 할 수 있는건? 써져 있지 않아 일단 아무나 할 수 있도록 
    # 영화 조회 API
    @jwt_required()
    def get(self):

        # 유저의 리뷰를 기반으로 추천시스템

        # 유저의 리뷰정보 가져오기 

        user_id = get_jwt_identity()
        print(user_id)

        # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        # 쿼리문 작성
        # 평균을 잡으니 decimal타입이 되어 json으로 포멧되지 않아, floor사용
        query ='''select m.title, r.rating
                          from movie_rating r
                          join movie m
                            on m.id = r.item_id
                          join movie_user u 
                            on u.id = r.user_id
                          where u.id = %s;'''
        
        param = (user_id, )

        

        # 쿼리문 실행 후 저장
        cursor.execute(query, param)
        records = cursor.fetchall()

        # 데이터베이스 닫기
        cursor.close()
        connection.close()

        print(records)
        # 리뷰를 작성하지 않아 데이터가 존재하지 않을 때
        if len(records) == 0:
            return {"message" : 1 },HTTPStatus.NOT_FOUND
    
        # 데이터를 처리하기 판다스 데이터프레임으로 만들어 사용 
        user_rating = pd.json_normalize(data= records)

        # 미리 만들어둔 movie_correlations.csv파일 불러온다.
        movie_correlations = pd.read_csv('./db/movie_correlations.csv', index_col='title')


        # 반복문을 사용하여 각 영화에 대한 관계와 가중치를 생성하여 새로운 리스트로 추가 
        similar_movies_list = pd.DataFrame()
        for i in np.arange(0, len(user_rating)):
            movie_title = user_rating['title'][i]
            similar_movie = movie_correlations[movie_title].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['weight'] = similar_movie['Correlation']*user_rating['rating'][i]
            similar_movies_list=similar_movies_list.append(similar_movie)

        # 영화 추천 상위 10개 
        Movie_recommendation = similar_movies_list.sort_values('weight',ascending=False).head(10)

        # Correlation컬럼은 버리고 json으로 변환        
        user_movie_recommend = Movie_recommendation.reset_index().drop('Correlation', axis =1).to_dict('records')


        return {"data" : user_movie_recommend }, HTTPStatus.OK
