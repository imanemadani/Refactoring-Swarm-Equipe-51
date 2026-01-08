# Logging Guidelines for Agents

This document explains how to log interactions of agents in the self-healing loop.

## 1. Always use `log_experiment()` or `LoggerAdapter.log()`
- Each agent (Auditor, Fixer, Judge) must call the logger for every action performed.

## 2. Mandatory fields in logs
- `agent_name`: Name of the agent performing the action.
- `model_used`: LLM or model used.
- `action`: Must be a valid `ActionType` or accepted string (`DEBUG` is allowed).
- `details`: Dictionary with:
  - `input_prompt`: The prompt sent to the LLM
  - `output_response`: The response returned by the LLM
- `status`: `"SUCCESS"` or `"FAILURE"`

## 3. ActionType recommendations
Use the `ActionType` enum whenever possible:
- `ActionType.ANALYSIS` → For code analysis
- `ActionType.GENERATION` → For code/test generation
- `ActionType.DEBUG` → For testing/debugging results
- `ActionType.FIX` → For applied fixes

If you want to log something outside these types, `"DEBUG"` string is acceptable.

## 4. Branch workflow
- The logs file `experiment_data.json` is append-only.
- A backup will automatically be created before each run (`experiment_data_backup_YYYYMMDD_HHMMSS.json`).
- This prevents overwriting logs from other team members working on feature branches.
