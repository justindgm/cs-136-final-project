class School:
    def __init__(self, id, rank, preferences, cap):
        self.id = id
        self.rank = rank
        self.pref = preferences
        self.cap = cap


class Naive(School):
    """Naive School Agent"""
    def early_action(self, proposals, schools):
        # loop through all proposals
        accepted = []
        for i, prop in enumerate(proposals):
            # restrict to the agents in the preferences
            if prop in self.preferences:
                # make sure you only accept students up to the cap
                if i < self.cap:
                    accepted.append(prop)
        return accepted

    def regular_decision(self, proposals, early_propsals, schools):
        # pull early action accepts
        early_accepts = len(self.early_action(early_propsals, schools))
        # understand remaining capacity
        regular_cap = self.cap - early_accepts
        # loop through all proposals
        accepted = []
        for i, prop in enumerate(proposals):
            # restrict to the agents in the preferences
            if prop in self.preferences:
                # make sure you only accept students up to the cap
                if i < regular_cap:
                    accepted.append(prop)
        return accepted
