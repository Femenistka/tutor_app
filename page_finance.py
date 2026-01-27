# page_finance.py
import streamlit as st
import pandas as pd

import DataBase as db
from students_store import load_students


def _to_df(obj, cols):
    """Принимает DataFrame или list/tuple и возвращает DataFrame с нужными колонками."""
    if isinstance(obj, pd.DataFrame):
        return obj.copy()
    if obj is None:
        return pd.DataFrame(columns=cols)
    # если это список строк из sqlite fetchall()
    return pd.DataFrame(list(obj), columns=cols)


def render():
    st.header("📊 Баланс по ученикам")
    st.caption("Все ученики из students.json. Баланс = оплаты − занятия. Занятий в остатке = баланс / цена.")

    students = load_students()
    if not students:
        st.warning("Справочник пуст (students.json).")
        return

    # --- справочник ---
    df_students = pd.DataFrame(students)[["name", "price"]].copy()
    df_students["price"] = pd.to_numeric(df_students["price"], errors="coerce").fillna(0.0)

    # --- БД (Neon возвращает DataFrame) ---
    lessons = db.get_lessons()
    payments = db.get_payments()

    df_l = _to_df(lessons, ["id", "name", "amount", "date", "comment"])
    df_p = _to_df(payments, ["id", "name", "amount", "date", "comment", "pay_method"])

    # на Neon колонки будут price, а не amount -> приведём к одному виду
    if "price" in df_l.columns and "amount" not in df_l.columns:
        df_l = df_l.rename(columns={"price": "amount"})
    if "price" in df_p.columns and "amount" not in df_p.columns:
        df_p = df_p.rename(columns={"price": "amount"})

    # гарантируем нужные столбцы, даже если пусто
    for col in ["name", "amount"]:
        if col not in df_l.columns:
            df_l[col] = pd.Series(dtype="object" if col == "name" else "float")
        if col not in df_p.columns:
            df_p[col] = pd.Series(dtype="object" if col == "name" else "float")

    df_l["amount"] = pd.to_numeric(df_l["amount"], errors="coerce").fillna(0.0)
    df_p["amount"] = pd.to_numeric(df_p["amount"], errors="coerce").fillna(0.0)

    # --- агрегации ---
    l_sum = df_l.groupby("name", as_index=False)["amount"].sum().rename(columns={"amount": "charged"})
    p_sum = df_p.groupby("name", as_index=False)["amount"].sum().rename(columns={"amount": "paid"})

    # --- merge + расчеты ---
    df = (
        df_students
        .merge(p_sum, on="name", how="left")
        .merge(l_sum, on="name", how="left")
        .fillna({"paid": 0.0, "charged": 0.0})
    )

    df["balance"] = df["paid"] - df["charged"]

    df["lessons_left"] = df["balance"] / df["price"]
    df.loc[df["price"] <= 0, "lessons_left"] = pd.NA

    df["status"] = "0"
    df.loc[df["balance"] > 0, "status"] = "Предоплата"
    df.loc[df["balance"] < 0, "status"] = "Долг"

    df["lessons_to_pay"] = 0.0
    df.loc[df["lessons_left"].notna() & (df["lessons_left"] < 0), "lessons_to_pay"] = -df["lessons_left"]

    df["lessons_prepaid"] = 0.0
    df.loc[df["lessons_left"].notna() & (df["lessons_left"] > 0), "lessons_prepaid"] = df["lessons_left"]

    out = df.rename(columns={
        "name": "Ученик",
        "price": "Цена (по умолч.)",
        "paid": "Оплатил",
        "charged": "Начислено",
        "balance": "Баланс (₽)",
        "lessons_left": "Занятий в остатке (±)",
        "status": "Статус",
        "lessons_to_pay": "Занятий должен оплатить",
        "lessons_prepaid": "Занятий оплачено наперёд",
    })[
        ["Ученик", "Цена (по умолч.)", "Оплатил", "Начислено", "Баланс (₽)", "Статус",
         "Занятий в остатке (±)", "Занятий должен оплатить", "Занятий оплачено наперёд"]
    ].copy()

    for col in ["Цена (по умолч.)", "Оплатил", "Начислено", "Баланс (₽)",
                "Занятий в остатке (±)", "Занятий должен оплатить", "Занятий оплачено наперёд"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").round(2)

    out["_grp"] = (out["Баланс (₽)"] >= 0).astype(int)
    out["_abs"] = out["Баланс (₽)"].abs()
    out = out.sort_values(["_grp", "_abs"], ascending=[True, False]).drop(columns=["_grp", "_abs"])

    st.dataframe(out, use_container_width=True)

    total_balance = float(out["Баланс (₽)"].sum())
    total_debt = float(out.loc[out["Баланс (₽)"] < 0, "Баланс (₽)"].sum())
    total_prepay = float(out.loc[out["Баланс (₽)"] > 0, "Баланс (₽)"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Итого баланс", f"{total_balance:.2f}")
    c2.metric("Итого долг", f"{total_debt:.2f}")
    c3.metric("Итого предоплата", f"{total_prepay:.2f}")
