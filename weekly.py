import stateUpdate
import assignRuns
import database.verifiers
import requests
import database.Interface as dbi


db = dbi.Interface("veri.db")
assignRuns.assignWeeklyRuns(db)
res = requests.post("http://localhost:6767/weekly")
for verifier in database.verifiers.getActiveVerifiers(db):
    res = requests.post(f"http://localhost:6767/weekly/{verifier.discordId}") # DM each verifier with their shit