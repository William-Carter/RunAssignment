import database.Interface as dbi
from database.models import Run
from api.fetchQueue import fetchCurrentSrcQueue

def updateRunsTable(db: dbi.Interface):
    """
    Updates the runs table to exactly match the current queue
    """
    db.insertAndFetchRowID(
        """
        DELETE FROM Runs;
        """
    )

    queue = fetchCurrentSrcQueue()
    for run in queue:
        db.insertAndFetchRowID(
            """
            INSERT OR REPLACE INTO users (srcId, name)
            VALUES (?, ?)
            """,
            (run.user.id, run.user.name)

        )
        db.insertAndFetchRowID(
            """
            INSERT INTO Runs (runId, userId, category, time, description, video, timestamp, isConsoleRun, isIndividualLevel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run.id, run.user.id, run.category, run.time, run.description, run.video, run.timestamp, run.isConsoleRun, run.isIndividualLevel)
        )
    

def cullStaleRecords(db: dbi.Interface):
    """
    Delete Assignments and Users that don't correspond to runs currently in the queue
    """

    db.insertAndFetchRowID(
        """
        DELETE FROM Users
        WHERE srcId NOT IN
        (
            SELECT userId
            FROM Runs
        )
        """
    )

    db.insertAndFetchRowID(
        """
        DELETE FROM Assignments
        WHERE runId NOT IN
        (
            SELECT runId
            FROM Runs
        )
        """
    )


if __name__ == "__main__":
    db = dbi.Interface("veri.db")

    updateRunsTable(db)
    cullStaleRecords(db)