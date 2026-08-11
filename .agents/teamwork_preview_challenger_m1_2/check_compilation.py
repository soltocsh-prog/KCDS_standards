import py_compile
from pathlib import Path

target_dir = Path(r"c:\Users\solto\OneDrive\문서\KCS_Automation")

py_files = list(target_dir.rglob("*.py"))
print(f"Compiling {len(py_files)} Python files...")

errors = []
for py_file in py_files:
    rel_path = py_file.relative_to(target_dir)
    try:
        py_compile.compile(str(py_file), doraise=True)
        print(f"[OK] {rel_path}")
    except Exception as e:
        print(f"[FAIL] {rel_path}: {e}")
        errors.append((rel_path, str(e)))

print(f"\nTotal files: {len(py_files)}, Successes: {len(py_files) - len(errors)}, Errors: {len(errors)}")
