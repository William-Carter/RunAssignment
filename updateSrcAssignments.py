import requests
import dotenv
import os

from database.Interface import Interface
from database.models import Verifier

dotenv.load_dotenv()

SESSION_COOKIE = f"PHPSESSID={os.getenv('PHP_SESSION_ID')}"

API_URL = "https://www.speedrun.com/api/v2/PutRunAssignee"

HEADERS = {
    "cookie": SESSION_COOKIE,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36..."
}


def update_assignment_on_src(run_id: str, assignee_src_id: str) -> bool:
    """
    Update a run assignment on speedrun.com.
    
    Returns:
        True if successful, False otherwise
    """
    payload = {
        "runId": run_id,
        "assigneeId": assignee_src_id
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"✓ Updated run {run_id} to assignee {assignee_src_id}")
            return True
        else:
            print(f"✗ Failed to update run {run_id}: {response.status_code}")
            print(f"  Response: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ Error updating run {run_id}: {str(e)}")
        return False


def main():
    db = Interface("veri.db")
    
    # Get all assignments from the database
    assignments = db.executeQuery(
        """
        SELECT Assignments.runId, Assignments.verifierId
        FROM Assignments
        """
    )
    
    if not assignments:
        print("No assignments found in the database.")
        return
    
    print(f"Found {len(assignments)} assignments to update on speedrun.com\n")
    
    success_count = 0
    failed_count = 0
    
    for assignment in assignments:
        run_id = assignment["runId"]
        verifier_id = assignment["verifierId"]
        
        # Get verifier's speedrun.com ID
        verifier = Verifier.verifierFromId(db, verifier_id)
        if not verifier:
            print(f"✗ Verifier {verifier_id} not found for run {run_id}")
            failed_count += 1
            continue
        
        srcId = verifier.srcId
        
        # Update on speedrun.com
        if update_assignment_on_src(run_id, srcId):
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\nResults: {success_count} succeeded, {failed_count} failed")


if __name__ == "__main__":
    main()



