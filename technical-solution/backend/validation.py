import re

def validate_email(email):
    pattern = r"[a-zA-Z0-9]+@[a-zA-Z]+\.(com)" #regular expressions are used to identify this pattern 
    if (re.search(pattern, email)): #check if user's email satisfy the defined pattern
        return True 
    else: 
        return False


def validate_password(password):
    if (len(password) >= 8 
    and any(c.isupper() for c in password) 
    and any(c.isdigit() for c in password) 
    and any(not c.isalnum() for c in password)): 
        return True 
    else: 
        return False 

#pattern =  r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$" #this is chat gpt pattern