from itertools import product
import json

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
    elif n==2:
        try:
            if ope[0] in "+-" and ope[1] in "*/":
                res = calc(int(nums[0]), calc(int(nums[1]), int(nums[2]), ope[1]), ope[0]) == int(nums[3])
            else:
                res = calc(calc(int(nums[0]), int(nums[1]), ope[0]), int(nums[2]), ope[1]) == int(nums[3])
            return res
        except:
            return False

def scan_exp2(n1, n2, n3, ope, n):
    if n == 0:
        try:
            res = calc(int(n1), int(n2), ope) == int(n3)
            return res
        except:
            return False
    elif n == 1:
        try:
            res = int(n1) == calc(int(n2), int(n3), ope)
            return res
        except:
            return False

expressions = dict()
num = 0
for l in product("0123456789", repeat=4):
    for m in product("+-/*", repeat=2):
        for n in range(3):
            ope = "=" + "".join(m)
            ope = ope[n % 3] + ope[(n + 2) % 3] + ope[(n + 1) % 3]
            m = [o for o in ope if not o == "="]
            if scan_exp(l, m, n):
                expression = l[0] + ope[0] + l[1] + ope[1] + l[2] + ope[2] + l[3]
                expressions[num] = expression
                num += 1

def scan_exp2(n1, n2, n3, ope, n):
    if n == 0:
        try:
            res = int(n1) == calc(int(n2), int(n3), ope)
            return res
        except:
            return False
    elif n == 1:
        try:
            res = calc(int(n1), int(n2), ope) == int(n3)
            return res
        except:
            return False

for l in product("0123456789", repeat=5):
    for m in ["+","-","*","/"]:
        for n in range(2):
            # 1=2ope2 1ope2=2 2=1ope2 2ope1=2 2=2ope1 2ope2=1
            # 愚直に実装した方が間違えなさそう
            ope = m
            l = "".join(l)
            if scan_exp2(l[:1], l[1:3], l[3:], ope, n):
                if l[1] == "0" or l[3] == "0":
                    pass
                elif n == 0:
                    expression = l[:1] + "=" + l[1:3] + ope + l[3:]
                    expressions[num] = expression
                    num += 1
                elif n == 1:
                    expression = l[:1] + ope + l[1:3] + "=" + l[3:]
                    expressions[num] = expression
                    num += 1
            if scan_exp2(l[:2], l[2:3], l[3:], ope, n):
                if l[0] == "0" or l[3] == "0":
                    pass
                elif n == 0:
                    expression = l[:2] + "=" + l[2:3] + ope + l[3:]
                    expressions[num] = expression
                    num += 1
                elif n == 1:
                    expression = l[:2] + ope + l[2:3] + "=" + l[3:]
                    expressions[num] = expression
                    num += 1
            if scan_exp2(l[:2], l[2:4], l[4:], ope, n):
                if l[0] == "0" or l[2] == "0":
                    pass
                elif n == 0:
                    expression = l[:2] + "=" + l[2:4] + ope + l[4:]
                    expressions[num] = expression
                    num += 1
                elif n == 1:
                    expression = l[:2] + ope + l[2:4] + "=" + l[4:]
                    expressions[num] = expression
                    num += 1

from collections import Counter

res = {}
i = 0
for k, v in expressions.items():
    c = Counter(v)
    if max(c.values()) < 3:
        res[i] = v
        i += 1

with open("./expressions_6blanks.json", mode="w") as f:
    json.dump(res, f)
