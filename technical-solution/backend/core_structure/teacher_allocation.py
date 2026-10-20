from backend.database import get_connection
from backend.core_structure.classroom_allocation import build_classgroup_mapping
import random 
import sqlite3

def retrieve_teachers_by_subject(db_connection): 
    cursor = db_connection.cursor() 

    cursor.execute("""SELECT subject_id, teacher_id
                    FROM teacher_subject
                    ORDER BY subject_id""")
#return a list of tuples such as: [(1,4), (1,6) etc]
    return cursor.fetchall()

def map_teacher_into_dictionary(database_data): 
    mapping = {}
    for subject_id, teacher_id in database_data:
# setdefault ensures that the subject key exists in the dictionary
# and initialises it with an empty list if necessary 
        mapping.setdefault(subject_id, []).append(teacher_id)
    return mapping #returns {1: [4,6], 2: [3,7]}

#Building the final teacher mapping dictionary
def build_teacher_mapping(): 
    conn = get_connection()
    rows = retrieve_teachers_by_subject(conn)
    conn.close()
    return map_teacher_into_dictionary(rows)

def random_teacher_allocation(teacher_dictionary, classgroup_dictionary):
    conn = get_connection()
    try:
        cursor = conn.cursor()
#Loop through each subject and its class groups
        for subject_id, classgroup_ids in classgroup_dictionary.items():
#Retrieve teachers available for that subject
            teacher_ids = teacher_dictionary.get(subject_id, [])

#If no teachers are available for a subject, the user schoould reassemple 
#the school structure, since there are not enough teachers
            if not teacher_ids:
                raise ValueError(f"No teachers available for subject_id={subject_id}")
#Assign teachers sequentially to class groups 
            for i, classgroup_id in enumerate(classgroup_ids):

#Cycle through teacher list 
                teacher_id = teacher_ids[i % len(teacher_ids)]
#Updating the database with assigned teachers 
                cursor.execute("""
                    UPDATE class_group
                    SET teacher_id = ?
                    WHERE classgroup_id = ?
                """, (teacher_id, classgroup_id))

        conn.commit() #save the changes to the database
    except Exception:
        conn.rollback() #if there is an error do NOT save anything to the database
        raise
    finally:
        conn.close() #Close the database




