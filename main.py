from typing import List
from urllib import response
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import datetime

class Expression(BaseModel):
    expression: str

class Check(BaseModel):
    check: List[int] = []

class PosEqual(BaseModel):
    pos: int

def int_to_date(date: int) -> datetime.date:
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

def date_to_int(date: datetime.date) -> int:
    return int(date.strftime("%Y%m%d"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def read_root():
    return {"site_intro": "This is description of the site."}

@app.get("/expression/{date}", response_model=PosEqual, response_model_exclude_unset=True)
def get_equal_daily(date: int):
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
        with open("expressions_6blanks.json", "r") as f:
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
            elif abs(date - date_to_int(problem.date)) > 10000:
                problem.date = date_datetime
                session.commit()
                flag = True
            else:
                continue
        expression_ans = date_expression
    else:
        expression_ans = date_expression.expression
    pos_equal = expression_ans.find(("="))
    return {"pos": pos_equal}

@app.post("/expression/{date}", response_model=Check, response_model_exclude_unset=True)
def post_expression_daily(date: int, expression: Expression):
    expr = expression.expression

    # 7,8桁以外は後々実装
    if len(str(date)) < 7 or len(str(date)) > 8:
        raise HTTPException(status_code=400, detail="This api can handle only 7/8 digit date time")
    
    # dateをdatetime objectへ
    date_datetime = int_to_date(date)
    
    # セッションの生成
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()
    
    date_expression = session.query(Problems).filter(Problems.date==date_datetime).first()
    
    expression_ans = date_expression.expression

    # 今日の式が存在しなければ
    if date_expression is None:
        raise HTTPException(status_code=400, detail="You looks trying to get answer with wrong way.")
    else:
        expression_ans = date_expression.expression

    if not len(expr) == len(expression_ans):
        raise HTTPException(status_code=400, detail="Length of expr unmatched.")
    else:
        res = [0] * (len(expr) - 1)
        pass_equal = 0
        for i in range(len(expr)):
            if expr[i] == "=":
                if not expression_ans[i] == "=":
                    raise HTTPException(status_code=400, detail="Your equal position unmatched.")
                pass_equal = 1
                continue
            if expr[i] == expression_ans[i]:
                res[i - pass_equal] = 1
            elif expr[i] in expression_ans and not (expr[i] in expr[:i] or expr[expression_ans.find(expr[i])] == expression_ans[expression_ans.find(expr[i])]):
                res[i - pass_equal] = 2
    return {"check": res}

"""
memo:
random生成について、
1. seed値固定なら同じ式が返るのでデータベースを使わない <- now
2. データベースを使う(dateはランダム生成で適当な8桁を生成する)
3. データベースを使う(使わないdateを割り当てて、idで管理)
4. データベースを使う(新たなテーブルを用意する)
"""
@app.get("/expression/random/{seed}", response_model=PosEqual, response_model_exclude_unset=True)
def get_equal_random(seed: int):
    random.seed(seed)
    with open("expressions_6blanks.json", "r") as f:
            expressions = json.load(f)
    ind = random.randrange(len(expressions.keys()))
    expr = expressions[str(ind)]
    pos_equal = expr.find("=")
    return {"pos": pos_equal}

@app.post("/expression/random/{seed}", response_model=Check, response_model_exclude_unset=True)
def post_expression_random(seed: int, expression: Expression):
    expr = expression.expression

    random.seed(seed)
    with open("expressions_6blanks.json", "r") as f:
            expressions = json.load(f)
    ind = random.randrange(len(expressions.keys()))
    expression_ans = expressions[str(ind)]
    
    if not len(expr) == len(expression_ans):
        raise HTTPException(status_code=400, detail="Length of expr unmatched.")
    else:
        res = [0] * (len(expr) - 1)
        pass_equal = 0
        for i in range(len(expr)):
            if expr[i] == "=":
                if not expression_ans[i] == "=":
                    raise HTTPException(status_code=400, detail="Your equal position unmatched.")
                pass_equal = 1
                continue
            if expr[i] == expression_ans[i]:
                res[i - pass_equal] = 1
            elif expr[i] in expression_ans and not (expr[i] in expr[:i] or expr[expression_ans.find(expr[i])] == expression_ans[expression_ans.find(expr[i])]):
                res[i - pass_equal] = 2
    return {"check": res}
