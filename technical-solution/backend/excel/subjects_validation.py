from backend.excel.validation.common import (
    validate_cell_type, 
    validate_excel_file, 
    validate_columns, 
    normalise_string, 
    ValidationError)

def import_subjects_excel(file_path, conn):
    sheet = validate_excel_file(file_path)
    cursor = conn.cursor()
    expected_columns = ["Subject", "Classroom Category"]
    actual_columns = [cell.value for cell in sheet[1]] 
    validate_columns(actual_columns, expected_columns)

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        # Skip completely empty rows
        if row[0].value is None and row[1].value is None:
            continue
        
        subject_name = normalise_string(row[0].value)
        classroom_category = normalise_string(row[1].value)

        validate_cell_type(subject_name, str, row_idx, "Subject")
        validate_cell_type(classroom_category, str, row_idx, "Classroom Category")

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
        cursor.execute(
            "SELECT category_id FROM classroom_category WHERE category_name = ?", 
            (classroom_category,))

        row_classroom_category = cursor.fetchone()
        if row_classroom_category: 
            category_id = row_classroom_category[0]
        else: 
            cursor.execute(
                "INSERT INTO classroom_category (category_name) VALUES (?)", 
                (classroom_category,))
            category_id = cursor.lastrowid
        cursor.execute(
            "SELECT 1 FROM subject_classroom_category WHERE subject_id = ? AND category_id = ?", 
            (subject_id, category_id))
        if not cursor.fetchone(): 
            cursor.execute(
                "INSERT INTO subject_classroom_category (subject_id, category_id) VALUES (?, ?)",
                (subject_id, category_id))

    conn.commit()
