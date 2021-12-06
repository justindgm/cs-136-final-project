from optparse import OptionParser
import copy
import itertools
import logging
import math
import random
import pprint
import numpy as np
import random
import sys
import scipy.stats as ss
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
    def __init__(self, agent, id, rank, preferences, cap, quality):
        self.agent = agent
        self.id = id
        self.rank = rank
        self.quality = quality
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

# round tracking
def history(h_stu_rank, h_stu_accept, h_stu_early, h_sch_qual, h_sch_enroll, iter, max_iter, student_classes, school_classes, student_agent_rank, student_agent_acceptance, student_early_acceptance, school_agent_quality, school_agent_enroll_avg):

    for student in student_classes.keys():

        if iter == 1:
            h_stu_rank[student] = 0
            h_stu_accept[student] = 0
            h_stu_early[student] = 0

        h_stu_rank[student] += student_agent_rank[student]
        h_stu_accept[student] += student_agent_acceptance[student]
        h_stu_early[student] += student_early_acceptance[student]

    for school in school_classes.keys():

        if iter == 1:
            h_sch_qual[school] = 0
            h_sch_enroll[school] = 0

        h_sch_qual[school] += school_agent_quality[school]
        h_sch_enroll[school] += school_agent_enroll_avg[school]

    if iter == max_iter:
        print("------------------------------------------------------")
        print(f"Final Summary Statistics")
        print("------------------------------------------------------")

        print("")
        print("STUDENT AGENTS:")
        for student in student_classes.keys():
            print("")
            print(f"    Agent: {student}")
            print(f"        Average school rank of {round(h_stu_rank[student]/iter,3)} ")
            print(f"        Average early acceptance rate of {round(h_stu_early[student]/iter*100,3)}%")
            print(f"        Average acceptance rate of {round(h_stu_accept[student]/iter*100,3)}%")

        print("")
        print("SCHOOL AGENTS:")
        for school in school_classes.keys():
            print("")
            print(f"    Agent: {school}")
            print(f"        Average student quality of {round(h_sch_qual[school]/iter, 3)} ")
            print(f"        Average school enrollment of {round(h_sch_enroll[school]/iter*100, 3)}%")

        print("")

    return h_stu_rank, h_stu_accept



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

    parser.add_option("--num_iter",
                      dest="num_iter", default=10,
                      help="Set Number of Iterations of Admissions")

    # options are the parameters of the simulation
    (options, args) = parser.parse_args()

    # schools, students are the school and student agents respectively
    schools, students = parse_agents(args)

    # load the classes
    student_classes = load_modules(students)
    school_classes = load_modules(schools)

    # iterate through rounds
    for iter in range(1,int(options.num_iter)+1):
        print("------------------------------------------------------")
        print(f"ROUND: {iter}")
        print("------------------------------------------------------")

        # initialize each school class
        school_list = []

        school_quals = []
        for i in range(len(schools)):
            quality = np.random.normal(0.5, 0.25)
            # truncate the tails of distribution
            while quality > 1 or quality < 0:
                quality = np.random.normal(0.5, 0.25)
            school_quals.append(quality)

        school_ranks = ss.rankdata([-1 * i for i in school_quals])

        for id, school in enumerate(schools):

            # set school quality to its id
            quality = school_quals[id]

            # set school ranks
            rank = school_ranks[id]

            # set school preferences over students
            pref = list(range(1, len(students) + 1))

            # set school enrollment cap
            cap = int(options.sch_cap)

            # create each school (set id to rank to support easy matching)
            s = School(school, rank, rank, pref, cap, quality)

            # add each student to the list
            school_list.append(s)

        school_list.sort(key=lambda x: x.rank, reverse=False)

        # initialize each student class
        student_list = []
        for id, student in enumerate(students):

            # set student quality to random uniform [0,1]
            q = random.uniform(0, 1)

            # set student preferences to a list of school ids
            ids = [i + 1 for i in range(len(schools))]

            chosen = random.choices(ids, weights = school_quals, k = len(schools))

            def f7(seq):
                seen = set()
                seen_add = seen.add
                return [x for x in seq if not (x in seen or seen_add(x))]

            pref = f7(chosen)
            while len(pref) < len(schools):
                not_chosen = list(set(ids) - set(pref))
                index = [i - 1 for i in not_chosen]
                weight = [school_quals[i] for i in index]
                new_samp = random.choices(not_chosen, weights=weight, k=len(schools))
                chosen = f7(new_samp)
                pref = pref + chosen

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

        # run early action round
        early_action_results, proposal_tracker, early_stats = round_1(student_list, school_list, student_classes, school_classes)

        # run regular decision round
        student_matching, school_matching = round_2(student_list, school_list, student_classes, school_classes,
                                early_action_results, proposal_tracker)

        # run summary stats
        student_agent_rank, student_agent_acceptance, student_early_acceptance, school_agent_quality, school_agent_enroll_avg = summary_stats(student_matching, school_matching, students, schools, student_list, school_list, int(options.sch_cap), early_stats)

        # call history function to record history
        if iter == 1:
            h_stu_rank = {}
            h_stu_accept = {}
            h_stu_early = {}
            h_sch_qual = {}
            h_sch_enroll = {}
        history(h_stu_rank, h_stu_accept, h_stu_early, h_sch_qual, h_sch_enroll, iter, int(options.num_iter), student_classes, school_classes, student_agent_rank, student_agent_acceptance, student_early_acceptance, school_agent_quality, school_agent_enroll_avg)

