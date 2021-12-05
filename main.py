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



    # run early action round
    early_action_results, proposal_tracker = round_1(student_list, school_list, student_classes, school_classes)

    # run regular decision round
    final_results = round_2(student_list, school_list, student_classes, school_classes,
                            early_action_results, proposal_tracker)

    # run summary stats
    summary_stats(final_results, students, schools, student_list, school_list)

def early_action(students, schools):
    # for each school, store the list of students who send it a proposal
    school_proposals = [[]] * len(schools)
    for student in students:
        school_proposals[student.early_action()].append(student.id)

    # iterate through the list and get acceptances/rejections
    for school, proposals in enumerate(school_proposals):
        accepted_students, rejected_students = schools[school].early_action(proposals)
        for id in accepted_students:
            students[id].accepted.append(school.id)
        for id in rejected_students:
            students[id].rejected.append(school.id)

def regular_decision(students, schools):
    # for each school, store the list of students who send it a proposal
    school_proposals = [[]] * len(schools)
    for student in students:
        proposals = student.regular_decision()

# regular decision round
def round_2(student_list, school_list, student_classes, school_classes, early_action_results, proposal_tracker):

    # iterate for each student in the student list and return rd preferences
    student_rd = {}
    for student in student_list:

        # get regular decision reports from each student
        s1 = student_classes[student.agent](student.id, student.quality, student.pref, student.const)
        regular_decision = s1.regular_decision(school_list, len(student_list))
        student_rd[student.id] = regular_decision

    # iterate for each school for regular decision
    school_rd = {}
    for school in school_list:

        # iterate over proposals and filter by proposes to the given school
        proposals = []
        for student, proposal in student_rd.items():
            if school.id in proposal:
                proposals.append(student)

        # pull forward early proposals to adjust cap
        early_proposals = proposal_tracker[school.id]

        # get students accepted in regular decision
        s1 = school_classes[school.agent](school.id, school.rank, school.pref, school.cap)
        regular_decision = s1.regular_decision(proposals, early_proposals, len(school_list))
        school_rd[school.id] = regular_decision

    # append acceptance letters for each student to an overall dictionary
    student_accepts = {}
    for student in student_list:
        # keep a running track of student acceptances
        accepts_list = []
        # append early action results if they were accepted before
        if len(early_action_results[student.id]) > 0:
            accepts_list.append(early_action_results[student.id][0])
        for school, results in school_rd.items():
            # check if the student was accepted by each school
            if student.id in results:
                accepts_list.append(school)
        student_accepts[student.id] = accepts_list

    # select final matchings:
    matching = {}
    for student, acceptances in student_accepts.items():

        # print(acceptances)

        # select first school in the ordered preference, if any
        if len(acceptances) > 0:
            matching[student] = acceptances[0]
        else:
            matching[student] = ""

    return matching

# summary statistics
def summary_stats(final_results, students, schools, student_list, school_list):

    # set up agent type summary stats dictionary
    student_agent_dict = {}
    student_agent_count = {}
    school_agent_dict = {}
    school_agent_count = {}
    student_agents = list(set(students))
    school_agents = list(set(schools))
    for student in student_agents:
        student_agent_dict[student] = 0
        student_agent_count[student] = 0
    for school in school_agents:
        school_agent_dict[school] = 0
        school_agent_count[student] = 0

    # iterate through students and calculate mean school rank for each agent type
    for student in student_list:

        # add to student agent count
        student_agent_count[student.agent] += 1

        # add mean student quality value
        if final_results[student.id] == "":
            add = 0
        else:
            add = final_results[student.id]
        student_agent_dict[student.agent] += add

    # mean the final to get average student agent ranks
    student_agent_rank = {}
    for agent, total_rank in student_agent_dict.items():
        student_agent_rank[agent] = total_rank / student_agent_count[agent]
        print(f"{agent} achieves average school rank: {student_agent_rank[agent]}")

    print("#############################################")

    # TODO: average school quality for schools, acceptance rates for schools, etc

    return student_agent_rank

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-avb", "--mean-student-budget", detault=10, help="Set the Mean Student Budget to an Integer")
    parser.add_argument("-mb", "--max-student-budget", detault=30, help="Set the Mean Student Budget to an Integer")
    parser.add_argument("-avc", "--mean-school-cap", default=50, help="Set the School Capacity to an Integer")
    parser.add_argument("-st", "--students", nargs=3) # Naive, Safety, Prediction
    parser.add_argument("-sc", "--schools", nargs=1) # Naive
    main(parser.parse_args())
