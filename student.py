import random


class Student:
    def __init__(self, id, quality, preferences, const):
        self.id = id
        self.quality = quality
        self.pref = preferences
        self.const = const


class Naive(Student):
    """Naive Student Agent"""
    def early_action(self, school_list, students):
        # return the first preference for each student
        return self.preferences[0]

    def regular_decision(self, school_list, students):
        # pull early-action school
        early_school = self.early_action(school_list, students)
        # iterate through preferences in order
        i = 0
        proposals = []
        for pref in self.preferences:
            # if the school is below the admissions cap and not the early school
            if pref != early_school and i < self.const:
                proposals.append(pref)
                i += 1

        return proposals


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
