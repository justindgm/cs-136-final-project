import random
class stuSafety:
    """Safety School student agent"""
    def __init__(self, id, quality, preferences, const):
        self.id = id
        self.quality = quality
        self.preferences = preferences
        self.const = const

    def early_action(self, school_list, students):
        # Applies to one of the bottom 3 choices for EA as a Safety (TO BE CHANGED AS PREFERENCES DIFFER FROM SCHOOL QUAL)
        safety = random.randint(-3,-1)
        return self.preferences[safety]

    def regular_decision(self, school_list, students, early_action_results):

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
