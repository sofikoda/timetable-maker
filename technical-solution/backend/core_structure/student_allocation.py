from backend.core_structure.option_blocks import retrieve_student_subjects
from backend.database import get_connection, retrieve_student_names, retrieve_subject_names, retrieve_student_year_groups
import math 
from openpyxl import Workbook

#Pure, stripped string with subject name schould be used for class group names
#"Product Design" -> "ProductDesign" 
def sanitise_subject_token(subject_name):
    token = "" #empty string to initialise the tokan 

#Iterate trhough each character in the subject name 
    for ch in subject_name:
#Check if the character is alphabetic 
        if ch.isalpha():
#If it is append it to the token 
            token += ch
    return token 

def build_subject_year_students(student_subjects, student_years):
    subject_year_students = {} #empty fictionary that will store the final data

#Iterate through each student and their chosen subjects
    for student_id, subjects in student_subjects.items():
        # Look up the year group for this student
        year_group = student_years.get(student_id)

        # For each subject the student takes, add them to the 
        # appropriate group based on (subject, year_group) 
        for subject_id in subjects:
#Ceate a composite key using a tuple of (subject_id, year group)
            key = (subject_id, year_group)
#Check if there is already a combination of (subject, year)
            if key not in subject_year_students:

#If it's new, initialise an empty list for this combination
                subject_year_students[key] = []

#Add the current student to the list for this (subject, year) combination
            subject_year_students[key].append(student_id)

    return subject_year_students

"""
Steps: 
1. Work out how many groups are needed using a maximum capacity. 
2. Create that many empty groups. 
3. For each student, place them into the smallest available group. 
This helps keep group sizes balanced. 
Returns: [[student_id, ...], [student_id, ...], ... ] 
""" 
def allocate_groups_greedy(student_ids, max_students):
# Calculate number of groups needed, ceil is used to round up 
    groups_required = math.ceil(len(student_ids) / max_students)
# Create empty groups
    groups = []
    for _ in range(groups_required):
        groups.append([])

# Loop through the students' list and assign students one by one
    for student_id in student_ids:
 # Find all groups that are not yet full
        eligible_groups = [g for g in groups if len(g) < max_students]
#Error handling if something goes wrong 
        if not eligible_groups:
            raise ValueError("No eligible group available")

#Using greedy balancing, choose the smallest group and assign one student to that groupz
        smallest_group = min(eligible_groups, key=len)
        smallest_group.append(student_id)

    return groups

def save_student_allocations_to_db(max_students=20):
    conn = get_connection()
    try:
        cursor = conn.cursor()
#Get all student-subject relationships (which subjects each student takes)
        student_subjects = retrieve_student_subjects(conn)
#Get year group for each student 
        student_years = retrieve_student_year_groups(conn)
#Get mapping of subject_id to subject_name 
        subject_names = retrieve_subject_names(conn)
#Orginise students by subject and year 
        subject_year_students = build_subject_year_students(student_subjects, student_years)

# This will store: (subject_id, year_group, group_index) -> classgroup_id
        classgroup_ids = {}

#Iterate through each subject-year combination
        for (subject_id, year_group) in sorted(subject_year_students.keys()):
#Get the list of student ids for this subject and year 
            student_ids = subject_year_students[(subject_id, year_group)]

#Get the subject name for creating readable class names
            subject_name = subject_names.get(subject_id, f"Subject_{subject_id}")
#Create a clean token from the subjcet name 
            subject_token = sanitise_subject_token(subject_name)
#Split students into groups based on max number of students
            groups = allocate_groups_greedy(student_ids, max_students)
#Create a class group record for each group 
            for group_index in range(1, len(groups) + 1):
    #Generate a meaningful class name 
                class_name = f"{subject_token}{year_group}_{group_index}"
#Insert class group into the database
#Note: teacher_id and classroom_id are initially NULL
# They will be assigned later by the allocation algorithms
                cursor.execute("""INSERT INTO class_group (subject_id, year_group,
                 class_name, teacher_id, classroom_id) VALUES (?, ?, ?, NULL, NULL)""",
                    (subject_id, year_group, class_name),)
