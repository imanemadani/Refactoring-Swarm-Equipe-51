# src/run_mini_loop.py

import os
from glob import glob
from datetime import datetime
from src.utils.logger import LOG_FILE
from src.utils.validate_logs import validate_logs
from src.utils.fake_llm import FakeLLM
from src.Agents.auditor import AuditorAgent
from src.Agents.fixer import FixerAgent
from src.Agents.judge import JudgeAgent
from src.utils.logger_adapter import LoggerAdapter

# --- 0️⃣ Automatic Timestamped Backup ---
if os.path.exists(LOG_FILE):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = LOG_FILE.replace(".json", f"_backup_{timestamp}.json")
    os.rename(LOG_FILE, backup_file)
    print(f"🔹 Backup created: {backup_file}")

# Start fresh logs
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

# --- 1️⃣ Initialize Agents & Logger ---
llm = FakeLLM()

auditor_logger = LoggerAdapter(agent_name="Auditor")
fixer_logger = LoggerAdapter(agent_name="Fixer")
judge_logger = LoggerAdapter(agent_name="Judge")

auditor = AuditorAgent(llm_client=llm, logger=auditor_logger)
fixer = FixerAgent(llm_client=llm, logger=fixer_logger)
judge = JudgeAgent(llm_client=llm, logger=judge_logger)

# --- 2️⃣ Gather Python files to process ---
sandbox_path = "sandbox"
files_to_process = glob(os.path.join(sandbox_path, "*.py"))

if not files_to_process:
    print(f"❌ No Python files found in {sandbox_path}")
    exit(0)

# --- 3️⃣ Self-Healing Loop ---
MAX_ITER = 3
summary = {}

for file_path in files_to_process:
    print(f"\nProcessing file: {file_path}\n")
    with open(file_path, "r") as f:
        code = f.read()
    
    file_passed = False
    for iteration in range(1, MAX_ITER + 1):
        print(f"--- Iteration {iteration} ---")
        
        # Auditor
        plan = auditor.analyze(code)
        print("Auditor done.")
        
        # Fixer
        code = fixer.fix(code, plan)
        print("Fixer done.")
        
        # Judge
        result = judge.judge(code)
        print(f"Judge done: {result}")
        
        if result.strip().upper() == "SUCCESS":
            file_passed = True
            print(f"✅ File {file_path} passed after {iteration} iteration(s).")
            break
    
    if not file_passed:
        print(f"❌ File {file_path} failed after {MAX_ITER} attempts.")
    
    summary[file_path] = "PASSED" if file_passed else "FAILED"

# --- 4️⃣ Validate Logs ---
print("\n--- Log Validation ---")
validate_logs()

# --- 5️⃣ Summary ---
print("\n--- Summary ---")
for f, status in summary.items():
    print(f"{f}: {status}")

print("\n👑 Self-healing loop completed.")
