import sqlite3
from pathlib import Path
from passlib.hash import bcrypt

DB_PATH = Path(__file__).parent / "timetable.db"
#Establish the connection 
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn 
    
#Initialisung the database 
def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # School structure
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS school_structure (
        structure_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        periods_per_day INTEGER NOT NULL,
        timetable_cycle INTEGER NOT NULL, 
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    # Timetable
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetable (
        timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        structure_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(structure_id) REFERENCES school_structure(structure_id)
    )
    """)

    # Classroom category
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classroom_category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL
    )
    """)

    # Classroom
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classroom (
        classroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
        classroom_name TEXT NOT NULL,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES classroom_category(category_id)
    )
    """)

    # Subject
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subject (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL
    )
    """)

    # Subject-ClassroomCategory junction
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subject_classroom_category (
        subject_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        category_id INTEGER,
        FOREIGN KEY(subject_id) REFERENCES subject(subject_id),
        FOREIGN KEY(category_id) REFERENCES classroom_category(category_id)
    )
    """)

    # Teacher
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    )
    """)

    # Teacher-Subject junction
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_subject (
        teacher_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        subject_id INTEGER,
        FOREIGN KEY(teacher_id) REFERENCES teacher(teacher_id),
        FOREIGN KEY(subject_id) REFERENCES subject(subject_id)
    )
    """)

    # Student
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        year_group INTEGER NOT NULL
    )
    """)

    # Student-Subject junction
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_subject (
        student_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES student(student_id),
        FOREIGN KEY(subject_id) REFERENCES subject(subject_id)
    )
    """)

    # ClassGroup
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_group (
        classgroup_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        year_group INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        teacher_id INTEGER,
        classroom_id INTEGER,
        FOREIGN KEY(subject_id) REFERENCES subject(subject_id),
        FOREIGN KEY(teacher_id) REFERENCES teacher(teacher_id),
        FOREIGN KEY(classroom_id) REFERENCES classroom(classroom_id)
    )
    """)

    # Student-ClassGroup allocation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_class_allocation (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        classgroup_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES student(student_id),
        FOREIGN KEY(classgroup_id) REFERENCES class_group(classgroup_id)
    )
    """)

    # TimetableSlot
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetable_slot (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timetable_id INTEGER,
        classgroup_id INTEGER,
        teacher_id INTEGER,
        classroom_id INTEGER,
        day TEXT NOT NULL,
        period TEXT NOT NULL,
        FOREIGN KEY(timetable_id) REFERENCES timetable(timetable_id),
        FOREIGN KEY(classgroup_id) REFERENCES class_group(classgroup_id),
        FOREIGN KEY(teacher_id) REFERENCES teacher(teacher_id),
        FOREIGN KEY(classroom_id) REFERENCES classroom(classroom_id)
    )
    """)

    connection.commit()
    connection.close()

# Inserting the users datails to the database 
def create_user(first_name, last_name, email, password):
    connection = get_connection()
    cursor = connection.cursor()
    hashed_password = bcrypt.hash(password)
    cursor.execute(
        "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
        (first_name, last_name, email, hashed_password)
    )
    user_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return user_id 

def login_user(email, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT user_id,password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    connection.close()

    if not result:
        return None
    user_id, hashed_password = result 
    
    if bcrypt.verify(password, hashed_password): 
        return user_id 
    return None 
   
def insert_school_structure(user_id, periods_per_day, timetable_cycle): 
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT structure_id FROM school_structure WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row:
        structure_id = row[0]
        cur.execute("""
            UPDATE school_structure
            SET periods_per_day = ?, timetable_cycle = ?
            WHERE user_id = ?
        """, (periods_per_day, timetable_cycle, user_id))
    else:
        cur.execute("""
            INSERT INTO school_structure (user_id, periods_per_day, timetable_cycle)
            VALUES (?, ?, ?)
        """, (user_id, periods_per_day, timetable_cycle))
        structure_id = cur.lastrowid

    conn.commit()
    conn.close()
    return structure_id

def create_timetable(user_id, structure_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT timetable_id FROM timetable WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()

    if row:
        timetable_id = row[0]
    else:
        cursor.execute(
            """
            INSERT INTO timetable (user_id, structure_id)
            VALUES (?, ?)
            """,
            (user_id, structure_id)
        )
        timetable_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return timetable_id

def retrieve_subject_names(db_connection): 
    cursor = db_connection.cursor()
    cursor.execute("SELECT subject_id, subject_name FROM subject") 
    return {sid: name for sid, name in cursor.fetchall()} 

def retrieve_student_names(db_connection): 
    cursor = db_connection.cursor()
    cursor.execute("SELECT student_id, first_name, last_name FROM student")
    return {sid: f"{fn} {ln}" for sid, fn, ln in cursor.fetchall()}

def has_imported_data(user_id): 
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute ("SELECT 1 FROM school_structure WHERE user_id = ? LIMIT 1 ", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None 

def retrieve_student_year_groups(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT student_id, year_group FROM student")
    return {student_id: year_group for student_id, year_group in cursor.fetchall()}



