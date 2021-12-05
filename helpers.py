import school
import student
import random
import math
import numpy as np


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

