import mysql.connector


def conectar():
    return mysql.connector.connect(
        host="172.16.78.139",
        port=3306,
        user="camilly",
        password="camilly123",
        database="db_techflow"
    )