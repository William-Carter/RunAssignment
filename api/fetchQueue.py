import requests
import json
from database.models import Run

def fetchCurrentSrcQueue() -> list[Run.Run]:
    runsInQueue = []
    allRunsCounted = False
    offset = 0
    while not allRunsCounted:
        print(f"Fetching page {int(offset/20) + 1}")
        jsonData = requests.get(f"https://www.speedrun.com/api/v1/runs?status=new&game=4pd0n31e&embed=players&offset={offset}").json()
        with open("api/dl/queue.json", "w") as f:
            json.dump(jsonData, f)
        for index, runData in enumerate(jsonData["data"]):
            run = Run.constructRunFromSrcData(index+offset, runData)
            # Run Assignment system isn't used for ILs or console runs
            if not run.isConsoleRun and not run.isIndividualLevel: 
                runsInQueue.append(run)
        
        if len(jsonData["data"]) < 20:
            allRunsCounted = True

        offset += 20

    return runsInQueue