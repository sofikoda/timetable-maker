# save as test_lessons.py in your technical-solution folder
from backend.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM class_group")
groups = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM timetable_slot")
lessons = cursor.fetchone()[0]

conn.close()

print(f"Groups: {groups}")
print(f"Lessons: {lessons}")
print(f"{lessons} == {groups} × 9? {lessons == groups * 9}")