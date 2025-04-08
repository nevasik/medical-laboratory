import pymysql
from config import Config

def get_connection():
    return pymysql.connect(**Config.DB_CONFIG)