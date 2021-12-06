import numpy as np

class schBase:

    """Base school agent"""

    def __init__(self, id, rank, preferences, cap):

        self.id = id
        self.rank = rank
        self.preferences = preferences
        self.cap = cap


    def early_action(self, proposals, schools, students):

        proposals = self.noise(proposals)

        # sort proposals by quality
        keys = sorted(proposals, key=proposals.get, reverse=True)

        # predict range of students we are looking for
        school_quality = self.cap * self.rank
        target_quality = 1 - school_quality/students
        factor = self.cap / students

        # loop through all proposals
        accepted = []
        i = 0
        for prop in keys:

            # restrict to the agents in the preferences
            if prop in self.preferences:

                # target specific types of students
                if proposals[prop] < target_quality + factor and proposals[prop] > target_quality - factor:

                    i += 1

                    # make sure you only accept students up to the cap
                    if i < self.cap + 1:

                        accepted.append(prop)

        return accepted


    def regular_decision(self, proposals, early_propsals, schools, students):

        proposals = self.noise(proposals)

        # sort proposals by quality
        keys = sorted(proposals, key=proposals.get, reverse=True)

        # predict range of students we are looking for
        school_quality = self.cap * self.rank
        target_quality = 1 - school_quality / students
        factor = self.cap / students

        # pull early action accepts
        early_accepts = len(self.early_action(early_propsals, schools, students))

        # understand remaining capacity
        regular_cap = self.cap - early_accepts

        # loop through all proposals
        accepted = []
        i = 0
        for prop in keys:

            # restrict to the agents in the preferences
            if prop in self.preferences:

                # target specific types of students
                if proposals[prop] < target_quality + factor and proposals[prop] > target_quality - factor:

                    i += 1

                    # make sure you only accept students up to the cap
                    if i < regular_cap + 1:

                        accepted.append(prop)

        return accepted


    def noise(self, proposals):

        # add school noise
        for student, quality in proposals.items():
            noise = np.random.normal(0, 0.05)
            proposals[student] += noise

        return proposals