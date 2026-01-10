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
        # Indicates whether the tests passed (0) or failed (non-zero)
        "stdout": result.stdout.splitlines(),
        # Splits the standard output into a list of lines (Human-readable)
        "stderr": result.stderr.splitlines(),
        # Errors from pytest itself as a list of lines
        "returncode": result.returncode
        # 0 means success, non-zero means failure from pytest
    }
