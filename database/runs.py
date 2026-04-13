import database.Interface as dbi
from database.models import Run

def getRuns(db: dbi.Interface) -> list[Run.Run]:
    r = db.executeQuery(
        """
        SELECT *
        FROM Runs
        """
    )
    runs = []
    for row in r:
        runs.append(Run.constructRunFromDbRow(db, row))

    return runs