# early action round
def round_1(student_list, school_list, student_classes, school_classes):

    # iterate for each student in the student_list and return early action preferences
    student_ea = {}
    student_q = {}
    for student in student_list:

        # get early action reports from each student
        s1 = student_classes[student.agent](student.id, student.quality, student.pref, student.const)
        early_action = s1.early_action(school_list, len(student_list))
        student_ea[student.id] = early_action
        student_q[student.id] = student.quality

    # iterate for each school in early action, return accepted students
    proposal_tracker = {}
    school_ea = {}
    for school in school_list:

        # iterate over proposals and filter by proposes to the given school
        early_proposals = {}
        for student, proposal in student_ea.items():
            if proposal == school.id:
                early_proposals[student] = student_q[student]

        # keep track of early_ea proposals for later
        proposal_tracker[school.id] = early_proposals

        # get students accepted in early action
        s1 = school_classes[school.agent](school.id, school.rank, school.pref, school.cap)
        early_action = s1.early_action(early_proposals, len(school_list), len(student_list))
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

    early_stats = {}
    for student in student_list:
        if student.agent not in early_stats:
            early_stats[student.agent] = []
        early_stats[student.agent].append(len(student_accepts[student.id]))

    return student_accepts, proposal_tracker, early_stats

# regular decision round
def round_2(student_list, school_list, student_classes, school_classes, early_action_results, proposal_tracker):

    # iterate for each student in the student list and return rd preferences
    student_rd = {}
    student_q = {}
    for student in student_list:

        # get regular decision reports from each student
        s1 = student_classes[student.agent](student.id, student.quality, student.pref, student.const)
        regular_decision = s1.regular_decision(school_list, len(student_list), early_action_results)
        student_rd[student.id] = regular_decision
        student_q[student.id] = student.quality

    # iterate for each school for regular decision
    school_rd = {}
    for school in school_list:

        # iterate over proposals and filter by proposes to the given school
        proposals = {}
        for student, proposal in student_rd.items():
            if school.id in proposal:
                proposals[student] = student_q[student]

        # pull forward early proposals to adjust cap
        early_proposals = proposal_tracker[school.id]

        # get students accepted in regular decision
        s1 = school_classes[school.agent](school.id, school.rank, school.pref, school.cap)
        regular_decision = s1.regular_decision(proposals, early_proposals, len(school_list), len(student_list))
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

    # select final matchings
    student_matching = {}
    for student, acceptances in student_accepts.items():

        # select first school in the ordered preference, if any
        if len(acceptances) > 0:
            acceptances = sorted(acceptances)
            student_matching[student] = acceptances[0]
        else:
            student_matching[student] = ""

    # select final matching for schools
    school_matching = {}
    for school in school_list:

        accepts_list = []
        for student, accept in student_matching.items():

            if school.id == accept:

                accepts_list.append(student)

        school_matching[school.id] = accepts_list

    return student_matching, school_matching

