from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import ast
import operator
from datetime import datetime

app = FastAPI()

# 允许前端访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite 数据库
DB_NAME = "calculator.db"


# 请求数据格式
class CalculateRequest(BaseModel):
    expression: str


# -------------------- 数据库初始化 --------------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------- 安全表达式计算 --------------------

allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate_expression(expression: str):

    def eval_node(node):

        if isinstance(node, ast.Expression):
            return eval_node(node.body)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("只允许数字")

        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)

            operator_type = type(node.op)

            if operator_type not in allowed_operators:
                raise ValueError("包含不支持的运算符")

            if operator_type == ast.Div and right == 0:
                raise ZeroDivisionError("不能除以 0")

            return allowed_operators[operator_type](left, right)

        elif isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in allowed_operators:
                raise ValueError("包含不支持的运算符")

            return allowed_operators[operator_type](
                eval_node(node.operand)
            )

        else:
            raise ValueError("非法表达式")

    try:
        parsed = ast.parse(expression, mode="eval")
        return eval_node(parsed)

    except ZeroDivisionError:
        raise

    except Exception:
        raise ValueError("表达式格式错误")


# -------------------- 首页测试接口 --------------------

@app.get("/")
def read_root():
    return {"message": "Backend running"}


# -------------------- 计算接口 --------------------

@app.post("/api/calculate")
def calculate(request: CalculateRequest):

    expression = request.expression.strip()

    if not expression:
        raise HTTPException(
            status_code=400,
            detail="表达式不能为空"
        )

    try:
        result = calculate_expression(expression)

    except ZeroDivisionError:
        raise HTTPException(
            status_code=400,
            detail="不能除以 0"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    # 保存历史记录
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO history
        (expression, result, created_at)
        VALUES (?, ?, ?)
        """,
        (
            expression,
            str(result),
            created_at
        )
    )

    history_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "id": history_id,
        "expression": expression,
        "result": result,
        "created_at": created_at
    }


# -------------------- 查询历史记录 --------------------

@app.get("/api/history")
def get_history():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            expression,
            result,
            created_at
        FROM history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# -------------------- 删除单条历史记录 --------------------

@app.delete("/api/history/{history_id}")
def delete_history(history_id: int):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM history WHERE id = ?",
        (history_id,)
    )

    conn.commit()

    deleted_count = cursor.rowcount

    conn.close()

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="该历史记录不存在"
        )

    return {
        "message": "删除成功"
    }