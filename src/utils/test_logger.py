# from logger import log_experiment, ActionType
from src.utils.logger import log_experiment, ActionType

print("=== TEST 1: Normal logging ===")
log_experiment(
    agent_name="Auditor",
    model_used="gpt-4",
    action=ActionType.ANALYSIS,
    details={
        "input_prompt": "Analyze bad_code.py",
        "output_response": "Found unused variables"
    },
    status="SUCCESS"
)

print("=== TEST 2: Append log ===")
log_experiment(
    agent_name="Fixer",
    model_used="gpt-4",
    action=ActionType.FIX,
    details={
        "input_prompt": "Fix indentation",
        "output_response": "Indentation fixed"
    },
    status="SUCCESS"
)

print("=== TEST 3: String action ===")
log_experiment(
    agent_name="Judge",
    model_used="gpt-4",
    action="DEBUG",
    details={
        "input_prompt": "Run tests",
        "output_response": "2 tests failed"
    },
    status="FAILURE"
)

print("Manual tests completed. Check experiment_data.json")
