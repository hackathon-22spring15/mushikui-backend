from fastapi import FastAPI
from pydantic import BaseModel
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from itertools import permutations
import os
import json
import datetime

def calc(x, y, ope):
    if ope == "+":
        return x + y
    elif ope == "-":
        return x - y
    elif ope == "*":
        return x * y
    else:
        return x / y

def scan_exp(nums, ope, n):
    if n == 0:
        try:
            if ope[0] in "+-" and ope[1] in "*/":
                res = int(nums[0]) == calc(int(nums[1]), calc(int(nums[2]), int(nums[3]), ope[1]), ope[0])
            else:
                res = int(nums[0]) == calc(calc(int(nums[1]), int(nums[2]), ope[0]), int(nums[3]), ope[1])
            return res
        except:
            return False
    if n == 1:
        try:
            res = calc(int(nums[0]), int(nums[1]), ope[0]) == calc(int(nums[2]), int(nums[3]), ope[1])
            return res
        except:
            return False
    else:
        try:
            if ope[0] in "+-" and ope[1] in "*/":
                res = calc(int(nums[0]), calc(int(nums[1]), int(nums[2]), ope[1]), ope[0]) == int(nums[3])
            else:
                res = calc(calc(int(nums[0]), int(nums[1]), ope[0]), int(nums[2]), ope[1]) == int(nums[3])
            return res
        except:
            return False


app = FastAPI()
# データベースへの接続
dialect = "mysql"
driver = "pymysql"
username = os.environ["MARIADB_USERNAME"]
password = os.environ["MARIADB_PASSWORD"]
# host = "@localhost"
host = os.environ["MARIADB_HOSTNAME"]
port = "3306"
database = os.environ["MARIADB_DATABASE"]
engine = create_engine(dialect + "+" + driver + "://" + username + ":" + password + "@" + host + ":" + port + "/" + database)

Base = declarative_base(bind=engine)

class Problems(Base):
    __tablename__ = "problems"  # テーブル名を指定
    __table_args__ = {"autoload": True} # カラムは自動読み込み

@app.get("/")
def read_root():
    return {"site_intro": "This is description of the site."}

# dateがどんな形式かは要検討
# 今回の例は20220613のような形を想定
@app.get("/expression/{date}")
def get_expression(date: int):
    # セッションの生成
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()
    # if NOT_EXIST_DATE_EXPRESSION:
    random.seed(date)
    with open("expression.json", "r") as f:
        expressions = json.load(f)
    ind = random.randrange(len(expression.keys()))
    expression = expressions[ind]
        # ADD_EXPRESSION_TO_DB
    # else:
    #     SELECT_EXPRESSION_FROM_DB
    return {"expression": expression}

# 後で消すやつ
@app.get("/test1")
def get_test1_db():
    # セッションの生成
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()
    # 試しにデータ挿入
    expression1 = Problems(expression = "1+4=8-3", date = datetime.date.today())
    session.add(expression1)
    session.commit()
    return {"comment": "successfully inserted"}

@app.get("/test2")
def get_test2_db():
    # セッションの生成
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()
    # delete data
    expressions = session.query(Problems).first()
    try:
        session.delete(expressions)
        session.commit()
    except:
        return {"comment": "failed to delete"}
    return {"comment": "successfully deleted"}



