from database.models import User
from database.models import Verifier
from database.Interface import Interface
from datetime import datetime, timezone
import SRCValues as src

class Run:
    def __init__(self, id: str, user: User.User, category: str, time: float, timestamp: str, 
                 description: str, video: str, queuePosition: int, isConsoleRun: bool, isIndividualLevel: bool, 
                 assignedTo: Verifier.Verifier = None):
        self.id = id
        self.user = user
        self.category = category
        self.time = time
        self.timestamp = timestamp
        self.description = description
        self.video = video
        self.queuePosition = queuePosition
        self.isConsoleRun = isConsoleRun
        self.isIndividualLevel = isIndividualLevel
        self.assignedTo = assignedTo


    def assign(self, db: Interface, verifier: Verifier):
        now = str(int(datetime.now(timezone.utc).timestamp()))
        #print(self.id)
        db.insertAndFetchRowID(
            """
            INSERT INTO Assignments (runId, verifierId, dateAssigned)
            VALUES (?, ?, ?)
            """,
            (self.id, verifier.discordId, now)
        )
        self.assignedTo = verifier

    def formattedTime(self) -> str:
        minutes = int(self.time // 60)
        sms = round(self.time % 60, 3)
        result = str(sms)
        if minutes:
            
            if sms < 10: 
                result = str(minutes)+":0"+result # Get 5:04.5 instead of 5:4.5

            else:
                result = str(minutes)+":"+result

        result = result+('0'*(3-len(result.split(".")[-1]))) # Add trailing zeroes
        return result


def constructRunFromSrcData(queuePosition: int, data: dict) -> Run:
    id = data["id"]
    category = src.getCategory(data["category"])

    isConsoleRun = False
    if src.values.VARIABLE_PC_CONSOLE in data["values"]:
        isConsoleRun = (data["values"][src.values.VARIABLE_PC_CONSOLE] == src.values.VALUE_PC_CONSOLE_CONSOLE)


    if data["level"]:
        isIndividualLevel = True
    else:
        isIndividualLevel = False

    time = data["times"]["primary_t"]

    timestamp = int(datetime.strptime(data["submitted"], "%Y-%m-%dT%H:%M:%SZ").timestamp())
    runnerName = data["players"]["data"][0]["names"]["international"]
    runnerId = data["players"]["data"][0]["id"]
    description = data["comment"]

    if data["videos"]:
        video = data["videos"]["links"][0]["uri"]
    else:
        video = None

    runner = User.User(runnerId, runnerName)
    return Run(id, runner, category, time, timestamp, description, video, queuePosition, isConsoleRun, isIndividualLevel)

def constructRunFromDbRow(db, row) -> Run:
    return Run(row['runId'], User.userFromId(db, row['userId']), row['category'], row['time'], row['timestamp'], row['description'], row['video'], -1, row['isConsoleRun'], row['isIndividualLevel'])



def runFromId(db, id):
    r = db.executeQuery("SELECT Runs.runId, userId, category, time, description, video, timestamp, isConsoleRun, isIndividualLevel, verifierId FROM Runs LEFT JOIN Assignments ON Runs.runId = Assignments.runId WHERE Runs.runId = ?", (id,))
    if len(r) == 0:
        return None
    
    v = r[0]
    
    return Run(v['runId'], User.userFromId(db, v['userId']), v['category'], v['time'], v['timestamp'], v['description'], v['video'], -1, v['isConsoleRun'], v['isIndividualLevel'], Verifier.verifierFromId(db, v['verifierId']))