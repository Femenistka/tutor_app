# app.py (фрагмент)
import streamlit as st
import DataBase as db

import page_lessons
import page_payments
import page_finance
import page_students
import page_analytics

db.init_db()

st.set_page_config(page_title="Учет репетиторства", page_icon="📘", layout="wide")

# лёгкий CSS (не ломает темы)
st.markdown("""
<style>
section[data-testid="stSidebar"] .stButton>button {
  width: 100%;
  border-radius: 12px;
  padding: 0.6rem 0.8rem;
  font-size: 0.95rem;
}
section[data-testid="stSidebar"] hr {
  margin: 0.6rem 0;
}
</style>
""", unsafe_allow_html=True)


def sidebar_nav():
    st.sidebar.markdown("## 📘 Tutor app")
    st.sidebar.caption("Занятия, оплаты, баланс и справочник учеников")
    st.sidebar.divider()

    # текущая страница в state
    if "page" not in st.session_state:
        st.session_state.page = "lessons"

    def nav_button(label, key):
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.page = key

    nav_button("🧑‍🏫 Занятия", "lessons")
    nav_button("💳 Пополнения", "payments")
    nav_button("🔢 Баланс", "finance")
    nav_button("👥 Ученики", "students")

    st.sidebar.divider()

    nav_button("📊 Аналитика", "Analytics")

    return st.session_state.page


page = sidebar_nav()

if page == "lessons":
    page_lessons.render()
elif page == "payments":
    page_payments.render()
elif page == "finance":
    page_finance.render()
elif page == "Analytics":
    page_analytics.render()
else:
    page_students.render()
