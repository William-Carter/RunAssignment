from database.Interface import Interface
from database.models import Run, RunCollection, Verifier
from database import verifiers
from datetime import datetime, timezone, timedelta

def assignWeeklyRuns(db: Interface):
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    timeStamp = int(cutoff.timestamp())
    
    runs = db.executeQuery(
        """
        SELECT Runs.runId as runId, userId, category, time, description, video, timestamp, isConsoleRun, isIndividualLevel
        FROM Runs
        LEFT JOIN Assignments ON Runs.runId = Assignments.runId
        WHERE Runs.timestamp < ?
        AND Assignments.runId IS NULL
        """,
        (timeStamp,)
    )
    runs = [Run.constructRunFromDbRow(db, x) for x in runs]

    runCollections = []

    for run in runs:
        collected = False
        for rc in runCollections:
            #print(run.user, run.category, rc.user, rc.category)
            # Pool runs that are in the same category - only the fastest one needs full verification
            if run.user == rc.user and run.category == rc.category:
                rc.addRun(run)
                collected = True
                break
            for rcr in rc.runs:
                # Pool runs of different categories that have the exact same time
                # They're probably just the same run submitted twice
                if run.user == rcr.user and run.time == rcr.time:
                    rc.addRun(run)
                    collected = True
                    break

        if not collected:
            rc = RunCollection.RunCollection(-1, run.user, run.category)
            rc.addRun(run)
            runCollections.append(rc)

    runCollections.sort(key= lambda x: x.duration(), reverse=True)
    
    activeVerifiers = verifiers.getActiveVerifiers(db)
    assignments = {v: 0 for v in activeVerifiers}
    for rc in runCollections:
        verifier = min(assignments.keys(), key = lambda x: assignments[x])
        assignments[verifier] += rc.duration()
        for run in rc.runs:
            run.assign(db, verifier)
            #print(f"assigned {run.user.name} {run.category} {run.time} to {verifier.name}")
        

def updateAssignments(db: Interface):
    runsAndAssignments = db.executeQuery(
        """
        SELECT Runs.runId, Runs.userId, Runs.category, Runs.time, Runs.timestamp, Runs.description, Runs.video, Runs.isConsoleRun, Runs.isIndividualLevel, Assignments.verifierId
        FROM Runs
        LEFT JOIN Assignments ON Runs.runId = Assignments.runId
        """
    )
    runs = []
    for run in runsAndAssignments:
        runObj = Run.constructRunFromDbRow(db, run)
        runObj.assignedTo = Verifier.verifierFromId(db, run['verifierId'])
        runs.append(runObj)

    for thisRun in runs:
        if thisRun.assignedTo == None:
            for otherRun in runs:
                if otherRun.assignedTo != None and thisRun.user == otherRun.user and thisRun.category == otherRun.category and thisRun.id != otherRun.id:
                    thisRun.assign(db, otherRun.assignedTo)
                    print(f"Assigned additional run {thisRun.category} {thisRun.time} by {thisRun.user.name} to {thisRun.assignedTo.name}")
                    break
                    



if __name__ == "__main__":
    db = Interface("veri.db")
    assignWeeklyRuns(db)