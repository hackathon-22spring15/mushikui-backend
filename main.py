from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

@app.get("/")
def read_root():
    return {"site_intro": "This is description of the site."}

# dateがどんな形式かは要検討
# 今回の例は2022613のような形を想定
@app.get("/expression/{date}/{mode}")
def get_expression(date: int, mode: int):
    operator = ['+', '-', '*', '%']
    random.seed(date)
    x, y = random.randrange(1000000), random.randrange(1000000)
    # mode == 1
    ope = 0
    if mode == 2:
        ope = random.randrange(4)
    if ope == 0:
        z = x + y
    elif ope == 1:
        z = x - y
    elif ope == 2:
        z = x * y
    elif ope == 3:
        z = x % y
    expression = str(x) + operator[ope] + str(y) + "=" + str(z)
    return {"expression": expression}
