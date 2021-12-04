import random
class stuPrediction:
    """Safety School student agent"""
    def __init__(self, id, quality, preferences, const):
        self.id = id
        self.quality = quality
        self.preferences = preferences
        self.const = const

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
