import random
class stuPrediction:
    """Safety School student agent"""
    def __init__(self, id, quality, preferences, const):
        self.id = id
        self.quality = quality
        self.preferences = preferences
        self.const = const

    def early_action(self,school_list, students):
        # given uniform quality distribution each student can determine their expected rank
        expected_rank = round((1 - self.quality)*students)
        # print(self.quality, expected_rank)

        # each student know the ranks of schools and believes that students apply to best schools first
        for pref in self.preferences:
            school = next((school for school in school_list if school.id == pref), None)

            # if there are fewer people expected to be ahead of you than the schools capacity
            if school.cap > (expected_rank - (school.rank - 1)*school.cap):
                return pref

        # if you are not expected to get into any school you apply to the lowest rank school (in theory easiest)
        school = next((school for school in school_list if school.rank == len(school_list)), None)
        return school.id

    def regular_decision(self, school_list, students, early_action_results):

        # pull early-action school
        early_school = self.early_action(school_list, students)
        accepted = len(early_action_results[self.id])
        # print(accepted)
        ea_index = self.preferences.index(early_school)

        proposals = []
        # got into early action should only apply higher
        if accepted == 1:

            # already got into top choice school so no longer applying -- content
            if ea_index == 0:
                return proposals

            # you will apply to less schools than your constraint
            if ea_index < self.const:
                for i,pref in enumerate(self.preferences):

                    # only apply to schools you prefer more
                    if i < ea_index:
                        proposals.append(pref)

            # you will max out your constraint starting from you EA rank
            else:
                proposals = self.preferences[ea_index - self.const : ea_index]

            # print("EA: ", early_school,"Proposals: ", proposals, "Const: ", self.const)

        # got rejected in EA apply to constraint to schools below
        else:
            if len(self.preferences[ea_index:]) > self.const:
                proposals = self.preferences[ea_index + 1 : ea_index + self.const + 1]
            else:
                proposals = self.preferences[ea_index + 1 :]
                extra_cap = self.const - len(proposals)
                above_prop = self.preferences[ea_index - extra_cap : ea_index]
                for prop in above_prop:
                    proposals.append(prop)

            # print("EA Rejection ID: ", early_school,"Proposals: ", proposals, "Const: ", self.const)




        # # iterate through preferences in order
        # i = 0
        # proposals = []
        # for pref in self.preferences:
        #
        #     # if the school is below the admissions cap and not the early school
        #     if pref != early_school and i < self.const:
        #         proposals.append(pref)
        #
        #         i += 1

        return proposals