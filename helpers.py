import school
import student
import random
import math
import numpy as np

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def init_agents(args):
    num_students = sum(args.students)
    num_schools = sum(args.schools)

    student_ids = np.arange(num_students)
    school_ids = np.arange(num_schools)

    student_qualities = softmax(np.random.normal(size=num_students))
    school_qualities = softmax(np.random.normal(size=num_schools))

    student_preferences = [np.random.choice(school_ids, size=num_schools, replace=False, p=school_qualities) for _ in range(num_students)]
    school_preferences = [np.random.choice(student_ids, size=num_students, replace=False, p=student_qualities) for _ in range(num_schools)]

    # produces integers in the range [1, max_student_budget] with a mean of mean_student_budget.
    student_budgets = np.random.binomial(args.max_student_budget, (args.mean_student_budget - 1)/args.max_student_budget, size=num_students) + 1
    
    # produces integers in the range [1, infinity) with a mean of mean_school_cap
    school_caps = np.random.geometric(1/args.mean_school_cap, size=num_schools)

    student_attributes = list(zip(student_ids, student_qualities, student_preferences, student_budgets))
    school_attributes = list(zip(school_ids, school_qualities, school_preferences, school_caps))

    students_naive = [student.Naive(*attrs) for attrs in student_attributes[0:args.students[0]]]
    students_safety = [student.Safety(*attrs) for attrs in student_attributes[args.students[0]:args.students[1]]]
    students_prediction = [student.Prediction(*attrs) for attrs in student_attributes[args.students[1]:args.students[2]]]
    students = students_naive + students_safety + students_prediction

    schools_naive = [school.Naive(*attrs) for attrs in school_attributes]
    schools = schools_naive

    return students, schools
