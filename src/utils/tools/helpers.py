import json

def list_python_files(target_dir: str) -> list[Path]:
    dir_path = Path(target_dir)
    if not is_in_sandbox(dir_path):
        raise PermissionError("Access outside sandbox forbidden")
    return [f for f in dir_path.rglob("*.py") if f.is_file()]

def save_log(data: dict, log_file: str):
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
