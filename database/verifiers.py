import database.Interface as dbi
from database.models import Verifier

def getVerifiers(db: dbi.Interface) -> list[Verifier.Verifier]:
    r = db.executeQuery(
        """
        SELECT *
        FROM Verifiers
        """
    )
    verifiers = []
    for row in r:
        verifiers.append(Verifier.Verifier(row["discordId"], row["name"], row["srcId"], row["weeklyMessageId"], row["weeklyMessageReceived"], row["isActive"], row["isAdmin"]))

    return verifiers

def getActiveVerifiers(db: dbi.Interface) -> list[Verifier.Verifier]:
    r = db.executeQuery(
        """
        SELECT *
        FROM Verifiers
        WHERE isActive = 1
        """
    )
    verifiers = []
    for row in r:
        verifiers.append(Verifier.Verifier(row["discordId"], row["name"], row["srcId"], row["weeklyMessageId"], row["weeklyMessageReceived"], row["isActive"], row["isAdmin"]))

    return verifiers

def getAdminVerifiers(db: dbi.Interface) -> list[Verifier.Verifier]:
    r = db.executeQuery(
        """
        SELECT *
        FROM Verifiers
        WHERE isAdmin = 1
        """
    )
    verifiers = []
    for row in r:
        verifiers.append(Verifier.Verifier(row["discordId"], row["name"], row["srcId"], row["weeklyMessageId"], row["weeklyMessageReceived"], row["isActive"], row["isAdmin"]))

    return verifiers
