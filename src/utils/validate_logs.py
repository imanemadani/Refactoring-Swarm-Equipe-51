import json
from .logger import LOG_FILE
# validates all logs in the file

# Required top-level fields in each log
REQUIRED_FIELDS = ["id", "timestamp", "agent", "model", "action", "details", "status"]

# Required fields inside "details" dictionary
DETAILS_REQUIRED_FIELDS = ["input_prompt", "output_response"]

def validate_logs(file_path=LOG_FILE):
    """
    Validates that every log entry in experiment_data.json has all required fields.
    Prints any missing fields and returns True if all entries are valid, False otherwise.
    """
    # Read the JSON file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        print(f"❌ Log file not found: {file_path}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Log file is not valid JSON: {file_path}")
        return False

    all_valid = True

    # Loop through logs
    for i, log in enumerate(logs):
        # Check top-level fields
        for field in REQUIRED_FIELDS:
            if field not in log:
                print(f"❌ Log #{i} missing field: {field}")
                all_valid = False

        # Check details fields
        if "details" in log:
            for key in DETAILS_REQUIRED_FIELDS:
                if key not in log["details"]:
                    print(f"❌ Log #{i} details missing: {key}")
                    all_valid = False
        else:
            print(f"❌ Log #{i} missing 'details'")
            all_valid = False

    if all_valid:
        print("✅ All logs are valid")
    else:
        print("⚠️ Some log entries are missing required fields")

    return all_valid
