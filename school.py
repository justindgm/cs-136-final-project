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

    def regular_decision(self, proposals):
        proposals.sort(key=lambda x: self.pref[x])
        remaining_cap = self.cap - len(self.accepted)
        accepted, rejected = proposals[:remaining_cap], proposals[remaining_cap:]
        self.accepted.extend(accepted)
        self.rejected.extend(rejected)
        return accepted, rejected
