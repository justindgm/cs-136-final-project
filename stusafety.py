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

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)
