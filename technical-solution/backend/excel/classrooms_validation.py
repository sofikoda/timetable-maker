from backend.excel.validation.common import (validate_cell_type, validate_excel_file, validate_columns, 
normalise_string, 
ValidationError)

def import_classrooms_excel(file_path, conn):
    sheet = validate_excel_file(file_path) #check if uploaded file is in the right format
    cursor = conn.cursor() #needed to execute SQL
    expected_columns = ["Classroom Name", "Classroom Category"] #uploaded excel file should correspond to these column names

#cell.value gives actual text inside the cell since each object in the sheet represented as a Cell object 
#so we are loooping through each cell in the first row and collecting its value
    actual_columns = [cell.value for cell in sheet[1]] 
# Validate that the Excel file contains the correct column structure
    validate_columns(actual_columns, expected_columns)

# Iterate through all rows starting from row 2 (row 1 contains headers)
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        classroom_name = normalise_string(row[0].value)
        classroom_category = normalise_string(row[1].value)
# Validate that both values are of the correct type (string)
        validate_cell_type(classroom_name, str, row_idx, "Classroom Name")
        validate_cell_type(classroom_category, str, row_idx, "Classroom Category")

#Check if a classroom_category already exist
        cursor.execute(
            "SELECT category_id FROM classroom_category WHERE category_name = ?", 
            (classroom_category,))
        row_classroom_category = cursor.fetchone()
#If the category exists retreive its ID
        if row_classroom_category: 
            category_id = row_classroom_category[0]
#Otherwise insert it into the database 
        else: 
            cursor.execute(
                "INSERT INTO classroom_category (category_name) VALUES (?)", 
                (classroom_category,))
            category_id = cursor.lastrowid #get the category id

#Check if a classroom already exist 
        cursor.execute( 
            "SELECT classroom_id FROM classroom WHERE classroom_name = ?",
            (classroom_name,))
        row_classroom_name = cursor.fetchone()
#If not insert it into the database
        if not row_classroom_name:  
            cursor.execute(
                "INSERT INTO classroom (classroom_name, category_id) VALUES (?, ?)", 
                (classroom_name, category_id))
    conn.commit() #save all the changes to the datase
