from optparse import OptionParser
import copy
import itertools
import logging
import math
import pprint
import numpy as np
import random
import sys
from stunaive import stuNaive
from schnaive import schNaive
# from stusafety import stuSafety
# from stuprediction import stuPrediction

# define a student class
class Student:
    def __init__(self, agent, id, quality, preferences, const):
        self.agent = agent
        self.id = id
        self.quality = quality
        self.pref = preferences
        self.const = const

class School:
    def __init__(self, agent, id, rank, preferences, cap):
        self.agent = agent
        self.id = id
        self.rank = rank
        self.pref = preferences
        self.cap = cap

# parse the school and student agents
def parse_agents(args):

    ans = []
    for c in args:
        s = c.split(',')
        if len(s) == 1:
            ans.extend(s)
        elif len(s) == 2:
            name, count = s
            ans.extend([name]*int(count))
        else:
            raise ValueError("Bad argument: %s\n" % c)

    schools = []
    students = []
    for agent in ans:
        if agent[0:3] == "stu":
            students.append(agent)
        if agent[0:3] == "sch":
            schools.append(agent)
    return schools, students

# load the agent modules in
def load_modules(agent_classes):

    def load(class_name):

        module_name = class_name.lower()  # by convention / fiat
        module = __import__(module_name)
        agent_class = module.__dict__[class_name]
        return (class_name, agent_class)

    return dict(list(map(load, agent_classes)))

# main system
def main(args):

    # define the options parser
    usage_msg = "??"
    parser = OptionParser(usage=usage_msg)

    # error handling for the parser
    def usage(msg):
        print("Error: %s\n" % msg)
        parser.print_help()
        sys.exit()

    # set the parameters for the simulation
    parser.add_option("--stu_con",
                      dest="stu_con", default=10,
                      help="Set the Mean Student Constraint to an Integer")

    parser.add_option("--sch_cap",
                      dest="sch_cap", default=50,
                      help="Set the School Capacity to an Integer")

    # options are the parameters of the simulation
    (options, args) = parser.parse_args()

    # schools, students are the school and student agents respectively
    schools, students = parse_agents(args)

    # load the classes
    student_classes = load_modules(students)
    school_classes = load_modules(schools)

    # initialize each student class
    student_list = []
    for id, student in enumerate(students):

        # set student quality to random uniform [0,1]
        q = random.uniform(0, 1)

        # set student preferences to a list of school ids
        pref = list(range(1, len(schools) + 1))

        # uniform student constraint around mean
        const = math.floor(np.random.normal(int(options.stu_con), 0))
        if const > len(schools) + 1:
            const = len(schools) + 1
        if const < 1:
            const = 1

        # create each student
        s = Student(student, id+1, q, pref, const)

        # add each student to the list
        student_list.append(s)

    # initialize each school class
    school_list = []
    for id, school in enumerate(schools):

        # set school quality to its id
        rank = id + 1

        # set school preferences over students
        pref = list(range(1, len(students) + 1))

        # set school enrollment cap
        cap = int(options.sch_cap)

        # create each school
        s = School(school, id + 1, rank, pref, cap)

        # add each student to the list
        school_list.append(s)

    # run early action round
    early_action_results, proposal_tracker = round_1(student_list, school_list, student_classes, school_classes)

    # run regular decision round
    final_results = round_2(student_list, school_list, student_classes, school_classes,
                            early_action_results, proposal_tracker)

    # run summary stats
    summary_stats(final_results, students, schools, student_list, school_list)

# early action round
def round_1(student_list, school_list, student_classes, school_classes):

    # iterate for each student in the student_list and return early action preferences
    student_ea = {}
    for student in student_list:

        # get early action reports from each student
        s1 = student_classes[student.agent](student.id, student.quality, student.pref, student.const)
        early_action = s1.early_action(school_list, len(student_list))
        student_ea[student.id] = early_action

    # iterate for each school in early action, return accepted students
    proposal_tracker = {}
    school_ea = {}
    for school in school_list:

        # iterate over proposals and filter by proposes to the given school
        early_proposals = []
        for student, proposal in student_ea.items():
            if proposal == school.id:
                early_proposals.append(student)

        # keep track of early_ea proposals for later
        proposal_tracker[school.id] = early_proposals

        # get students accepted in early action
        s1 = school_classes[school.agent](school.id, school.rank, school.pref, school.cap)
        early_action = s1.early_action(early_proposals, len(school_list))
        school_ea[school.id] = early_action

    # append acceptance letters for each student to an overall dictionary
    student_accepts = {}
    for student in student_list:
        # keep a running track of student acceptances
        accepts_list = []
        for school, results in school_ea.items():
            # check if the student was accepted by each school
            if student.id in results:
                accepts_list.append(school)

        student_accepts[student.id] = accepts_list

    return student_accepts, proposal_tracker

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
    main(sys.argv)
