from this import d
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
    check: List[int]

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


def generate_daily_problem(sc: sessionmaker, date_datetime: datetime.date) -> str:
    with open("expressions_6blanks.json", "r") as f:
        expressions = json.load(f)
    random.seed(datetime.datetime.now())
    date = date_to_int(date_datetime)

    with sc() as session:
        # 最近(一年以内)出されたものは出題しないようにする
        while True:
            ind = random.randrange(len(expressions.keys()))
            date_expression = expressions[str(ind)]
            problem = session.query(Problems).order_by(desc(Problems.date)).filter(Problems.expression==date_expression).first()
            if problem is None:
                exp_data = Problems(expression=date_expression, date = date_datetime)
                session.add(exp_data)
                session.commit()
                return exp_data.expression
            elif abs(date - date_to_int(problem.date)) > 10000:
                exp_data = Problems(expression=date_expression, date = date_datetime)
                session.add(exp_data)
                session.commit()
                return exp_data.expression
            else:
                continue

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

    with SessionClass() as session:
        date_expression = session.query(Problems).filter(Problems.date==date_datetime).first()

    # 今日の式が存在しなければ
    if date_expression is None:
        expression_ans: str = generate_daily_problem(SessionClass, date_datetime)
    else:
        expression_ans: str = date_expression.expression
    pos_equal = expression_ans.find(("="))

    return {"pos": pos_equal}

@app.get("/expression/{date}/answer", response_model=Expression, response_model_exclude_unset=True)
def get_answer_daily(date: int):
    # 7,8桁以外は後々実装
    if len(str(date)) < 7 or len(str(date)) > 8:
        raise HTTPException(status_code=400, detail="This api can handle only 7/8 digit date time")
    
    # dateをdatetime objectへ
    date_datetime = int_to_date(date)

    # セッションの生成
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成

    with SessionClass() as session:
        date_expression = session.query(Problems).filter(Problems.date==date_datetime).first()

    # 今日の式が存在しなければ
    if date_expression is None:
        # 8桁に揃える
        expression_ans = generate_daily_problem(SessionClass, date_datetime)
    else:
        expression_ans = date_expression.expression
    return {"expression": expression_ans}


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

    # 今日の式が存在しなければ
    if date_expression is None:
        session.close()
        raise HTTPException(status_code=400, detail="You looks trying to get answer with wrong way.")
    else:
        expression_ans = date_expression.expression

    if not len(expr) == len(expression_ans):
        session.close()
        raise HTTPException(status_code=400, detail="Length of expr unmatched.")
    else:
        res = [0] * (len(expr) - 1)
        pass_equal = 0
        for i in range(len(expr)):
            if expression_ans[i] == "=":
                if not expr[i] == "=":
                    session.close()
                    raise HTTPException(status_code=400, detail="Your equal position unmatched.")
                pass_equal = 1
                continue
            if expr[i] == expression_ans[i]:
                res[i - pass_equal] = 2
            elif expr[i] in expression_ans:
                res[i - pass_equal] = max(res[i - pass_equal], 1)
        session.close()
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
    with open("expressions_6blanks.json", "r") as f:
            expressions = json.load(f)
    random.seed(seed)
    ind = random.randrange(len(expressions.keys()))
    expr = expressions[str(ind)]
    pos_equal = expr.find("=")
    return {"pos": pos_equal}

@app.get("/expression/random/{seed}/answer", response_model=Expression, response_model_exclude_unset=True)
def get_answer_random(seed: int):
    with open("expressions_6blanks.json", "r") as f:
            expressions = json.load(f)
    random.seed(seed)
    ind = random.randrange(len(expressions.keys()))
    expr = expressions[str(ind)]
    return {"expression": expr}

@app.post("/expression/random/{seed}", response_model=Check, response_model_exclude_unset=True)
def post_expression_random(seed: int, expression: Expression):
    expr = expression.expression
    with open("expressions_6blanks.json", "r") as f:
            expressions = json.load(f)
    random.seed(seed)
    ind = random.randrange(len(expressions.keys()))
    expression_ans = expressions[str(ind)]
    
    if not len(expr) == len(expression_ans):
        raise HTTPException(status_code=400, detail="Length of expr unmatched.")
    else:
        res = [0] * (len(expr) - 1)
        pass_equal = 0
        for i in range(len(expr)):
            if expression_ans[i] == "=":
                if not expr[i] == "=":
                    raise HTTPException(status_code=400, detail="Your equal position unmatched.")
                pass_equal = 1
                continue
            if expr[i] == expression_ans[i]:
                res[i - pass_equal] = 2
            elif expr[i] in expression_ans:
                res[i - pass_equal] = max(res[i - pass_equal], 1)
    return {"check": res}

