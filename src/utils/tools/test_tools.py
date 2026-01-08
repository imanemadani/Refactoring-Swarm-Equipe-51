import subprocess
# Utility function to run pytest on a specified directory and return structured results.
def run_pytest(target_dir: str) -> dict:
    result = subprocess.run(
        ["pytest", target_dir, "--tb=short", "--disable-warnings"],
        capture_output=True,
        text=True
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout.splitlines(),
        "stderr": result.stderr.splitlines(),
        "returncode": result.returncode
    }
