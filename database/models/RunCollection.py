from database.models.User import User
from database.models.Run import Run
class RunCollection:
    def __init__(self, queuePosition: int, user: User, category: str):
        self.queuePosition = queuePosition
        self.user = user
        self.category = category
        self.runs = []
        self.verifier = None

    def addRun(self, run: Run):
        self.runs.append(run)


    def duration(self):
        # Assume that verifying an obsolete run will take about 2 additional minutes
        obsoleteRunEffortValue = 120
        fastestRun = min(self.runs, key = lambda x: x.time)
        return fastestRun.time + obsoleteRunEffortValue * (len(self.runs) - 1)
    

    def getMainRun(self):
        return min(self.runs, key = lambda r: r.time)