import argparse # listen for instructions from the terminal
import os # allow us to touch files and look into folders on the system (os.path.exists,os.listdir,os.path.join,...)
import sys #allow us to access to system-specific parameters (standard)


# Path check: This looks inside the /src folder for the logger and the enum
from src.utils.logger import log_experiment, ActionType
from src.utils.tools.file_tools import read_file  # toolsmith
from src.utils.tools.file_tools import write_file #toolsmith
from src.Agents.auditor import AuditorAgent    # AI engineer
from src.Agents.fixer import FixerAgent  # AI engineer
from src.Agents.judge import JudgeAgent  # AI engineer
from src.utils.logger import Logger


SANDBOX_DIR = "./sandbox" # hardcoded , like a default one --> can be overriden by --target_dir
MAX_ATTEMPTS = 10


class MockLLMClient:
    def send(self, prompt, code):
        return "Mock audit report: no real AI was used."




parser = argparse.ArgumentParser() #create a parser object to handle command-line arguments
parser.add_argument("--target_dir",type=str,required=True)  # mandatory argument
args = parser.parse_args() #reads the argument from the command line --> accessed via:args.target_dir


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


def run_auditor(file_path, llm_client, logger):
    print(f"The auditor is analysing the file : {file_path}")
    #read file content
    code_content = read_file(file_path)
    # initialize the Auditor
    auditor = AuditorAgent(llm_client=llm_client, logger=logger)
    # sent content to Auditor
    audit_report = auditor.analyze(code_content)
    # return the plan
    return audit_report


def run_fixer(file_path, plan, llm_client, logger):    
    print(f"The fixer is applying the plan to the file: {file_path}")
   
    # Read file content
    code_content = read_file(file_path)
    # Initialize the Fixer agent
    fixer = FixerAgent(llm_client=llm_client, logger=logger)    
    # Send code + plan to the fixer
    fixed_code = fixer.fix(code_content, plan)
    # Write the fixed code back so Judge tests the new version
    write_file(file_path, fixed_code)
    # Return the fixed code
    return fixed_code


def run_judge(file_path, llm_client, logger):
    print(f"The judge is running tests on the file: {file_path}")
    # Read file content
    code_content = read_file(file_path)
    # Initialize the Judge agent
    judge = JudgeAgent(llm_client=llm_client, logger=logger)
    # Send code to the judge
    test_result = judge.judge(code_content)
    # Return the test result
    return test_result


def orchestrate_swarm(target_dir):
   
    # --- 1. Initialize logger and LLM client ---
    # Logger is responsible for logging all actions
    logger = Logger()
    # LLM client is a placeholder for now (Ilham will replace it later)
    llm_client = MockLLMClient()


    # --- 2. Get all Python files in the target directory ---
    python_files = get_python_files(target_dir)
    if not python_files:
        print("No Python files found. Exiting.")
        return


    # --- 3. Loop over each Python file ---
    for file_name in python_files:
        file_path = os.path.join(target_dir, file_name)
        print(f"\nProcessing file: {file_path}")
        attempts = 0


        # --- 4. Retry loop for self-healing ---
        while attempts < MAX_ATTEMPTS:
            print(f"Attempt {attempts + 1} of {MAX_ATTEMPTS} for {file_name}")


            # 4a. Run Auditor to get the plan
            plan = run_auditor(file_path, llm_client, logger)
            print(f"Audit plan:\n{plan}")


            # 4b. Run Fixer to apply the plan
            fixed_code = run_fixer(file_path, plan, llm_client, logger)
            print(f"Fixed code returned by fixer (first 200 chars):\n{fixed_code[:200]}")


            # 4c. Run Judge to test the fixed code
            test_result = run_judge(file_path, llm_client, logger)
            print(f"Test result: {test_result}")


            # 4d. Check if tests passed
            if "SUCCESS" in test_result:
                print(f"{file_name} passed tests after {attempts + 1} attempt(s).")
                break  # file is fixed, move to next file
            else:
                print(f"{file_name} failed tests. Retrying...")
                attempts += 1


        # If we reach MAX_ATTEMPTS and still fail
        if attempts == MAX_ATTEMPTS:
            print(f"{file_name} could not be fixed after {MAX_ATTEMPTS} attempts.")



if __name__ == "__main__":
    orchestrate_swarm(args.target_dir)