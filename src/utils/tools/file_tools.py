from pathlib import Path

SANDBOX_DIR = Path("sandbox").resolve()  # This points to the folder sandbox in the current working directory.

def is_in_sandbox(file_path: Path) -> bool:
    return SANDBOX_DIR in file_path.resolve().parents

#safe reading/writing of files within a sandboxed directory
def read_file(file_path: str) -> str:
    path = Path(file_path)
    if not is_in_sandbox(path):
        raise PermissionError("Access outside sandbox forbidden")
    with open(path, "r", encoding="utf-8") as f:
        return f.read() # Return the file content as a string.

def write_file(file_path: str, content: str):
    path = Path(file_path)
    if not is_in_sandbox(path):
        raise PermissionError("Write outside sandbox forbidden")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
