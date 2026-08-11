import ast
import os
from pathlib import Path

target_dir = Path(r"c:\Users\solto\OneDrive\문서\KCS_Automation")

py_files = list(target_dir.rglob("*.py"))
print(f"Found {len(py_files)} Python files in {target_dir}")

external_relative_imports = []
all_imports = []

for py_file in py_files:
    rel_path = py_file.relative_to(target_dir)
    depth = len(rel_path.parts) - 1 # directory depth relative to root
    
    with open(py_file, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(py_file))
        except Exception as e:
            print(f"Error parsing {rel_path}: {e}")
            continue
            
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                all_imports.append((str(rel_path), f"import {name.name}"))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = node.level
            imp_str = f"from {'.' * level}{module} import ..."
            all_imports.append((str(rel_path), imp_str))
            
            # Check relative import level vs file depth
            if level > 0 and level > depth:
                external_relative_imports.append((str(rel_path), level, depth, imp_str))

print("\n--- Summary of Relative Imports pointing outside KCS_Automation ---")
if external_relative_imports:
    for path, level, depth, imp in external_relative_imports:
        print(f"VIOLATION: {path} has relative import '{imp}' (level {level} > depth {depth})")
else:
    print("NO relative imports pointing outside KCS_Automation detected!")

print("\n--- Detailed List of Imports per File ---")
file_imports = {}
for path, imp in all_imports:
    file_imports.setdefault(path, []).append(imp)

for path, imps in file_imports.items():
    print(f"\nFile: {path}")
    for imp in imps:
        print(f"  {imp}")