# summary statistics
def summary_stats(student_matching, school_matching, students, schools, student_list, school_list, cap, early_stats):

    # set up agent type summary stats dictionary
    student_agent_dict = {}
    student_agent_count = {}
    student_accepts_count = {}
    school_agent_dict = {}
    school_agent_count = {}
    school_agent_enroll = {}
    student_agents = list(set(students))
    school_agents = list(set(schools))
    for student in student_agents:
        student_agent_dict[student] = 0
        student_agent_count[student] = 0
        student_accepts_count[student] = 0
    for school in school_agents:
        school_agent_dict[school] = 0
        school_agent_count[school] = 0
        school_agent_enroll[school] = 0

    # iterate through students and calculate mean school rank for each agent type
    unaccepted = []
    student_quality = {}
    for student in student_list:

        # add to student agent count
        student_agent_count[student.agent] += 1

        # get student quality
        student_quality[student.id] = student.quality

        # add mean student quality value
        if student_matching[student.id] == "":
            school_rank = 0
            accept = 0
            unaccepted.append(student.id)
        else:
            school_rank = student_matching[student.id]
            accept = 1
        student_agent_dict[student.agent] += school_rank
        student_accepts_count[student.agent] += accept

    print("")
    print("###### Student Acceptances ######")
    print("")

    # mean the final to get average student agent ranks
    student_agent_rank = {}
    student_agent_acceptance = {}
    student_early_acceptance = {}
    for agent, total_rank in student_agent_dict.items():

        # average school rank
        student_agent_rank[agent] = total_rank / student_accepts_count[agent]
        print(f"{agent} achieves average school rank: {round(student_agent_rank[agent],2)}")

        # early results
        student_early_acceptance[agent] = sum(early_stats[agent])/len(early_stats[agent])
        print(f"{agent} achieves early acceptance rate: {round(sum(early_stats[agent])/len(early_stats[agent])*100,2)}%")

        # average acceptance rate
        student_agent_acceptance[agent] = student_accepts_count[agent] / student_agent_count[agent]
        print(f"{agent} achieves acceptance rate of: {round(student_agent_acceptance[agent]*100,2)}%")

    print("")
    print("###### School Acceptances ######")
    print("")

    # get dict of student ranks and agent type
    school_type = {}
    for school in school_list:
        school_type[school.rank] = school.agent

    # compile basic school summary statistics
    i = 1
    avg_quality = {}
    enroll_count = {}
    for school, students in school_matching.items():

        quality = 0
        j = 1
        for student in students:

            quality += student_quality[student]

            j += 1

        print(f"{school_type[i]} school {i} accepts students {len(students)} with average quality {round(quality/j,3)}")
        i += 1

        avg_quality[school] = quality/j
        enroll_count[school] = len(students)

    print(f"Count unaccepted students: {len(unaccepted)}")

    for school in school_list:
        school_agent_dict[school.agent] += avg_quality[school.id]
        school_agent_count[school.agent] += 1
        school_agent_enroll[school.agent] += enroll_count[school.id]

    print("")
    school_agent_quality = {}
    school_agent_enroll_avg = {}
    for school_agent, total_quality in school_agent_dict.items():
        print(f"School agent {school_agent} has average student quality of {round(school_agent_dict[school_agent] / school_agent_count[school_agent],3)}")
        print(f"School agent {school_agent} has average student enrollment of {round(((school_agent_enroll[school_agent] / school_agent_count[school_agent] / cap)) * 100,3)}%")
        school_agent_quality[school_agent] = school_agent_dict[school_agent] / school_agent_count[school_agent]
        school_agent_enroll_avg[school_agent] = school_agent_enroll[school_agent] / school_agent_count[school_agent] / cap
    print("")

    return student_agent_rank, student_agent_acceptance, student_early_acceptance, school_agent_quality, school_agent_enroll_avg

if __name__ == "__main__":
    main(sys.argv)
