from backend.database import get_connection
from backend.core_structure.teacher_allocation import (random_teacher_allocation,build_teacher_mapping)
from backend.core_structure.classroom_allocation import (random_classroom_allocation,build_classgroup_mapping,
build_classroom_mapping)

#Hard-coded based on course delivery requirements across all schools
LESSONS_PER_FORTNIGHT = 9 

#This class 
class Lesson:
    def __init__(self, lesson_id, subject_id, classgroup_id, teacher_id, classroom_id, year_group):
        self.lesson_id = lesson_id
        self.subject_id = subject_id
        self.classgroup_id = classgroup_id
        self.teacher_id = teacher_id
        self.classroom_id = classroom_id
        self.year_group = year_group

class TimetableGenerator:
    def __init__(self):
        self.conn = get_connection()
        self.lessons = []
        self.graph = {}
        self.timeslots = []

    def retrieve_school_structure(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT periods_per_day, timetable_cycle FROM school_structure")
        row = cursor.fetchone()
        return row[0], row[1]

#Gets all the classgroups that need to be scheduled 
    def retrieve_classgroups(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT classgroup_id, subject_id, teacher_id, classroom_id, year_group FROM class_group")
        return cursor.fetchall()


    def construct_lessons(self):
        rows = self.retrieve_classgroups() #gets the classgroups
        lesson_counter = 1 #Start lesson UDs from 1
        for row in rows:
            classgroup_id, subject_id, teacher_id, classroom_id, year_group = row
#Create multiple lessons (9) for each class group 
            for _ in range(LESSONS_PER_FORTNIGHT):
                lesson = Lesson(lesson_counter, subject_id, classgroup_id, teacher_id, classroom_id, year_group)
                self.lessons.append(lesson)
                lesson_counter += 1


    def generate_timeslots(self, periods_per_day, timetable_cycle):
#Setting up a colour set, each timeslot has a unique identifier, representing 
#a specific time 
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"] #each timeslot is a colour 
        timeslots = []

        for week in range(1, timetable_cycle + 1):
            for day in days:
                for period in range(1, periods_per_day + 1):

#Creates timeslot string: W1_Mon3 = week 1 monday period 3
                    timeslot = f"W{week}_{day}{period}" #getting a timeslot to be 
                    timeslots.append(timeslot)
        self.timeslots = timeslots


    def build_conflict_graph(self):
        graph = {} #initialising the graph 
        for lesson in self.lessons:
            graph[lesson.lesson_id] = set()
#Compare every pair of lessons (i, j) where i < j
#This avoids duplicate comparisons
        for i in range(len(self.lessons)):
            for j in range(i + 1, len(self.lessons)):
#Constructing the vertices 
                l1 = self.lessons[i]
                l2 = self.lessons[j]
                conflict = False

#Establish a conflict between two vertices if they share the same teacher 
                if l1.teacher_id == l2.teacher_id:
                    conflict = True

#Establish a conflict between two vertices if they share the same classroom 
                if l1.classroom_id == l2.classroom_id:
                    conflict = True

#Establish a conflict between two vertices if they share the same class group
                if l1.classgroup_id == l2.classgroup_id:
                    conflict = True

#If there is a conflict draw an edge between two vertices 
                if conflict:
                    graph[l1.lesson_id].add(l2.lesson_id)
                    graph[l2.lesson_id].add(l1.lesson_id)

        self.graph = graph


    def greedy_colour(self):
#Sort vertices by degree (number of conflicts) in descending order
#Heuristic approach 
        order = sorted(self.graph.keys(),
            key=lambda v: len(self.graph[v]), reverse=True)
        colour_of = {} #stores lesson_id to timeslot mapping
    
#An algorithm gives feedback on why the timetable generation process might fail 
        print(f"Number of lessons: {len(self.lessons)}")
        print(f"Number of timeslots: {len(self.timeslots)}")
#Finding maximum conflicts
        max_conflicts = max(len(neighbors) for neighbors in self.graph.values())
        print(f"Maximum conflicts per lesson: {max_conflicts}")
        print(f"Minimum timeslots needed: {max_conflicts + 1}")
#Go thorugh each vertes in the sorted order 
        for vertex in order:
#Collect colours used by already coloured neighbors
            used_colours = set()
            for neighbour in self.graph[vertex]:
                if neighbour in colour_of:
                    used_colours.add(colour_of[neighbour])
#Find the first available color not used by neighbors
            for colour in self.timeslots:
                if colour not in used_colours:
                    colour_of[vertex] = colour
                    break
            else:
#No colour has been found so the timetable cannot be generated
#Debugging step to see which vertex has failed 
                print(f"Failed to color vertex {vertex}")
                print(f"Used colours: {used_colours}")
                print(f"Available timeslots: {self.timeslots[:10]}...")
                raise ValueError("Timetable cannot be generated")

        return colour_of


    def save_timetable(self, colouring):
        cursor = self.conn.cursor()
        for lesson in self.lessons:
            timeslot = colouring[lesson.lesson_id]
#Get the period and the day from a timeslot string 
            week, rest = timeslot.split("_")
            day = rest[:3]
            period = int(rest[3:])
            day_value = week + "_" + day
#Saving the result of the greedy colouring algorithm into the database 
            cursor.execute("""INSERT INTO timetable_slot (classgroup_id, teacher_id, classroom_id, day, period)
                VALUES (?, ?, ?, ?, ?)""", 
                (lesson.classgroup_id, lesson.teacher_id, lesson.classroom_id, day_value, period))

        self.conn.commit() #save all the changes to the database


    def generate(self):
#Get school parameters 
        periods_per_day, timetable_cycle = self.retrieve_school_structure()
#Generate available timeslots 
        self.generate_timeslots(periods_per_day, timetable_cycle)

# clear any previously generate timetable
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM timetable_slot")
        self.conn.commit()
#Build mappings for allocation
        classgroups = build_classgroup_mapping()
        teachers = build_teacher_mapping()
        classrooms = build_classroom_mapping()
#Run allocations 
        random_teacher_allocation(teachers, classgroups)
        random_classroom_allocation(classgroups, classrooms)
#Reset data stuctures, if the timetable was generated multiple times 
        self.lessons = []
        self.graph = {}
#Build lessons and conflict graph 
        self.construct_lessons()
        self.build_conflict_graph()
#Assign timeslots 
        colouring = self.greedy_colour()
#Save to the database 
        self.save_timetable(colouring)
#Close the database connection 
        self.conn.close()
    

def generate_timetable():
    generator = TimetableGenerator() #creating an object 
    generator.generate() #running its object's method 


