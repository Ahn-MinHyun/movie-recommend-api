from flask_restful import Resource
from flask import request
from http import HTTPStatus

# 이메일 형식 체크하기 위한 import
from email_validator import validate_email, EmailNotValidError
from mysql.connector import Error

# 패스워드 비밀번호 암호화 및 체크를 위한 import
from utils import hash_passwd, check_passwd
from db.db import get_mysql_connection

# 유저인증을 위한 JWT 라이브러리 import 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# 로그아웃 기능 구현
from flask_jwt_extended import get_jti


jwt_blocklist = set()


class UserJoinResource(Resource):
    # 회원가입 API
    def post(self):
        data =request.get_json()

        # 필수 입력 체크
        if "name" not in data or "email" not in data or "password" not in data or "gender" not in data:
            return {'error_code': 1 }, HTTPStatus.BAD_REQUEST

        # 1. 이메일 유효한지 체크
        try:
            # Validate.
            valid = validate_email(data['email'])

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error_code': 2 },HTTPStatus.BAD_REQUEST

        # 2. 비밀 번호 암호화
        if len(data["password"]) < 4 or len(data["password"]) > 10:
            return {'error_code': 3 }, HTTPStatus.BAD_REQUEST 

        password = hash_passwd(data['password'])
        # print(password)

        # 3. 데이터 베이스에 저장
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()
            query = ''' insert into movie_user(name, email, password, gender)
                        values (%s, %s, %s, %s);'''
            param = (data['name'],data['email'],password,data['gender'])

            cursor.execute(query,param)
            connection.commit()
            # print('------------------확인용 -----------------')
            #유저아이디 가져오기 
            user_id = cursor.lastrowid
          
            print(user_id)

        except Error as e : 
            print(e)
            return {'error_code': "MySQL"},HTTPStatus.NOT_ACCEPTABLE

        finally:
            cursor.close()
            connection.close()

        access_token = create_access_token(identity = user_id)

        return {'token': access_token }, HTTPStatus.OK


class UserResource(Resource):
    # 로그인 API
    def post(self):
        data = request.get_json()
        print(data)
        if "email" not in data or "password" not in data:
            # 이메일 패스워드 입력이 없는 경우
            return {'error_code': 1 }, HTTPStatus.BAD_REQUEST

        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        try:
            # Validate.
            valid = validate_email(data['email'])

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            # 이메일 형식이 다른경우
            return {'error_code': 2 },HTTPStatus.BAD_REQUEST

        query = '''select id, password
                    from movie_user
                    where email = %s;'''

        param = (data['email'],)

        cursor.execute(query, param)
        records = cursor.fetchall()
    
        if records == []:
            return {'error_code': 3 }, HTTPStatus.NOT_ACCEPTABLE

        cursor.close()
        connection.close()
        
        # JWT를 이용해서 인증토큰을 생성해 준다. 
        

        password = check_passwd(data['password'],records[0]['password'])
        if password is True:

            user_id = records[0]['id']
            access_token = create_access_token(identity=user_id)

            return {'message': 'success', 'token': access_token},HTTPStatus.OK
        else:
            return {'message': 4 },HTTPStatus.NOT_ACCEPTABLE


class UserReview(Resource):
    # 유저의 리뷰 리스트 가져오기 
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        # 쿼리문 작성
        # 평균을 잡으니 decimal타입이 되어 json으로 포멧되지 않아, floor사용
        query ='''select m.title, r.rating, u.id
                    from movie_rating r
                    join movie m
                        on m.id = r.item_id
                    join movie_user u 
                        on u.id = r.user_id
                    where u.id = %s;
                    '''
        #페이징 
        param = (user_id, )

        # 쿼리문 실행 후 저장
        cursor.execute(query, param)
        records = cursor.fetchall()

        # 데이터베이스 닫기
        cursor.close()
        connection.close()

        print(records)
        
        return { "count" : len(records),"movie_rate" : records}


class UserBookMarkList(Resource):
    # 유저의 북마크 리스트 가져오기 
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        # 쿼리문 작성
        # 평균을 잡으니 decimal타입이 되어 json으로 포멧되지 않아, floor사용
        query ='''select m.title
                    from movie_bookmarks b
                    join movie m
                        on m.id = b.item_id
                    where b.user_id = %s;
                    '''
        #페이징 
        param = (user_id, )

        # 쿼리문 실행 후 저장
        cursor.execute(query, param)
        records = cursor.fetchall()

        # 데이터베이스 닫기
        cursor.close()
        connection.close()

        print(records)
        
        return { "count" : len(records),"movie_rate" : records}

class UserLogoutResource(Resource):
    #로그아웃 API
    @jwt_required()
    def post(self):
        # 로그아웃을 위한 레퍼런스를 따라하는 것

        jti = get_jwt()['jti']
        jwt_blocklist.add(jti)

        return {'message':'logout'},HTTPStatus.OK