import subprocess

def run_pylint(target_path: str) -> dict:
     # Run pylint on the specified target path and return the results as a dictionary instead of printing them on the console.
    result = subprocess.run(
        ["pylint", target_path, "--score=y"],
        capture_output=True,
        text=True
    )
    return {
        "stdout": result.stdout,  # The standard output from pylint
        "stderr": result.stderr, # The standard error from pylint
        "returncode": result.returncode # The return code of the pylint command
    }
