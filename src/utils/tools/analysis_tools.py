import re

def run_pylint(target_path: str) -> dict:
    result = subprocess.run(
        ["pylint", target_path, "--score=y"],
        capture_output=True,
        text=True
    )
    score_match = re.search(r"Your code has been rated at ([0-9.]+)/10", result.stdout)
    score = float(score_match.group(1)) if score_match else None

    return {
        "stdout": result.stdout.splitlines(),
        "stderr": result.stderr.splitlines(),
        "returncode": result.returncode,
        "score": score
    }
