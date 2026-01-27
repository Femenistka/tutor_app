# DataBase.py
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("app.db")


def connect():
    return sqlite3.connect(DB_PATH)


def _has_column(con, table: str, col: str) -> bool:
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()]
    return col in cols


def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                comment TEXT
            )
        """)

        # payments: добавили pay_method
        con.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                comment TEXT,
                pay_method TEXT NOT NULL DEFAULT 'card'  -- 'cash' | 'card'
            )
        """)

        # если таблица была создана раньше без pay_method — миграция
        if not _has_column(con, "payments", "pay_method"):
            con.execute("ALTER TABLE payments ADD COLUMN pay_method TEXT NOT NULL DEFAULT 'card'")


def add_lesson(name: str, price: float, date: str, comment: Optional[str] = None):
    with connect() as con:
        con.execute(
            "INSERT INTO lessons(name, price, date, comment) VALUES(?,?,?,?)",
            (name, float(price), date, comment)
        )


def add_payment(
    name: str,
    price: float,
    date: str,
    pay_method: str,               # 'cash' | 'card'
    comment: Optional[str] = None
):
    if pay_method not in ("cash", "card"):
        raise ValueError("pay_method must be 'cash' or 'card'")

    with connect() as con:
        con.execute(
            "INSERT INTO payments(name, price, date, comment, pay_method) VALUES(?,?,?,?,?)",
            (name, float(price), date, comment, pay_method)
        )


def get_lessons():
    with connect() as con:
        return con.execute("SELECT * FROM lessons ORDER BY date DESC, id DESC").fetchall()


def get_payments():
    with connect() as con:
        return con.execute("SELECT * FROM payments ORDER BY date DESC, id DESC").fetchall()


def get_balance_by_students():
    # баланс = оплаты - занятия
    with connect() as con:
        return con.execute("""
            SELECT
                n.name,
                COALESCE(p.pay_sum, 0) - COALESCE(l.lesson_sum, 0) AS balance
            FROM (SELECT name FROM lessons UNION SELECT name FROM payments) n
            LEFT JOIN (SELECT name, SUM(price) AS lesson_sum FROM lessons GROUP BY name) l ON l.name = n.name
            LEFT JOIN (SELECT name, SUM(price) AS pay_sum FROM payments GROUP BY name) p ON p.name = n.name
            ORDER BY n.name COLLATE NOCASE
        """).fetchall()
