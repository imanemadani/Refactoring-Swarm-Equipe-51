import argparse # listen for instructions from the terminal
import os, shutil # allow us to touch files and look into folders on the system (os.path.exists,os.listdir,os.path.join,...)

# Path check: This looks inside the /src folder for the logger and the enum
from src.utils.logger import log_experiment, ActionType
from src.utils.tools.file_tools import read_file  # toolsmith
from src.utils.tools.file_tools import write_file #toolsmith
from src.utils.llm_client import LlamaClient #toolsmith
from src.Agents.auditor import AuditorAgent    # prompt engineer
from src.Agents.fixer import FixerAgent  # prompt engineer
from src.Agents.judge import JudgeAgent  # prompt engineer
from src.utils.tools.analysis_tools import run_pylint
from src.utils.validate_logs import validate_logs

SANDBOX_DIR = "./sandbox/workspace"# To preserve the original code in sandbox until the correct version we copy it to the original file
os.makedirs(SANDBOX_DIR, exist_ok=True)
MAX_ATTEMPTS = 10

#create a parser object to handle command-line arguments
parser = argparse.ArgumentParser() 
# mandatory argument
parser.add_argument("--target_dir",type=str,required=True, help="Directory containing Python files to audit/fix/judge") 
#reads the argument from the command line --> accessed via:args.target_dir
args = parser.parse_args()


def get_python_files(target_dir):
    #check if the folder exists
    if not os.path.exists(target_dir):
        print(f"The folder :{target_dir} doesn't exist")
        return []

    #folder exists : list all the files ending with .py
    files = []

    for f in os.listdir(target_dir):
        if f.endswith('.py'):
            files.append(f)

    #return the list
    return files

def run_auditor(file_path, llm_client, pylint_report):
    print(f"The auditor is analysing the file : {file_path}")

    #read file content
    try:
        code_content = read_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        raise e  # let the outer loop catch it


    input_data = f"CODE:\n{code_content}\n\nPYLINT REPORT:\n{pylint_report}"
    # initialize the Auditor
    auditor = AuditorAgent(llm_client=llm_client)  
    
    return auditor.analyze(code_content, pylint_report)

def run_fixer(file_path, plan, llm_client):    
    print(f"The fixer is applying the plan to the file: {file_path}")
    
    # Read file content
    try:
        code_content = read_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        raise e

    if isinstance(plan, str):
        plan = plan.replace("```json", "").replace("```JSON", "").replace("```", "").strip()

    # Initialize the Fixer agent
    fixer = FixerAgent(llm_client=llm_client)

    # Apply fix only once
    fixed_code = fixer.fix(code_content, plan)

    # 🔒 Ensure fixed_code is always a string
    if isinstance(fixed_code, dict):
        if "code" in fixed_code:
            fixed_code = fixed_code["code"]
        else:
            print("⚠️ Fixer returned dict without 'code'. Using original code")
            fixed_code = code_content

    if not isinstance(fixed_code, str) or len(fixed_code.strip()) == 0:
        print("⚠️ Fixer returned invalid type. Using original code")
        fixed_code = code_content

    # Clean markdown artifacts
    fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

    # Ensure ends with newline
    if not fixed_code.endswith("\n"):
        fixed_code += "\n"

    # 🔒 Minimal syntax check
    try:
        compile(fixed_code, "<string>", "exec")
    except Exception as e:
        print(f"⚠️ Fixed code has syntax errors: {e}. Using original code")
        fixed_code = code_content

    # Write to file
    write_file(file_path, fixed_code)
    return fixed_code

def run_judge(file_path, llm_client):
    print(f"The judge is running tests on the file: {file_path}")

    try:
        code_content = read_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        raise e

    # Defensive check
    if not isinstance(code_content, str) or len(code_content.strip()) == 0:
        return {"status": "FAILURE", "details": "Invalid or empty code passed to Judge"}

    # Initialize Judge
    judge = JudgeAgent(llm_client=llm_client)

    # 🔒 If judge returns a dict, return it directly; else, wrap properly
    result = judge.judge(code_content)
    if isinstance(result, dict):
        return result  # already structured
    else:
        return {"status": "SUCCESS", "details": str(result)}

def orchestrate_swarm(target_dir):
   
    # --- 1. Initialize LLM client ---
    llm_client = LlamaClient()


    # --- 2. Get all Python files in the target directory ---
    python_files = get_python_files(target_dir)
    if not python_files:
        print("No Python files found. Exiting.")
        return

    # --- 3. Loop over each Python file ---
    for file_name in python_files:

        file_path = os.path.join(target_dir, file_name)
        working_file = os.path.join(SANDBOX_DIR, file_name)
        # Copy original to working sandbox
        shutil.copy(file_path, working_file)

        print(f"\nProcessing file: {file_path}")
        attempts = 0

        # --- 4. Retry loop for self-healing ---
        while attempts < MAX_ATTEMPTS:
            print(f"Attempt {attempts + 1}/{MAX_ATTEMPTS} for {file_name}")

            # Run pylint to get the report for the Auditor
            pylint_data = run_pylint(working_file)
            # We convert the list of lines into one big string
            initial_report = "\n".join(pylint_data["stdout"])

            # 4a. Run Auditor to get the plan on the working file
            try:
                plan = run_auditor(working_file, llm_client, initial_report)
            except Exception as e:
                print(f"Auditor failed on {file_name}: {e}")
                attempts += 1
                continue  # Move to next attempt
                        
            # print(f"Audit plan:\n{plan}")  # i think it will be removed , but just as cheking 


            # 4b. Run Fixer to apply the plan
            try:
                fixed_code = run_fixer(working_file, plan, llm_client)
            except Exception as e:
                print(f"Fixer failed on {file_name}: {e}")
                attempts += 1
                continue
            # print(f"Fixed code returned by fixer (first 200 chars):\n{fixed_code[:200]}")

            # 4c. Run Judge to test the fixed code
            try:
                test_result = run_judge(working_file, llm_client)
            except Exception as e:
                print(f"Judge failed on {file_name}: {e}")
                attempts += 1
                continue    
            print(f"Test result: {test_result}")

            # 4d. Check if tests passed
            if  test_result["status"] == "SUCCESS":
                # Only overwrite original if test_result is successful
                shutil.copy(working_file, file_path)
                # Get the score from the pylint_data we ran at the start of this attempt
                score = pylint_data.get("score", "N/A")
                
                print(f"✅ {file_name} passed tests after {attempts + 1} attempt(s).")
                print(f"📈 Final Pylint Score: {score}/10")
                break  # file is fixed, move to next file
            else:
                print(f"{file_name} failed tests. Retrying...")
                attempts += 1

        # If we reach MAX_ATTEMPTS and still fail
        if attempts == MAX_ATTEMPTS:
            print(f"{file_name} could not be fixed after {MAX_ATTEMPTS} attempts.")


if __name__ == "__main__":
    orchestrate_swarm(args.target_dir)
    validate_logs()