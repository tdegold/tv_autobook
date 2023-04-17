from .Database import *
from .util import ftext, getnums, now_year
from functools import partial

class Predictor:

    def __init__(self, database: Database):
        self.db = database  

        self.exclude_groups = {6, 7, 48, 58}   
        
    def match_id(self, entry):
        txt = " ".join([str(entry.reference), str(entry.text)])
        sender = ftext(entry.sender)

        nums = getnums(txt)
        if nums == set():
            return -1, None
        
        candidates = list(map(self.db.lookup_member, nums))
        ci = list(map(partial(self.check_candidate, sender), candidates))

        if 1 in ci:
            i = ci.index(1)
            return 1, candidates[i]["id"]
        elif 2 in ci:
            i = ci.index(2)
            return 2, candidates[i]["id"]
        else:
            return -1, None

    def check_candidate(self, sender, candidate):
        if candidate == set():
            return -99
        if candidate["surname"] in ftext(sender):
            if set(candidate["groups"]).intersection(self.exclude_groups) == set():
                if (candidate["lby"] is None) or (candidate["lby"] < now_year()):
                    return 1#, "Alle Attribute passen"
                else:
                    return 2#, "Alle Attribute passen, hatte jedoch bereits eine Buchung dieses Jahr"
            else:
                return -2#, "Name passt, jedoch nicht die Gruppenzugehoerigkeit"
        else:
            return -1#, "Name stimmt nicht überein"