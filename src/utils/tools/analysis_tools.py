import re
import subprocess
def run_pylint(target_path: str) -> dict:
    # Run pylint on the specified target path and return the results.
    result = subprocess.run(
        ["pylint", target_path, "--score=y"],
        capture_output=True,
        text=True
    )

    score_match = re.search(r"Your code has been rated at ([0-9.]+)/10", result.stdout)
    score = float(score_match.group(1)) if score_match else None

    return {
        "stdout": result.stdout.splitlines(),
        #standard output from pylint containing the line-by-line report for the code
        #Each line tells: File name and line number, Message code (like C0114 = convention, W0612 = warning,....) and Description
        #splitlines() just converts this into a Python list of strings, one per line.

        "stderr": result.stderr.splitlines(),
        #standard error from pylint, usually empty [] unless there are serious issues running pylint itself

        "returncode": result.returncode,
        #the exit code from pylint, 0 means no issues, higher values indicate problems

        "score": score
        #the overall pylint score as a float, or None if it couldn't be determined
    }

