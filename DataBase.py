# DataBase.py (фрагменты)
import streamlit as st
from sqlalchemy import text


def _conn():
    return st.connection("postgresql", type="sql")




def init_db():
    conn = _conn()
    with conn.session as s:
        s.execute(text("""
            CREATE TABLE IF NOT EXISTS lessons (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                date DATE NOT NULL,
                comment TEXT
            );
        """))

        s.execute(text("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                date DATE NOT NULL,
                comment TEXT,
                pay_method TEXT NOT NULL DEFAULT 'card'
            );
        """))
        s.commit()



def add_lesson(name: str, price: float, date: str, comment: str | None = None):
    conn = _conn()
    with conn.session as s:
        s.execute(
            text("INSERT INTO lessons (name, price, date, comment) VALUES (:name, :price, :date, :comment);"),
            {"name": name, "price": float(price), "date": date, "comment": comment},
        )
        s.commit()


def add_payment(name: str, price: float, date: str, pay_method: str, comment: str | None = None):
    conn = _conn()
    with conn.session as s:
        s.execute(
            text("""INSERT INTO payments (name, price, date, comment, pay_method)
                    VALUES (:name, :price, :date, :comment, :pay_method);"""),
            {"name": name, "price": float(price), "date": date, "comment": comment, "pay_method": pay_method},
        )
        s.commit()



def get_lessons():
    conn = _conn()
    return conn.query(
        "SELECT id, name, price, date, comment FROM lessons ORDER BY date DESC, id DESC;",
        ttl=0,
    )


def get_payments():
    conn = _conn()
    return conn.query(
        "SELECT id, name, price, date, comment, pay_method FROM payments ORDER BY date DESC, id DESC;",
        ttl=0,
    )


def get_balance_by_students():
    """
    Баланс по ученикам: sum(payments.price) - sum(lessons.price)
    Возвращает DataFrame со столбцами: name, balance
    """
    conn = _conn()
    return conn.query(
        """
        SELECT
            n.name,
            COALESCE(p.pay_sum, 0) - COALESCE(l.lesson_sum, 0) AS balance
        FROM (
            SELECT name FROM lessons
            UNION
            SELECT name FROM payments
        ) n
        LEFT JOIN (
            SELECT name, SUM(price) AS lesson_sum
            FROM lessons
            GROUP BY name
        ) l ON l.name = n.name
        LEFT JOIN (
            SELECT name, SUM(price) AS pay_sum
            FROM payments
            GROUP BY name
        ) p ON p.name = n.name
        ORDER BY n.name;
        """,
        ttl=0,
    )

