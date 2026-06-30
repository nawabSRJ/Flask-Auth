import pymysql
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='auth_app',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,    # commits each query immediately, no need to call conn.commit() manually, fine for smaller projects
    )