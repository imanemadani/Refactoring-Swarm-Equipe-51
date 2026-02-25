import argparse
import os
import shutil
import autopep8
import json

from src.utils.tools.file_tools import read_file, write_file
from src.utils.tools.analysis_tools import run_pylint
from src.utils.llm_client import LlamaClient
from src.Agents.auditor import AuditorAgent
from src.Agents.fixer import FixerAgent
from src.Agents.judge import JudgeAgent

SANDBOX_DIR = "./sandbox/workspace"
os.makedirs(SANDBOX_DIR, exist_ok=True)
MAX_ATTEMPTS = 10


# --- Command-line parser ---
parser = argparse.ArgumentParser()
parser.add_argument("--target_dir", type=str, required=True, help="Directory containing Python files")
args = parser.parse_args()


def get_python_files(target_dir):
    if not os.path.exists(target_dir):
        print(f"The folder {target_dir} doesn't exist")
        return []
    return [
        f for f in os.listdir(target_dir)
        if f.endswith(".py") and f != "test_code.py"
    ]



def clean_fences(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return (
        text.replace("```json", "")
            .replace("```JSON", "")
            .replace("```python", "")
            .replace("```", "")
            .strip()
    )


def safe_compile(code: str) -> bool:
    try:
        compile(code, "<string>", "exec")
        return True
    except Exception as e:
        print(f"⚠️ Syntax error in fixed code: {e}")
        return False


def run_auditor(file_path, llm_client, pylint_report):
    print(f"The auditor is analysing the file: {file_path}")

    try:
        code_content = read_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        raise

    if not isinstance(code_content, str) or len(code_content.strip()) == 0:
        return {"error": "Empty code file", "file": file_path}

    auditor = AuditorAgent(llm_client=llm_client)

    plan = auditor.analyze(code_content, pylint_report)

    # Ensure dict
    if not isinstance(plan, dict):
        plan = {"error": "Auditor returned non-dict plan", "raw_plan": plan}

    return plan


def run_fixer(file_path, plan, llm_client):
    print(f"The fixer is applying the plan to the file: {file_path}")

    try:
        code_content = read_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        raise

    if not isinstance(code_content, str) or len(code_content.strip()) == 0:
        print("⚠️ Empty code content; skipping fixer.")
        return code_content

    if isinstance(plan, dict):
        plan_str = json.dumps(plan, indent=2, ensure_ascii=False)
    else:
        plan_str = str(plan)
    plan_str = clean_fences(plan_str)

    fixer = FixerAgent(llm_client=llm_client)

    fixed_code = fixer.fix(code_content, plan)

    if isinstance(fixed_code, dict):
        fixed_code = fixed_code.get("code", code_content)

    if not isinstance(fixed_code, str) or len(fixed_code.strip()) == 0:
        print("⚠️ Fixer returned empty/invalid code. Using original code.")
        fixed_code = code_content

    fixed_code = clean_fences(fixed_code)

    if not fixed_code.endswith("\n"):
        fixed_code += "\n"

    if not safe_compile(fixed_code):
        print("⚠️ Fixed code failed compile check. Using original code.")
        fixed_code = code_content

    write_file(file_path, fixed_code)
    return fixed_code


def run_judge(file_path, llm_client):
    print(f"The judge is running tests on the file: {file_path}")

    # 1) Delete old generated tests (if exists)
    test_path = os.path.join(SANDBOX_DIR, "test_code.py")
    if os.path.exists(test_path):
        try:
            os.remove(test_path)
        except Exception as e:
            print(f"⚠️ Could not delete old test_code.py: {e}")

    # 2) Read code
    try:
        code_content = read_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        raise

    if not isinstance(code_content, str) or len(code_content.strip()) == 0:
        return {"status": "FAILURE", "all_passed": False, "details": "Invalid or empty code passed to Judge"}

    # 3) Run judge
    judge = JudgeAgent(llm_client=llm_client)
    result = judge.judge(code_content)

    # 4) Normalize output
    if not isinstance(result, dict):
        return {"status": "FAILURE", "all_passed": False, "details": f"Judge returned non-dict: {result}"}

    # 5) Fail fast if judge generated 0 tests
    details = str(result.get("details", ""))
    if "collected 0 items" in details or "no tests ran" in details:
        return {"status": "FAILURE", "all_passed": False, "details": "Judge generated 0 tests"}

    if "status" not in result:
        all_passed = bool(result.get("all_passed", False))
        result["status"] = "SUCCESS" if all_passed else "FAILURE"

    return result


def orchestrate_swarm(target_dir):
    llm_client = LlamaClient()

    python_files = get_python_files(target_dir)
    if not python_files:
        print("No Python files found. Exiting.")
        return

    for file_name in python_files:
        file_path = os.path.join(target_dir, file_name)
        working_file = os.path.join(SANDBOX_DIR, file_name)

        # Copy original to sandbox
        shutil.copy(file_path, working_file)

        print(f"\nProcessing file: {file_path}")
        attempts = 0

        while attempts < MAX_ATTEMPTS:
            print(f"Attempt {attempts + 1}/{MAX_ATTEMPTS} for {file_name}")

            # Run pylint
            pylint_data = run_pylint(working_file)
            initial_report = "\n".join(pylint_data.get("stdout", []))

            # Auditor
            try:
                plan = run_auditor(working_file, llm_client, initial_report)
            except Exception as e:
                print(f"Auditor failed on {file_name}: {e}")
                attempts += 1
                continue

            if isinstance(plan, dict) and plan.get("error"):
                print(f"⚠️ Auditor returned error plan: {plan}")
                attempts += 1
                continue

            # Fixer
            try:
                _ = run_fixer(working_file, plan, llm_client)
            except Exception as e:
                print(f"Fixer failed on {file_name}: {e}")
                attempts += 1
                continue

            # Judge (this is your tests!)
            try:
                test_result = run_judge(working_file, llm_client)
            except Exception as e:
                print(f"Judge failed on {file_name}: {e}")
                attempts += 1
                continue

            print(f"Test result: {test_result}")

            if test_result.get("status") == "SUCCESS":
                # Format ONLY after success
                try:
                    code_content = read_file(working_file)
                    formatted_code = autopep8.fix_code(code_content, options={"aggressive": 2})
                    write_file(working_file, formatted_code)
                    print(f"📈 Applied autopep8 formatting to {file_name}")
                except Exception as e:
                    print(f"⚠️ autopep8 failed on {file_name}: {e}")

                # Copy back only on success
                shutil.copy(working_file, file_path)

                final_score = run_pylint(file_path).get("score", "N/A")
                print(f"✅ {file_name} passed tests. Final Pylint Score: {final_score}/10")
                break
            else:
                print(f"{file_name} failed tests. Retrying...")
                attempts += 1

        if attempts == MAX_ATTEMPTS:
            print(f"{file_name} could not be fixed after {MAX_ATTEMPTS} attempts.")


if __name__ == "__main__":
    orchestrate_swarm(args.target_dir)
