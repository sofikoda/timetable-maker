from backend.excel.validation.common import (
    validate_excel_file,
    normalise_string,
    validate_columns,
    validate_cell_type)
#Same logic and structure as in students_validation.py

def import_teachers_excel(file_path, conn):
    sheet = validate_excel_file(file_path)
    cursor = conn.cursor()

    expected_columns = ["First Name", "Last Name", "Subject"]
    actual_columns = [cell.value for cell in sheet[1]]
    validate_columns(actual_columns, expected_columns)

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        #Reading values
        first_name = normalise_string(row[0].value)
        last_name = normalise_string(row[1].value)
        subject_name = normalise_string(row[2].value)

 #Validating the datatypes in each cell
        validate_cell_type(first_name, str, row_idx, "First Name")
        validate_cell_type(last_name, str, row_idx, "Last Name")
        validate_cell_type(subject_name, str, row_idx, "Subject")


        #  Ensure subject exists
        cursor.execute(
            "SELECT subject_id FROM subject WHERE subject_name = ?",
            (subject_name,))
        row_subject = cursor.fetchone()

        if row_subject:
            subject_id = row_subject[0]
        else:
            cursor.execute(
                "INSERT INTO subject (subject_name) VALUES (?)",
                (subject_name,))
            subject_id = cursor.lastrowid

        # Ensure teacher exists
        cursor.execute("SELECT teacher_id FROM teacher WHERE first_name = ? AND last_name = ? ",
            (first_name, last_name))
        row_teacher = cursor.fetchone()

        if row_teacher:
            teacher_id = row_teacher[0]
        else:
            cursor.execute("INSERT INTO teacher (first_name, last_name) VALUES (?, ?) ",
                (first_name, last_name))
            teacher_id = cursor.lastrowid

        # Ensure teacher–subject link does not already exist
        cursor.execute("SELECT 1 FROM teacher_subject WHERE teacher_id = ? AND subject_id = ?",
        (teacher_id, subject_id))

        if not cursor.fetchone():
            cursor.execute("INSERT INTO teacher_subject (teacher_id, subject_id) VALUES (?, ?)" ,
            (teacher_id, subject_id))

    conn.commit()
