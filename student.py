import random


class Student:
    def __init__(self, id, quality, preferences, budget):
        self.id = id
        self.quality = quality
        self.pref = preferences
        self.pref2 = {school:rank for rank, school in enumerate(preferences)}
        self.budget = budget
        self.accepted = []
        self.rejected = []


class Naive(Student):
    """Naive Student Agent"""
    def early_action(self):
        # return the first preference for each student
        return self.pref[0]

    def regular_decision(self):
        # fill the remainder of the student budget
        return self.pref[1:self.budget]

    def matriculate(self):
        self.accepted.sort(key=lambda x: self.pref2[x])
        if len(self.accepted) < 1:
            self.matriculated = None
            self.matriculation_rank = len(self.pref) + 1
        else:
            self.matriculated = self.accepted[0]
            self.matriculation_rank = self.pref2[self.matriculated]
        return self.matriculated


class Safety(Student):
    """Safety Student Agent"""
    def early_action(self, school_list, students):
        # Applies to one of the bottom 3 choices for EA as a Safety (TO BE CHANGED AS PREFERENCES DIFFER FROM SCHOOL QUAL)
        safety = random.randint(-3,-1)
        return self.preferences[safety]

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


class Prediction(Student):
    """Prediction Student Agent"""
    def early_action(self,school_list, students):
        # given uniform quality distribution
        expected_rank = (1 - self.quality)*students
        print(self.quality, expected_rank)
        # for school in school_list:
            # print(school.id,school.quality)
        safety = random.randint(-3,-1)
        return self.preferences[safety]

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)
