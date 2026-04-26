from database import Interface
from database import verifiers
from database.models import Run, RunCollection
from datetime import datetime, timezone, timedelta


def getVerifierAssignments(db: Interface.Interface, verifierId: int):
    assignments = db.executeQuery(
        """
        SELECT runId, dateAssigned
        FROM Assignments
        WHERE verifierId = ?
        """,
        (str(verifierId),)
    )

    if len(assignments) == 0:
        return "All done!", "#45ce23"

    runs = [Run.runFromId(db, x['runId']) for x in assignments]

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

    

    description = ""
    for rc in runCollections:
        rc.runs.sort(key = lambda x: x.time)
        if len(rc.runs) == 1:
            description += generateLine(rc.runs[0])
        else:
            for index, run in enumerate(rc.runs):
                if index == 0:
                    description += generateLine(run)
                else:
                    description += generateSubLine(run)

        description += "\n"


    description += "This message will update hourly."
    

        
    return description, "#e1bd68"


def generateLine(run: Run.Run):
    return f"**[{run.user.name} - {run.category} {run.formattedTime()}](https://speedrun.com/portal/runs/{run.id})**\n"

def generateSubLine(run: Run.Run):
    return f"[+ {run.category} {run.formattedTime()}](https://speedrun.com/portal/runs/{run.id})\n"


def getWeeklyAnnouncement(db: Interface.Interface):
    assignments = db.executeQuery(
        """
        SELECT runId, dateAssigned
        FROM Assignments
        """
    )

    now = datetime.now(timezone.utc)
    weekStart = ((now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    assignments = [a for a in assignments if int(a['dateAssigned']) > weekStart]

    if len(assignments) == 0:
        return "No runs to be assigned this week!"

    runs = [Run.runFromId(db, x['runId']) for x in assignments]

    runCollections = []

    for run in runs:
        collected = False
        for rc in runCollections:
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

            if collected:
                break

        if not collected:
            rc = RunCollection.RunCollection(-1, run.user, run.category)
            rc.verifier = run.assignedTo
            rc.addRun(run)
            runCollections.append(rc)


    activeVerifiers = verifiers.getActiveVerifiers(db)
    activeVerifiers.sort(key= lambda x: x.name)

    verifierTotals = {v: {"pooled": 0, "runs": 0, "time": 0, "runList": []} for v in activeVerifiers}
    for rc in runCollections:
        verifierTotals[rc.verifier]["pooled"] += 1
        verifierTotals[rc.verifier]["runs"] += len(rc.runs)
        verifierTotals[rc.verifier]["time"] += rc.duration()
        verifierTotals[rc.verifier]["runList"].append(rc)
        
    finalOutput = []
    workingOutput = ""
    for verifier in activeVerifiers:
        if verifierTotals[verifier]['runs'] == 0:
            output = f"<@{verifier.discordId}> hasn't been assigned any runs\n"
        else:
            output = f"<@{verifier.discordId}> has been assigned {verifierTotals[verifier]['pooled']} ({verifierTotals[verifier]['runs']}) runs totaling {formattedTime(verifierTotals[verifier]['time'])}\n"
            for rc in verifierTotals[verifier]["runList"]:
                subtext = ""
                for index, run in enumerate(sorted(rc.runs, key = lambda x: x.time)):
                    if index == 0:
                        subtext += " "*5+generateLine(run)
                    else:
                        subtext += " "*5+generateSubLine(run)
                output += subtext
        
        if len(workingOutput) + len(output) > 1900:
            finalOutput.append(workingOutput)
            workingOutput = ""

        workingOutput += output

    finalOutput.append(workingOutput)

    return finalOutput


def formattedTime( time) -> str:
    hours = int(time // 3600)
    minutes = int((time % 3600) // 60)
    sms = round(time % 60, 3)
    result = str(sms)
    if minutes or hours:
        if sms < 10:
            result = f"{minutes}:0{result}"
        else:
            result = f"{minutes}:{result}"
    if hours:
        if minutes < 10:
            result = f"{hours}:0{result}"
        else:
            result = f"{hours}:{result}"
    result = result + ('0' * (3 - len(result.split(".")[-1])))
    return result