#Get the auto-generated ID for the newl created group 
                classgroup_id = cursor.lastrowid

#Store the Id for the later use when allocating students
                classgroup_ids[(subject_id, year_group, group_index)] = classgroup_id

#All the class groups exist now we need to assign students to them
        for (subject_id, year_group) in sorted(subject_year_students.keys()):
#Get the student list again 
            student_ids = subject_year_students[(subject_id, year_group)]
#Split into groups again (same greedy logic)
            groups = allocate_groups_greedy(student_ids, max_students)
#For each group and its assigned students, get the classgroup_id we stored earlier
            for group_index, group_students in enumerate(groups, start=1):
                classgroup_id = classgroup_ids[(subject_id, year_group, group_index)]
#Create an allocation record for each student in this group
                for student_id in group_students:
                    cursor.execute(
                        """INSERT INTO student_class_allocation (student_id, classgroup_id)
                        VALUES (?, ?)""",
                        (student_id, classgroup_id),)
        conn.commit()

    except Exception:
#If anything goes wrong, undo all database changes
#Prevents inconsistent data 
        conn.rollback()
        raise

    finally:
        conn.close() #close the database connection

def build_student_allocations(max_students=20):
    # Open database connection
    conn = get_connection()
# Fetch raw data from database
    try:
#Get mapping of student_id to list of subject_ids 
        student_subjects = retrieve_student_subjects(conn) # Example: {101: [1, 2, 3], 102: [1, 4], ...}
#Get mapping of student_id to year_group 
        student_years = retrieve_student_year_groups(conn) # Example: {101: 10, 102: 10, 103: 11, ...}
#Get mapping of subject_id to subject_name 
        subject_names = retrieve_subject_names(conn)# Example: {1: "Mathematics", 2: "Physics", 3: "Chemistry", ...}
#Get mapping of student_id to full student's name 
        student_names = retrieve_student_names(conn)        # Example: {101: "Eva Smith", 102: "Sofia Jones", ...}

# Group students by subject and year group
# This creates a nested structure: {(subject_id, year): [student_ids]}
# Example: {(1, 10): [101, 102, 103], (1, 11): [201, 202], ...}
        subject_year_students = build_subject_year_students(
            student_subjects, student_years)
        rows = []

# Process each (subject, year_group) combination
#Iterate through all unique pairs 
        for (subject_id, year_group) in sorted(subject_year_students.keys()):
            student_ids = subject_year_students[(subject_id, year_group)]

# Look up readable subject name and build naming token
            subject_name = subject_names.get(subject_id, f"Subject_{subject_id}")
            subject_token = sanitise_subject_token(subject_name)

# Allocate students into balanced groups
            groups = allocate_groups_greedy(student_ids, max_students)

# Generate group names and output rows
            for index, group in enumerate(groups, start=1):
#Create readable class group name 
                group_name = f"{subject_token}{year_group}_{index}"
#For each student in this group, create a row
                for student_id in group:
                    student_name = student_names.get(student_id, str(student_id))
#Add all the info to the tuple that will be used within UI
                    rows.append((group_name, subject_name, year_group, student_name))

        return rows

    finally:
# Always close the database connection
        conn.close()

#This function exports the student alloation data to an Excel file 
#A single sheet contains: Group | Subject | Year Group | Student
def export_student_allocations_to_excel(filepath, rows):
#Create a new excel workbook 
#Workbook() creates an in memory excel file
    wb = Workbook()
    ws = wb.active
#rename the worksheet to a valid name
    ws.title = "Student Allocation"
# Header row
#The order matches the tuple structure from build_student_allocations()
    ws.append(["Group", "Subject", "Year Group", "Student"])

# Freeze header row for easier scrolling
    ws.freeze_panes = "A2"

# Write each allocation as one row
    for group, subject, year_group, student in rows:
        ws.append([group, subject, year_group, student])

# Set column widths for readability
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 26
#Save the excel file to a specific location 
    wb.save(filepath)