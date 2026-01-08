# src/utils/log_backup.py
import os
from datetime import datetime
from src.utils.logger import LOG_FILE

def backup_logs():
    """Create a timestamped backup of the current experiment_data.json file."""
    if os.path.exists(LOG_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = LOG_FILE.replace(".json", f"_backup_{timestamp}.json")
        os.rename(LOG_FILE, backup_file)
        print(f"🔹 Backup created: {backup_file}")
