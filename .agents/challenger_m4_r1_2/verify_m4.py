import os
import sys
import re
import subprocess

kcs_dir = r"c:\Users\solto\OneDrive\문서\KCS_Automation"
log_path = os.path.join(kcs_dir, "migration_log.txt")

print("=== Starting Milestone 4 Empirical Verification ===")

# 1. Read migration_log.txt and parse file inventory
print("\n--- Step 1: Validating migration_log.txt accuracy ---")

with open(log_path, "r", encoding="utf-8") as f:
    log_content = f.read()

# Line pattern: "  - path/to/file                                            1,234 bytes"
pattern = re.compile(r"^\s+-\s+([^\s].*?)\s+([0-9,]+)\s+bytes$", re.MULTILINE)
matches = pattern.findall(log_content)

print(f"Parsed {len(matches)} files from migration_log.txt")

log_file_dict = {}
for file_path, size_str in matches:
    clean_path = file_path.replace("/", os.sep).replace("\\", os.sep)
    byte_size = int(size_str.replace(",", ""))
    log_file_dict[clean_path] = byte_size

# Check files on disk
disk_files = {}
for root, dirs, files in os.walk(kcs_dir):
    if ".git" in root.split(os.sep):
        continue
    for file in files:
        full_p = os.path.join(root, file)
        rel_p = os.path.relpath(full_p, kcs_dir).replace("/", os.sep)
        disk_files[rel_p] = os.path.getsize(full_p)

print(f"Total files found on disk (excluding .git): {len(disk_files)}")

mismatches = []
missing_on_disk = []
for rel_p, log_size in log_file_dict.items():
    if rel_p not in disk_files:
        missing_on_disk.append(rel_p)
    else:
        actual_size = disk_files[rel_p]
        if rel_p == "migration_log.txt":
            print(f"Note: migration_log.txt logged size={log_size}, actual size={actual_size} (self-referential logging difference)")
        elif actual_size != log_size:
            mismatches.append((rel_p, log_size, actual_size))

unlogged_files = []
for rel_p in disk_files:
    if rel_p not in log_file_dict:
        unlogged_files.append(rel_p)

print(f"Missing on disk: {missing_on_disk}")
print(f"Size mismatches (excluding migration_log.txt self-ref): {mismatches}")
print(f"Unlogged files on disk: {unlogged_files}")


# 2. Check .gitignore rules against git tracking
print("\n--- Step 2: Validating .gitignore rules ---")
test_patterns = [
    ("__pycache__/", True),
    ("venv/", True),
    ("output/test.hwp", True),
    ("scratch_test.py", True),
    ("check_test.py", True),
    ("main.py", False)
]

gitignore_results = []
for item, expected_ignored in test_patterns:
    res = subprocess.run(["git", "check-ignore", "-v", item], cwd=kcs_dir, capture_output=True, text=True)
    is_ignored = res.returncode == 0
    gitignore_results.append((item, is_ignored, expected_ignored, res.stdout.strip()))
    print(f"Item: {item:20s} | Ignored: {str(is_ignored):5s} | Expected: {str(expected_ignored):5s} | Rule: {res.stdout.strip()}")

# 3. Check git commit log integrity
print("\n--- Step 3: Validating git commit log integrity ---")
res_log = subprocess.run(["git", "log", "-n", "1", "--stat"], cwd=kcs_dir, capture_output=True, text=True)
print("Git log output:")
print(res_log.stdout)

res_status = subprocess.run(["git", "status", "--porcelain"], cwd=kcs_dir, capture_output=True, text=True)
print(f"Git working tree status (clean if empty): '{res_status.stdout.strip()}'")

# 4. Check remote status
print("\n--- Step 4: Validating git remote and push status ---")
res_remote = subprocess.run(["git", "remote", "-v"], cwd=kcs_dir, capture_output=True, text=True)
print("Git remotes:")
print(res_remote.stdout)

res_branch = subprocess.run(["git", "status", "-sb"], cwd=kcs_dir, capture_output=True, text=True)
print("Branch status:")
print(res_branch.stdout.strip())

print("\n=== Verification Finished ===")
