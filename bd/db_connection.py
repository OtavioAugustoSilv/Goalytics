import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = "/content/Goalytics/futebol.db"

def conectar():
    return sqlite3.connect(db_path)