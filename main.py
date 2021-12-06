from collections import defaultdict
import copy
import itertools
import logging
import math
import pprint
import numpy as np
import random
import sys

import school
import student
from helpers import init_agents
import argparse

# main system
def main(args):
    # initialize student and school class instances
    students, schools = init_agents(args)

    # run early action round
    early_action(students, schools)

    # run regular decision round
    regular_decision(students, schools)

    # calculate matriculation
    matriculation(students, schools)

    stats(args, students, schools)

def early_action(students, schools):
    # for each school, store the list of students who send it a proposal
    school_proposals = [[]] * len(schools)
    for student in students:
        school_proposals[student.early_action()].append(student.id)

    # iterate through the list and get acceptances/rejections
    for school, proposals in enumerate(school_proposals):
        accepted_students, rejected_students = schools[school].early_action(proposals)
        for id in accepted_students:
            students[id].accepted.append(school)
        for id in rejected_students:
            students[id].rejected.append(school)

def regular_decision(students, schools):
    # for each school, store the list of students who send it a proposal
    school_proposals = [[]] * len(schools)
    for student in students:
        proposals = student.regular_decision()
        for school in proposals:
            school_proposals[school].append(student.id)

    # iterate through the list and get acceptances/rejections
    for school, proposals in enumerate(school_proposals):
        accepted_students, rejected_students = schools[school].regular_decision(proposals)
        for id in accepted_students:
            students[id].accepted.append(school)
        for id in rejected_students:
            students[id].rejected.append(school)

def matriculation(students, schools):
    for student in students:
        matriculated = student.matriculate()
        if matriculated:
            schools[matriculated].matriculated.append(student.id)

def stats(args, students, schools):
    naive_ranks = [student.matriculation_rank for student in students[0:args.students[0]]]
    naive_avg = sum(naive_ranks) / len(naive_ranks) if len(naive_ranks) else -1
    safety_ranks = [student.matriculation_rank for student in students[args.students[0]:args.students[1]]]
    safety_avg = sum(safety_ranks) / len(safety_ranks) if len(safety_ranks) else -1
    prediction_ranks = [student.matriculation_rank for student in students[args.students[1]:args.students[2]]]
    prediction_avg = sum(prediction_ranks) / len(prediction_ranks) if len(prediction_ranks) else -1
    print(f'Naive Average Rank: {naive_avg:.2f}\nSafety Average Rank: {safety_avg:.2f}\nPrediction Average Rank: {prediction_avg:.2f}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-avb", "--mean-student-budget", default=10, help="Set the Mean Student Budget to an Integer")
    parser.add_argument("-mb", "--max-student-budget", default=30, help="Set the Mean Student Budget to an Integer")
    parser.add_argument("-avc", "--mean-school-cap", default=50, help="Set the School Capacity to an Integer")
    parser.add_argument("-st", "--students", nargs=3, type=int) # Naive, Safety, Prediction
    parser.add_argument("-sc", "--schools", nargs=1, type=int) # Naive
    main(parser.parse_args())
