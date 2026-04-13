from database import Interface
class Verifier:
    def __init__(self, discordId: int, name: str, srcId: str, weeklyMessageId: int, weeklyMessageReceived: bool, isActive: bool, isAdmin: bool):
        self.name = name
        self.discordId = discordId
        self.srcId = srcId
        self.weeklyMessageId = weeklyMessageId
        self.weeklyMessageReceived = weeklyMessageReceived
        self.isActive = isActive
        self.isAdmin = isAdmin


    def updateWeeklyMessage(self, db: Interface.Interface, messageId: int):
        db.insertAndFetchRowID("UPDATE Verifiers SET weeklyMessageId = ? WHERE discordId = ?", (messageId, self.discordId))
        self.weeklyMessageId = messageId
        

    def updateMessageStatus(self, db: Interface.Interface, status: bool):
        db.insertAndFetchRowID("UPDATE Verifiers SET weeklyMessageReceived = ? WHERE discordId = ?", (int(status), self.discordId))

    def __eq__(self, other):
        if not isinstance(other, Verifier):
            return False

        return self.discordId == other.discordId

    def __hash__(self):
        return hash(self.discordId)


def verifierFromId(db: Interface.Interface, id):
    r = db.executeQuery("SELECT discordId, name, srcId, weeklyMessageId, weeklyMessageReceived, isActive, isAdmin FROM Verifiers WHERE discordId = ?", (id,))
    if len(r) == 0:
        return None
    
    v = r[0]
    
    return Verifier(v['discordId'], v['name'], v['srcId'], v['weeklyMessageId'], v['weeklyMessageReceived'], v['isActive'], v['isAdmin'])
