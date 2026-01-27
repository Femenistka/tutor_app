# page_analytics.py
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px


DB_PATH = "app.db"


@st.cache_data(ttl=60)
def load_data():

    conn = st.connection("postgresql", type="sql")

    payments = conn.query(
        "SELECT id, name, price, date, comment, pay_method FROM payments;",
        ttl=0
    )
    lessons = conn.query(
        "SELECT id, name, price, date, comment FROM lessons;",
        ttl=0
    )


    conn.close()

    # даты (на всякий случай dayfirst=True)
    lessons["date"] = pd.to_datetime(lessons["date"], errors="coerce", dayfirst=True)
    payments["date"] = pd.to_datetime(payments["date"], errors="coerce", dayfirst=True)

    return lessons, payments


def render():
    st.header("📊 Аналитика")

    lessons, payments = load_data()

    # --- Общая статистика ---
    total_income = float(payments["price"].sum()) if not payments.empty else 0.0
    total_lessons = int(lessons["name"].count()) if not lessons.empty else 0

    c1, c2 = st.columns(2)
    c1.metric("Количество занятий", total_lessons)
    c2.metric("Доход за всё время", f"{total_income:.2f}")

    st.divider()

    # --- Динамика (переключатель) ---
    st.subheader("Динамика")
    scale = st.radio("Масштаб", ["Недели", "Месяцы"], horizontal=True)

    if lessons.empty and payments.empty:
        st.info("Пока нет данных для графиков.")
        return

    if scale == "Недели":
        lessons_per_week = (
            lessons.dropna(subset=["date"])
            .assign(week=lessons["date"].dt.isocalendar().week)
            .groupby("week")["name"]
            .count()
            .reset_index(name="lessons_count")
        )

        payments_per_week = (
            payments.dropna(subset=["date"])
            .assign(week=payments["date"].dt.isocalendar().week)
            .groupby("week")["price"]
            .sum()
            .reset_index(name="payments_sum")
        )

        fig1 = px.line(lessons_per_week, x="week", y="lessons_count", markers=True,
                       title="Занятия по неделям")
        fig2 = px.line(payments_per_week, x="week", y="payments_sum", markers=True,
                       title="Оплаты по неделям")

    else:  # "Месяцы"
        lessons_per_month = (
            lessons.dropna(subset=["date"])
            .assign(month=lessons["date"].dt.month)
            .groupby("month")["name"]
            .count()
            .reset_index(name="lessons_count")
            .sort_values("month")
        )

        payments_per_month = (
            payments.dropna(subset=["date"])
            .assign(month=payments["date"].dt.month)
            .groupby("month")["price"]
            .sum()
            .reset_index(name="payments_sum")
            .sort_values("month")
        )

        fig1 = px.line(lessons_per_month, x="month", y="lessons_count", markers=True,
                       title="Занятия по месяцам")
        fig2 = px.line(payments_per_month, x="month", y="payments_sum", markers=True,
                       title="Оплаты по месяцам")

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- Доли по ученикам (кольцевые диаграммы) ---
    st.subheader("Доли по ученикам")

    lessons_per_person = (
        lessons.groupby("name")["id"]
        .count()
        .reset_index(name="lessons_count")
        .sort_values("lessons_count", ascending=False)
    ) if not lessons.empty else pd.DataFrame(columns=["name", "lessons_count"])

    payments_per_person = (
        payments.groupby("name")["price"]
        .sum()
        .reset_index(name="payments_sum")
        .sort_values("payments_sum", ascending=False)
    ) if not payments.empty else pd.DataFrame(columns=["name", "payments_sum"])

    col1, col2 = st.columns(2)

    with col1:
        if lessons_per_person.empty:
            st.info("Нет занятий для диаграммы.")
        else:
            fig_lessons_pie = px.pie(
                lessons_per_person,
                names="name",
                values="lessons_count",
                hole=0.5,
                title="Доля занятий по ученикам",
            )
            st.plotly_chart(fig_lessons_pie, use_container_width=True)

    with col2:
        if payments_per_person.empty:
            st.info("Нет оплат для диаграммы.")
        else:
            fig_payments_pie = px.pie(
                payments_per_person,
                names="name",
                values="payments_sum",
                hole=0.5,
                title="Доля дохода по ученикам",
            )
            st.plotly_chart(fig_payments_pie, use_container_width=True)
