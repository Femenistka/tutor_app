# page_lessons.py
import streamlit as st
from datetime import date

import DataBase as db
from students_store import load_students


def render():
    st.header("Добавить занятие")

    students = load_students()
    names = [s["name"] for s in students]
    if not names:
        st.warning("Список учеников пуст.")
        return

    # --- init state ---
    if "lesson_name" not in st.session_state:
        st.session_state.lesson_name = names[0]
    if "lesson_prev_name" not in st.session_state:
        st.session_state.lesson_prev_name = None
    if "lesson_price" not in st.session_state:
        st.session_state.lesson_price = float(next(s for s in students if s["name"] == names[0]).get("price", 0))

    # выбор ученика вне формы
    name = st.selectbox("Имя", options=names, key="lesson_name")
    student = next(s for s in students if s["name"] == name)
    default_price = float(student.get("price", 0))

    # авто-подстановка цены при смене имени
    if st.session_state.lesson_prev_name != name:
        st.session_state.lesson_price = default_price
        st.session_state.lesson_prev_name = name

    with st.form("lesson_form", clear_on_submit=False):
        price = st.number_input("Цена", min_value=0.0, step=5.0, key="lesson_price")
        d = st.date_input("Дата", value=date.today())
        comment = st.text_input("Комментарий (необяз.)")
        ok = st.form_submit_button("Сохранить", type="primary")

    if ok:
        if not name or not name.strip():
            st.error("Имя обязательно")
            return
        if price <= 0:
            st.error("Цена должна быть > 0")
            return

        try:
            # ВАЖНО: передаём d (datetime.date), НЕ isoformat()
            db.add_lesson(name.strip(), float(price), d, comment.strip() or None)
            st.success("Занятие сохранено")
        except Exception as e:
            st.error(f"{type(e).__name__}: {str(e)[:250]}")

    st.subheader("Последние занятия")
    try:
        st.dataframe(db.get_lessons(), use_container_width=True)
    except Exception as e:
        st.error(f"{type(e).__name__}: {str(e)[:250]}")
