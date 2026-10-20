import openpyxl
class ValidationError(Exception): #custom exceptio type 
    pass

def validate_excel_file(file_path):
    if not file_path.endswith(".xlsx"):
        raise ValidationError("File must be an .xlsx Excel file")

    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
    except Exception:
        raise ValidationError("Excel file cannot be opened or is corrupted")

    if sheet.max_row < 2:
        raise ValidationError("Excel file contains no data rows")

    return sheet



def validate_columns(actual_columns, expected_columns):
    def clean(col): 
        return str(col).strip().lower()
    actual_col = [clean(c) for c in actual_columns]
    expected_col = [clean(c) for c in expected_columns]
    if actual_col != expected_col:
        raise ValidationError(
            f"Invalid columns.\nExpected: {expected_columns}\nFound: {actual_columns}")


def validate_cell_type(value, expected_type, row, column):
    if value is None or value == '': 
        raise ValidationError(f"Row {row}: {column} cannot be empty")
    if expected_type == str and not isinstance(value, str):
        raise ValidationError(
            f"Row {row}: {column} must be a string")


    if expected_type == int:
        try:
            int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                f"Row {row}: {column} must be an integer"
            )
def normalise_string(value):
    if value is None:
        return ""
    return str(value).strip().lower()



def ensure_entity_exists(entity_id, entity_name):
    if entity_id is None:
        raise ValidationError(f"{entity_name} does not exist")
