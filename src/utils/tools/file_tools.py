from pathlib import Path
# Define a sandbox directory for file operations
SANDBOX_DIR = Path("sandbox").resolve()

def is_in_sandbox(file_path: Path) -> bool:
    return SANDBOX_DIR in file_path.resolve().parents

def read_file(file_path: str) -> str:
    path = Path(file_path)
    if not is_in_sandbox(path):
        raise PermissionError("Access outside sandbox forbidden")
    if not path.exists():
        raise FileNotFoundError(f"{file_path} does not exist")
    return path.read_text(encoding="utf-8")

def write_file(file_path: str, content: str):
    path = Path(file_path)
    if not is_in_sandbox(path):
        raise PermissionError("Write outside sandbox forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
