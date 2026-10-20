from backend.database import get_connection
#import matplotlib.pyplot as plt
#import networkx as nx

def retrieve_student_subjects(db_connection):
    cursor = db_connection.cursor() #for SQL execution

    #Get student_id and a corresponding subject_id from student_subject entity
    cursor.execute(
        "SELECT student_id, subject_id FROM student_subject ORDER BY student_id")

    student_subjects = {}
#Query result is in the tuple format (1,3) where 1 is a student_id and 3 is a subject_id 
#However, it has to be converted into dictionary to group all the subject_ids together 
#for a particular student 
    for student_id, subject_id in cursor.fetchall():
        if student_id not in student_subjects:
            student_subjects[student_id] = []
#Each student has the student's subject list, simply add each subject for that student to the list 
        student_subjects[student_id].append(subject_id)
    return student_subjects


def build_conflict_graph(student_subjects):
    graph = {}

    # Add all subjects as vertices
    for subjects in student_subjects.values():
        for s in subjects:
            if s not in graph:
                graph[s] = set()

# Add conflict edges between subjects chosen by the same student
    for subjects in student_subjects.values():
        for i in range(len(subjects)):
            for j in range(i + 1, len(subjects)):
                s1 = subjects[i]
                s2 = subjects[j]
#Adding edges in both directions making an undirected graph
                graph[s1].add(s2)
                graph[s2].add(s1)

    return graph

#Each option block represents a colour 
#By applying greedy colouring the graph gets coloured
def colour_graph(adj_list, num_blocks):
#Creating block names in a readable format (BlockA, BlockB etc)
    colours = [f"Block{chr(ord('A') + i)}" for i in range(num_blocks)]

# Sort vertices by decreasing degree, most constrained subjects get coloured first 
    order = sorted(adj_list.keys(), key=lambda v: len(adj_list[v]), reverse=True)

    colour_of = {}
    for v in order:
#Find out which colours have already been used by neighbouring vertices
        used = {colour_of[u] for u in adj_list[v] if u in colour_of}
#Determine which colours that are still available
        available = [c for c in colours if c not in used]
#Assign the first available colour 
        if available:
            colour_of[v] = available[0]
#If no colour is available, the colouring should fail
        else:
            raise ValueError("Greedy colouring failed")

    return colour_of

def build_option_table():
    number_blocks = 4 #hard coded minimum number of blocks (students can select up to 4 subjcets)
    conn = get_connection() #open database connection
#Get the subject choices in a format of a dictionary
    student_subjects = retrieve_student_subjects(conn)
#Build a conflict graph
    adjacency_list = build_conflict_graph(student_subjects)

#Try to colour the graph, if colouring fails, increase the number of blocks
    while True:
        try:
            colouring = colour_graph(adjacency_list, number_blocks)
            break
        except ValueError:
            number_blocks += 1
#Convert colouring result into readable block structure
#E.g {"BlockA": [1,4,7], "BlockB": [2,5]}
    blocks = {}
    for subject, block in colouring.items():
        blocks.setdefault(block, []).append(subject)
    conn.close()
    return blocks, number_blocks




