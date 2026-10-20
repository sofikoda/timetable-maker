from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.database_sqlalchemy import Base


class Teacher(Base):
    __tablename__ = "teacher"

    teacher_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    timeslots = relationship("Timeslot", back_populates="teacher")


class Student(Base):
    __tablename__ = "student"

    student_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    year_group = Column(Integer)
 #This allows: student.class_allocations to get all class allocations for this student
    class_allocations = relationship("StudentClassAllocation", back_populates="student")


class Classroom(Base):
    __tablename__ = "classroom"

    classroom_id = Column(Integer, primary_key=True)
    classroom_name = Column(String)
#This allows: classroom.timeslots to get all timetable slots in this room
    timeslots = relationship("Timeslot", back_populates="classroom")


class Subject(Base):
    __tablename__ = "subject"

    subject_id = Column(Integer, primary_key=True)
    subject_name = Column(String)


class Classgroup(Base):
    __tablename__ = "class_group"

    classgroup_id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subject.subject_id"))
    year_group = Column(Integer)
    class_name = Column(String)
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"))
    classroom_id = Column(Integer, ForeignKey("classroom.classroom_id"))
# Allows: classgroup.subject to get the Subject object
    subject = relationship("Subject")
    timeslots = relationship("Timeslot", back_populates="classgroup")
    student_allocations = relationship("StudentClassAllocation", back_populates="classgroup")


class Timeslot(Base):
    __tablename__ = "timetable_slot"

    slot_id = Column(Integer, primary_key=True)
    day = Column(String, nullable=False)
    period = Column(Integer, nullable=False)
    classgroup_id = Column(Integer, ForeignKey("class_group.classgroup_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"), nullable=False)
    timetable_id = Column(Integer, nullable=True)
    classroom_id = Column(Integer, ForeignKey("classroom.classroom_id"), nullable=False)

    classgroup = relationship("Classgroup", back_populates="timeslots")
    teacher = relationship("Teacher", back_populates="timeslots")
    classroom = relationship("Classroom", back_populates="timeslots")


class StudentClassAllocation(Base):
    __tablename__ = "student_class_allocation"

    allocation_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.student_id"), nullable=False)
    classgroup_id = Column(Integer, ForeignKey("class_group.classgroup_id"), nullable=False)

    student = relationship("Student", back_populates="class_allocations")
    classgroup = relationship("Classgroup", back_populates="student_allocations")