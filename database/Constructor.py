import sqlite3
def construct(dbPath: str) -> None:
    """
    Constructs the database from scratch
    """
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE "Users" (
	"srcId"	TEXT NOT NULL UNIQUE,
    "name" TEXT NOT NULL UNIQUE,
	PRIMARY KEY("srcId")
    )
    """)

    cursor.execute("""
    CREATE TABLE "Verifiers" (
	"discordId"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"srcId"	TEXT NOT NULL UNIQUE,
    "weeklyMessageId" INTEGER,
    "weeklyMessageReceived" INTEGER NOT NULL,
	"isActive"	INTEGER NOT NULL,
	"isAdmin"	INTEGER NOT NULL,
	PRIMARY KEY("discordId")
    )
    """)


    cursor.execute("""
    CREATE TABLE "Assignments" (
    "runId" TEXT NOT NULL UNIQUE,
    "verifierId" INTEGER NOT NULL,
    "dateAssigned" TEXT NOT NULL,
    PRIMARY KEY("runId", "verifierId")
    )
    """)

    cursor.execute("""
    CREATE TABLE "Runs" (
	"runId"	TEXT NOT NULL UNIQUE,
	"userId"	TEXT NOT NULL,
	"category"	TEXT NOT NULL,
	"time"	REAL NOT NULL,
    "description" TEXT,
    "video" TEXT,
	"timestamp"	TEXT NOT NULL,
	"isConsoleRun"	INTEGER NOT NULL,
	"isIndividualLevel"	INTEGER NOT NULL,
	FOREIGN KEY("userId") REFERENCES "Users"("srcId"),
	PRIMARY KEY("runId")
    )
    """)


if __name__ == "__main__":
    construct("fresh.db")
