#라이브러리
from flask import Flask
from flask_restful import Api
from config.config import Config
from Resource.user import UserJoinResource, UserResource, UserReview, UserLogoutResource, UserBookMarkList, jwt_blocklist
from Resource.movie import MovieList, MovieRate, MovieSearch, MovieRating, MovieBookMark
from Resource.movie_recommender import MovieRecommendation

from flask_jwt_extended import JWTManager

import mysql.connector 
#시작

app = Flask(__name__)


# 1. 환경변수 설정
app.config.from_object(Config)
## 1-1. JWT 환경 설정
jwt = JWTManager(app)

# 2. API설정
api = Api(app)

## 로그인/로그아웃 관리를 위한 jwt설정
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

# 3. 경로연결

# 회원가입 경로
api.add_resource(UserJoinResource,'/v1/movie/join')

# 로그인 경로
api.add_resource(UserResource,'/v1//movie/login')

# 로그아웃 경로
api.add_resource(UserLogoutResource,'/v1/movie/logout')

# 영화 리스트 경로 
api.add_resource(MovieList,'/v1/movie/list') # 쿼리 파라미터 page, avg/cnt_order, limit

# 영화 리뷰 경로
api.add_resource(MovieRate,'/v1/movie/<int:movie_id>') # 쿼리 파라미터 page, limit

# 영화 검색 경로
api.add_resource(MovieSearch,'/v1/movie/search') # 쿼리 파라미터 page, limit, keword

# 영화 별점 작성 경로
api.add_resource(MovieRating,'/v1/movie/<int:movie_id>/rating')

# 유저 리뷰 가져오는 경로
api.add_resource(UserReview, '/v1/movie/user/rating')

# 유저 영화 추천 경로
api.add_resource(MovieRecommendation,'/v1/movie/user/recommendation')

# 유저 영화 북마크 경로
api.add_resource(MovieBookMark,'/v1/movie/user/<int:movie_id>/bookmark')

# 유저 영화 북마크 리스트 경로
api.add_resource(UserBookMarkList,'/v1/movie/user/bookmark') # 쿼리 파라미터 page, limit

if __name__=="__main__":

    app.run(port=5001)
