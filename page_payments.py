# page_payments.py
import streamlit as st
from datetime import date

import DataBase as db
from students_store import load_students, default_pay_method


def render():
    st.header("Оплата")

    students = load_students()
    names = [s["name"] for s in students]
    if not names:
        st.warning("Список учеников пуст. Добавь учеников в students.json или на странице 'Ученики'.")
        return

    # --- init state ---
    if "pay_name" not in st.session_state:
        st.session_state.pay_name = names[0]
    if "pay_prev_name" not in st.session_state:
        st.session_state.pay_prev_name = None

    # ВАЖНО: выбор имени вне формы -> автоподстановка срабатывает сразу
    name = st.selectbox("Имя", options=names, key="pay_name")

    student = next(s for s in students if s["name"] == name)
    default_price = float(student.get("price", 0))
    pm_default = default_pay_method(student)  # 'cash' | 'card'

    # если ученик сменился — обновить значения в виджетах
    if st.session_state.pay_prev_name != name:
        st.session_state.pay_price = default_price
        st.session_state.pay_method = pm_default
        st.session_state.pay_prev_name = name

    with st.form("pay_form", clear_on_submit=False):
        price = st.number_input("Сумма", min_value=0.0, step=5.0, key="pay_price")

        pay_method = st.selectbox(
            "Способ оплаты",
            options=["card", "cash"],
            key="pay_method",
            format_func=lambda x: "Карта" if x == "card" else "Наличные",
        )

        d = st.date_input("Дата", value=date.today())
        comment = st.text_input("Комментарий (необяз.)")
        ok = st.form_submit_button("Сохранить", type="primary")

    if ok:
        if price <= 0:
            st.error("Сумма должна быть > 0")
        else:
            db.add_payment(name, float(price), d.isoformat(), pay_method, comment.strip() or None)
            st.success("Пополнение сохранено")

    st.subheader("Последние пополнения")
    st.dataframe(db.get_payments(), use_container_width=True)
