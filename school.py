class School:
    def __init__(self, id, quality, preferences, cap):
        self.id = id
        self.quality = quality
        self.pref = {student:rank for rank, student in enumerate(preferences)}
        self.cap = cap
        self.accepted = []
        self.rejected = []
        self.matriculated = []


class Naive(School):
    """Naive School Agent"""
    def early_action(self, proposals):
        proposals.sort(key=lambda x: self.pref[x])
        accepted, rejected = proposals[:self.cap], proposals[self.cap:]
        self.accepted.extend(accepted)
        self.rejected.extend(rejected)
        return accepted, rejected

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
