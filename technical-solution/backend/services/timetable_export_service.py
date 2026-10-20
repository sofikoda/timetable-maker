from pathlib import Path

from openpyxl import Workbook
from sqlalchemy.orm import joinedload

from backend.database_sqlalchemy import SessionLocal
from backend.models import (Teacher, Student, Timeslot, StudentClassAllocation, Classgroup)


def get_teacher_timetable_rows(session, first_name, last_name):
    teacher = (
        session.query(Teacher).filter(Teacher.first_name == first_name, 
        Teacher.last_name == last_name).first())

    if teacher is None:
        raise ValueError(f"Teacher '{first_name} {last_name}' was not found.")

    timeslots = (session.query(Timeslot).options(
            joinedload(Timeslot.teacher),
            joinedload(Timeslot.classroom),
            joinedload(Timeslot.classgroup).joinedload(Classgroup.subject))
        .filter(Timeslot.teacher_id == teacher.teacher_id).order_by(Timeslot.day, Timeslot.period).all())

    rows = []
    for slot in timeslots:
        teacher_name = f"{slot.teacher.first_name} {slot.teacher.last_name}"
        classroom_name = getattr(slot.classroom, "classroom_name", "")
        class_name = getattr(slot.classgroup, "class_name", "")

        rows.append({"day": slot.day,
            "period": slot.period,
            "class_name": class_name,
            "teacher_name": teacher_name,
            "classroom_name": classroom_name})

    return rows, f"{teacher.first_name}_{teacher.last_name}"

#Student export 
def get_student_timetable_rows(session, first_name, last_name):
    student = (session.query(Student).filter(
            Student.first_name == first_name,
            Student.last_name == last_name).first())

    if student is None:
        raise ValueError(f"Student '{first_name} {last_name}' was not found.")

    allocations = (session.query(StudentClassAllocation)
        .filter(StudentClassAllocation.student_id == student.student_id).all())

    classgroup_ids = [allocation.classgroup_id for allocation in allocations]

    if not classgroup_ids:
        raise ValueError(
            f"Student '{first_name} {last_name}' is not allocated to any class groups.")

    timeslots = (session.query(Timeslot).options(
            joinedload(Timeslot.teacher),
            joinedload(Timeslot.classroom),
            joinedload(Timeslot.classgroup).joinedload("subject"))
        .filter(Timeslot.classgroup_id.in_(classgroup_ids))
        .order_by(Timeslot.day, Timeslot.period).all())

    rows = []
    for slot in timeslots:
        teacher_name = f"{slot.teacher.first_name} {slot.teacher.last_name}"
        classroom_name = getattr(slot.classroom, "classroom_name", "")
        class_name = getattr(slot.classgroup, "class_name", "")
       # subject_name = getattr(slot.classgroup.subject, "subject_name", "")

        rows.append({
            "day": slot.day,
            "period": slot.period,
            "class_name": class_name,
            "teacher_name": teacher_name,
            "classroom_name": classroom_name,})

    return rows, f"{student.first_name}_{student.last_name}"

#Export everything to excel 
def export_rows_to_excel(rows, output_name):
    if not rows:
        raise ValueError("No timetable data found.")

    output_folder = Path("exports")
    output_folder.mkdir(exist_ok=True)

    file_path = output_folder / f"{output_name}_timetable.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Timetable"

    ws.append(["Day", "Period", "Subject", "Class", "Teacher", "Classroom"])

    for row in rows:
        ws.append([
            row["day"],
            row["period"],
            row["class_name"],
            row["teacher_name"],
            row["classroom_name"]])

    wb.save(file_path)
    return str(file_path)

#Frontend 
def export_person_timetable(person_type, first_name, last_name):
    session = SessionLocal()

    try:
        if person_type == "teacher":
            rows, output_name = get_teacher_timetable_rows(session, first_name, last_name)
        elif person_type == "student":
            rows, output_name = get_student_timetable_rows(session, first_name, last_name)
        else:
            raise ValueError("Person type must be 'teacher' or 'student'.")

        return export_rows_to_excel(rows, output_name)

    finally:
        session.close()