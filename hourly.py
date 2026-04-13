import stateUpdate
import assignRuns
import database.verifiers
import requests
import database.Interface as dbi


db = dbi.Interface("veri.db")
stateUpdate.updateRunsTable(db) # Sync queue with SRC
stateUpdate.cullStaleRecords(db) # Get rid of any assignments/users corresponding to runs that aren't in queue anymore
assignRuns.updateAssignments(db) # Assign any straggler runs (runs that obsolete a run already assigned)
for verifier in database.verifiers.getActiveVerifiers(db): 
    res = requests.post(f"http://localhost:6767/hourly/{verifier.discordId}") # Update verifiers' personal queues