import database.Interface as dbi

db = dbi.Interface("veri.db")

db.insertAndFetchRowID(
    "ALTER TABLE Assignments ADD COLUMN assignedOnSRC INTEGER NOT NULL DEFAULT 0"
)