from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from itertools import permutations
import os
import json
import datetime

class Expression(BaseModel):
    expression: str

class Check(BaseModel):
    check: List[int] = []

def calc(x: int, y: int, ope: str) -> int:
    if ope == "+":
        return x + y
    elif ope == "-":
        return x - y
    elif ope == "*":
        return x * y
    else:
        return x / y

def scan_exp(nums: str, ope: str, n: str) -> bool:
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

def int_to_date(date: int) -> datetime:
    if len(str(date)) == 7:
        try:
            res = datetime.date(year = date // 1000, month = (date % 1000) // 100, day = date % 100)
            return res
        except ValueError:
            raise HTTPException(status_code=400, detail="You should send correct date.")
    if len(str(date)) == 8:
        try:
            res = datetime.date(year = date // 10000, month = (date % 10000) // 100, day = date % 100)
            return res
        except ValueError:
            raise HTTPException(status_code=400, detail="You should send correct date.")

def date_to_int(date: datetime) -> int:
    return int(date.strftime("%Y%m%d"))

app = FastAPI()
# データベースへの接続
dialect = "mysql"
driver = "pymysql"
username = os.environ["MARIADB_USERNAME"]
password = os.environ["MARIADB_PASSWORD"]
host = os.environ["MARIADB_HOSTNAME"]
port = "3306"
database = os.environ["MARIADB_DATABASE"]
engine = create_engine(dialect + "+" + driver + "://" + username + ":" + password + "@" + host + ":" + port + "/" + database)

Base = declarative_base(bind=engine)

class Problems(Base):
    __tablename__ = "problems"  # テーブル名を指定
    __table_args__ = {"autoload": True} # カラムは自動読み込み

@app.post("/expression/{date}")
def post_expression(date: int, expression: Expression):
    expression = expression.expression

    # 7,8桁以外は後々実装
    if len(str(date)) < 7 or len(str(date)) > 8:
        raise HTTPException(status_code=400, detail="This api can handle only 7/8 digit date time")
    
    # dateをdatetime objectへ
    date_datetime = int_to_date(date)
    
    # セッションの生成
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()
    
    date_expression = session.query(Problems).filter(Problems.date==date_datetime).first()
    
    # 今日の式が存在しなければ
    if date_expression is None:
        # 8桁に揃える
        date = date_to_int(date_datetime)
        random.seed(date)
        with open("expression.json", "r") as f:
            expressions = json.load(f)
        flag = False

        # 最近(一年以内)出されたものは出題しないようにする
        while flag == False:
            ind = random.randrange(len(expressions.keys()))
            date_expression = expressions[str(ind)]
            problem = session.query(Problems).order_by(desc(Problems.date)).filter(Problems.expression==date_expression).first()
            if problem is None:
                exp_data = Problems(expression=date_expression, date = date_datetime)
                session.add(exp_data)
                session.commit()
                flag = True
            elif date - date_to_int(problem.date) > 10000:
                problem.date = date_datetime
                session.commit()
                flag = True
            else:
                continue
        expression_ans = date_expression
    else:
        expression_ans = date_expression.expression

    if not len(expression) == len(expression_ans):
        raise HTTPException(status_code=400, detail="Length of expression unmatched.")
    else:
        res = [0] * (len(expression) - 1)
        pass_equal = 0
        for i in range(len(expression)):
            if expression[i] == "=":
                pass_equal = 1
                continue
            if expression[i] == expression_ans[i]:
                res[i - pass_equal] = 1
            elif expression[i] in expression_ans and not (expression[i] in expression[:i] or expression[expression_ans.find(expression[i])] == expression_ans[expression_ans.find(expression[i])]):
                res[i - pass_equal] = 2
    return {"check": res}
