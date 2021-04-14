

#MySQL접속 정보를 딕셔너리 형태로 저장한다.
db_config={ 'host' : 'database-2.cumcickeiqsl.ap-northeast-2.rds.amazonaws.com',
            'database' :'yhdb',
            'user' : 'streamlit',
            'password' :'yh1234'}


class Config :
    DEBUG =True
    PORT = 5002
# 토큰 jwt secret key
    SECRET_KEY = 'we love movie '
    

# 비밀번호 암호화를 위한 변수 설정 => 해킹 방지
salt = 'secret for movie user'

