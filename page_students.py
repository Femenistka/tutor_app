# page_students.py
import streamlit as st
from students_store import load_students, add_student, delete_student


def render():
    st.header("👥 Ученики (справочник)")

    students = load_students()
    st.dataframe(students, use_container_width=True)

    st.subheader("Добавить / обновить ученика")
    with st.form("add_student_form", clear_on_submit=True):
        name = st.text_input("Имя")
        price = st.number_input("Цена по умолчанию", min_value=0.0, step=1.0, value=0.0)

        cash = st.selectbox(
            "Обычно платит",
            options=[0, 1],
            index=0,
            format_func=lambda x: "Картой/безнал" if x == 0 else "Наличными",
        )

        ok = st.form_submit_button("Сохранить", type="primary")

    if ok:
        if not name.strip():
            st.error("Имя обязательно")
        elif price <= 0:
            st.error("Цена должна быть > 0")
        else:
            add_student(name, float(price), int(cash))
            st.success("Сохранено")
            st.rerun()

    st.subheader("Удалить ученика")
    names = [s["name"] for s in students]
    if names:
        victim = st.selectbox("Кого удалить", options=names)
        if st.button("Удалить", type="secondary"):
            delete_student(victim)
            st.success("Удалено")
            st.rerun()
