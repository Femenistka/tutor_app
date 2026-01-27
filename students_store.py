# students_store.py
import json
from pathlib import Path
from typing import Optional

FILE = Path("students.json")


def _ensure_file():
    if not FILE.exists():
        FILE.write_text(json.dumps({"students": []}, ensure_ascii=False, indent=2), encoding="utf-8")


def load_students() -> list[dict]:
    _ensure_file()
    data = json.loads(FILE.read_text(encoding="utf-8"))
    students = data.get("students", [])
    # нормализуем: cash только 0/1
    for s in students:
        s["cash"] = 1 if int(s.get("cash", 0)) == 1 else 0
        s["price"] = float(s.get("price", 0))
        s["name"] = str(s.get("name", "")).strip()
    return [s for s in students if s["name"]]


def save_students(students: list[dict]) -> None:
    FILE.write_text(json.dumps({"students": students}, ensure_ascii=False, indent=2), encoding="utf-8")


def add_student(name: str, price: float, cash: int = 0) -> None:
    name = name.strip()
    if not name:
        return

    cash = 1 if int(cash) == 1 else 0
    students = load_students()

    for s in students:
        if s["name"].lower() == name.lower():
            s["name"] = name
            s["price"] = float(price)
            s["cash"] = cash
            students.sort(key=lambda x: x["name"].lower())
            save_students(students)
            return

    students.append({"name": name, "price": float(price), "cash": cash})
    students.sort(key=lambda x: x["name"].lower())
    save_students(students)


def delete_student(name: str) -> None:
    students = [s for s in load_students() if s["name"] != name]
    save_students(students)


def get_student(name: str) -> Optional[dict]:
    for s in load_students():
        if s["name"] == name:
            return s
    return None


def default_pay_method(student: dict) -> str:
    # cash=1 -> 'cash', иначе 'card'
    return "cash" if int(student.get("cash", 0)) == 1 else "card"
