from pathlib import Path

target_dir = Path(r"c:\Users\solto\OneDrive\문서\KCS_Automation")

matches = []
for file_path in target_dir.rglob("*"):
    if file_path.is_file():
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if "Soltovity" in content or "soltovity" in content.lower():
                matches.append(file_path.relative_to(target_dir))
        except Exception as e:
            pass

print("Files containing reference to 'Soltovity':")
for m in matches:
    print(f" - {m}")
