from database.Interface import Interface
from database.models import Run
from database import runs
import re

linkpattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', re.MULTILINE)

def checkRun(run: Run.Run):
    notes = []
    # 1. No video/demos
    demoLink = None
    if run.description:
        demoLink = linkpattern.search(run.description)

    if not run.video and not demoLink:
        notes.append("Run likely has no proof")

    # 2. Incorrect decimals
    if round(run.time / 0.015, 3) != round(run.time / 0.015, 0):
        notes.append("Run has invalid decimal places")

    return notes


if __name__ == "__main__":
    db = Interface("veri.db")
    toMod = runs.getRuns(db)
    for run in toMod:
        notes = checkRun(run)
        print(f"{run.user.name} {run.category} {run.time} - {notes}")
        