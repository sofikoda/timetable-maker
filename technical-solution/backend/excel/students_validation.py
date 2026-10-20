from backend.excel.validation.common import (
    validate_excel_file,
    validate_columns,
    validate_cell_type,
    normalise_string,
    ValidationError)

def import_students_excel(file_path, conn):
    sheet = validate_excel_file(file_path) #checks if the uploaded file is in the rigth format 
    cursor = conn.cursor() #needed to execute SQL

    #uploaded excel file should correspond to these column names
    expected_columns = ["First Name", "Last Name", "Subject", "Year Group"] 

    actual_columns = [cell.value for cell in sheet[1]]
    validate_columns(actual_columns, expected_columns)

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        #Reading the values
        first_name = normalise_string(row[0].value)
        last_name = normalise_string(row[1].value)
        
        subject_name = normalise_string(row[2].value)
        year_group = row[3].value

        #Data type validation of each cell 
        validate_cell_type(first_name, str, row_idx, "First Name")
        validate_cell_type(last_name, str, row_idx, "Last Name")
        validate_cell_type(subject_name, str, row_idx, "Subject")
        validate_cell_type(year_group, int, row_idx, "Year Group")
        
        # Ensure subject exists
        cursor.execute(
            "SELECT subject_id FROM subject WHERE subject_name = ?",
            (subject_name,))
        row_subject = cursor.fetchone()
#Get the subject_id
        if row_subject:
            subject_id = row_subject[0]
        else:
#if the subject is not found insert it into the database
            cursor.execute(
                "INSERT INTO subject (subject_name) VALUES (?)",
                (subject_name,))
            subject_id = cursor.lastrowid

        # Ensure student exists
        cursor.execute(
            """
            SELECT student_id FROM student
            WHERE first_name = ? AND last_name = ? AND year_group = ?
            """,
            (first_name, last_name, year_group))
        row_student = cursor.fetchone()

        if row_student:
            student_id = row_student[0]
        else:
#If there is no record about a student insert the details into the database
            cursor.execute(
                """
                INSERT INTO student (first_name, last_name, year_group)
                VALUES (?, ?, ?)
                """,
                (first_name, last_name, year_group))
            student_id = cursor.lastrowid

        # Ensure student–subject link does not already exist
        cursor.execute(
            """
            SELECT 1 FROM student_subject
            WHERE student_id = ? AND subject_id = ?
            """,
            (student_id, subject_id))

        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO student_subject (student_id, subject_id)
                VALUES (?, ?)
                """,
                (student_id, subject_id))

    conn.commit()
