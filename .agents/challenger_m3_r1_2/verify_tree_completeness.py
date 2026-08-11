import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

KCS_DIR = r"c:\Users\solto\OneDrive\문서\KCS_Automation"
README_PATH = os.path.join(KCS_DIR, "README.md")

with open(README_PATH, "r", encoding="utf-8") as f:
    readme_text = f.read()

# Extract directory tree block from README
tree_match = readme_text.split("```")[1] # First code block is tree architecture

# Collect all files on disk in KCS_Automation (excluding .git and output/ if generated)
ignore_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", "output"}

disk_files = []
for root, dirs, files in os.walk(KCS_DIR):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        rel_path = os.path.relpath(os.path.join(root, file), KCS_DIR).replace(os.sep, "/")
        disk_files.append(rel_path)

print(f"Total files on disk in KCS_Automation (excluding runtime/git dirs): {len(disk_files)}")

missing_in_tree = []
for file in disk_files:
    filename = os.path.basename(file)
    if filename not in tree_match and file not in tree_match:
        missing_in_tree.append(file)

if missing_in_tree:
    print("Files on disk not found in README tree/text:", missing_in_tree)
else:
    print("ALL disk files are accounted for in the README tree/text!")
