import subprocess

def run_pytest(target_dir: str) -> dict:
    # Run pytest on the specified target directory and return the results as a dictionary.
    result = subprocess.run(
        ["pytest", target_dir],
        capture_output=True,
        text=True
    )
    return {
        "stdout": result.stdout, # The standard output from pytest
        "stderr": result.stderr, # The standard error from pytest
        "returncode": result.returncode, # The return code of the pytest command
        "success": result.returncode == 0 # Boolean indicating if tests passed
    }
