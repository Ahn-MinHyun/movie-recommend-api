from flask_restful import Resource
from flask import request
from http import HTTPStatus
from db.db import get_mysql_connection
import json, decimal

# 유저인증을 위한 JWT 라이브러리 import 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt



class MovieList(Resource) :
    # 영화를 조회 할 수 있는건? 써져 있지 않아 일단 아무나 할 수 있도록 
    # 영화 리스트 조회 API
    @jwt_required()
    def get(self):

        # 쿼리 파라미터 page, avg/cnt_order, limit
        page = request.args.get('page', default= 1 , type= int)
        limit = request.args.get('limit', default= 25 ,type=int)
        order = request.args.get('order', default='cnt' ,type = str)
        print('-----------확인용----------')
             
        # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        # 쿼리문 작성
        # 평균을 잡으니 decimal타입이 되어 json으로 포멧되지 않아, floor사용
        query ='''select title, FLOOR(avg(r.rating)) as avg_rating, count(r.rating) as cnt_rating
                    from movie m
                    right join movie_rating r
                    on m.id = r.item_id 
                    group by m.title 
                    order by '''+ order+'''_rating desc '''+ '''limit %s , %s;'''
        
        param = (limit*page, limit)

        # 쿼리문 실행 후 저장
        cursor.execute(query, param)
        records = cursor.fetchall()

        # 데이터베이스 닫기
        cursor.close()
        connection.close()

        print(records)
        # ret = []
        # for row in records:
        #     ret['avg_rating'] = int(ret['avg_rating'])
        # print(ret) 

        return {"count": len(records), "movies" : records}, HTTPStatus.OK

    
class MovieRate(Resource):
    # 영화 리뷰 리스트 보기 
    @jwt_required()
    def get(self,movie_id):
        
        # 쿼리 파라미터 page, limit

        print("-----------확인용------------")

        page = request.args.get('page', default= 1 , type= int)
        limit = request.args.get('limit', default= 25 ,type=int)
        # print(page, type(limit))

        # # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        # 쿼리문 작성
        # 평균을 잡으니 decimal타입이 되어 json으로 포멧되지 않아, floor사용
        query ='''select m.title, u.name, u.gender, r.rating ,cast(created_at as char) as created_at 
                    from movie_rating r
                    join movie m
                        on m.id = r.item_id
                    join movie_user u 
                        on u.id = r.user_id
                    where m.id = %s
                    limit %s, %s;
                    '''
        #페이징 
        param = (movie_id, limit * page, limit)

        # 쿼리문 실행 후 저장
        cursor.execute(query, param)
        records = cursor.fetchall()

        if len(records) == 0:
            return {"error_code": 1}, HTTPStatus.NOT_FOUND

        # 데이터베이스 닫기
        cursor.close()
        connection.close()

        print(records)
        
        return {"movie_rate" : records}

class MovieSearch(Resource):
    # 영화 검색
    @jwt_required()
    def get(self):
        
        # 쿼리 파라미터 page, limit, keword         
        page = request.args.get('page', default= 1 , type= int)
        limit = request.args.get('limit', default= 25 ,type=int)
        keyword = request.args.get('keyword', type = str)

        # 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)
        
        # 쿼리문
        qurey= '''select title, FLOOR(avg(r.rating)) as avg_rating, count(r.rating) as cnt_rating
                    from movie m
                    left join movie_rating r
                        on m.id = r.item_id
                    where m.title like %s 
                    group by m.title 
                    limit %s, %s;'''

        param = ("%"+keyword+"%",limit * page, limit)

        # 쿼리 실행/저장
        cursor.execute(qurey,param)
        records = cursor.fetchall()
        print(records)

        # 닫기 
        cursor.close()
        connection.close()

        return {"searched": records }, HTTPStatus.OK

class MovieRating(Resource):
    # 리뷰 남기기
    @jwt_required()
    def get(self, movie_id):
        data = request.get_json()
        print(data)

        # body 데이터 부족 
        if 'rating' not in data:
            return {"error_code": 1}, HTTPStatus.BAD_REQUEST

        # 별점은 1이상 5이하
        if data['rating'] >5 or data['rating'] < 1:
            return {"error_code": 2}, HTTPStatus.BAD_REQUEST

        user_id = get_jwt_identity()

        # 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)
        
        # 쿼리문
        qurey= ''' insert into 
                    movie_rating (user_id, item_id, rating) 
                            values (%s, %s, %s);'''
        param = (user_id, movie_id ,data['rating'])

        # 쿼리 실행/저장
        cursor.execute(qurey,param)
        connection.commit()


        # 닫기 
        cursor.close()
        connection.close()

        return {"message": "success"}, HTTPStatus.OK

class MovieBookMark(Resource):
    # 즐겨찾기 추가 
    @jwt_required()
    def post(self, movie_id):

        user_id = get_jwt_identity()

        # 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)
        
        # 쿼리문
        qurey= ''' insert into movie_bookmarks(user_id, item_id)
                    values (%s, %s);'''
        param = (user_id, movie_id)

        # 쿼리 실행/저장
        cursor.execute(qurey,param)
        connection.commit()

        # 닫기 
        cursor.close()
        connection.close()

        return {"message": "success"}, HTTPStatus.OK

    @jwt_required()
    def delete(self, movie_id):
    
        user_id = get_jwt_identity()

        # 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)
        
        # 쿼리문
        qurey= ''' delete 
                    from movie_bookmarks 
                    where user_id = %s and item_id = %s;'''
        param = (user_id, movie_id)

        # 쿼리 실행/저장
        cursor.execute(qurey,param)
        connection.commit()

        # 닫기 
        cursor.close()
        connection.close()

        return {"message": "success"}, HTTPStatus.OK
        