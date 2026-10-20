from backend.database import get_connection
import random 

""" 
database_data is in the format of [(subject_id, classgroup_id)]
I need to convert it into {subject_id: [classgroup_id1, classgroup_id2]}
"""

#returns a tuple with subject_id and classgroup_id in the format of (subject_id, classroom_id)
def retrieve_classgroups_by_subject(db_connection): 
    cursor = db_connection.cursor()
    cursor.execute("""SELECT subject_id, classgroup_id FROM class_group
    ORDER BY subject_id, classgroup_id""")
    return cursor.fetchall()

def retrieve_classrooms_by_subject(db_connection): 
    cursor = db_connection.cursor() 
    cursor.execute("""SELECT subject_classroom_category.subject_id, classroom.classroom_id 
    FROM classroom 
    JOIN subject_classroom_category ON classroom.category_id = subject_classroom_category.category_id
    ORDER BY subject_id """)
    return cursor.fetchall()


"""To assign one classgroup to a classroom I can use the next mapping: {subject_id: [classgroup_id1, classgroup_id2] etc} 
and the same mapping for classrooms
{subject_id: [classroom_id1, classroom_id2] etc} 
"""
def map_classgroup_into_dictionary(database_data): 
    mapping = {}
# For each tuple, add the classgroup_id to the list for that subject     
    for subject_id, classgroup_id in database_data:
        mapping.setdefault(subject_id, []).append (classgroup_id)
    return mapping

def build_classgroup_mapping():
    conn = get_connection()
    rows = retrieve_classgroups_by_subject(conn)
    conn.close()
    return map_classgroup_into_dictionary(rows)

def map_classroom_into_dictionary(database_data):
    mapping = {}
    for subject_id, classroom_id in database_data: 
# For each tuple, add the classroom_id to the list for that subject
        mapping.setdefault(subject_id, []).append(classroom_id) #important 
    return mapping

def build_classroom_mapping(): 
    conn = get_connection()
    rows = retrieve_classrooms_by_subject(conn)
    conn.close()
    return map_classroom_into_dictionary(rows)

#Finally assign a classroom to a classgroup (classroom category should match subject)
def random_classroom_allocation(classgroup_dictionary, classroom_dictionary):
#Established database connection 
    conn = get_connection()
    try:
        cursor = conn.cursor()
#process each subject and its class groups 
        for subject_id, classgroup_ids in classgroup_dictionary.items():
# Get list of available classrooms for this subject
            room_ids = classroom_dictionary.get(subject_id, [])
# stop if no classrooms exist for that subject
            if not room_ids:
                raise ValueError(f"No classrooms available for subject_id={subject_id}")
#Allocate classrooms 
            for i, classgroup_id in enumerate(classgroup_ids):
#Calculate which classroom to use based on index
                classroom_id = room_ids[i % len(room_ids)]
#update the database with new allocations 
                cursor.execute("""UPDATE class_group SET classroom_id = ?
                    WHERE classgroup_id = ?""", (classroom_id, classgroup_id))
        conn.commit()
#To prevent partial allocation, if there is any errors we should roll back
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close() #close the database 


