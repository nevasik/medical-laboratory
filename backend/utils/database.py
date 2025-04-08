from pymysql import connect, cursors

def get_db_connection():
    return connect(
        host='localhost',
        user='lab_user',
        password='lab_password',
        database='lab_db',
        cursorclass=cursors.DictCursor
    )