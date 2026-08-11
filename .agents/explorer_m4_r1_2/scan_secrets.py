import os
import re

base = r'c:\Users\solto\OneDrive\문서\KCS_Automation'
patterns = [
    (r'(?i)api[_\-]?key\s*=\s*["\']([^"\']+)["\']', 'API Key assignment'),
    (r'(?i)secret[_\-]?key\s*=\s*["\']([^"\']+)["\']', 'Secret Key assignment'),
    (r'(?i)token\s*=\s*["\']([^"\']+)["\']', 'Token assignment'),
    (r'AIzaSy[A-Za-z0-9_\-]{31}', 'Google API Key pattern'),
    (r'sk-[A-Za-z0-9]{32,}', 'OpenAI Key pattern'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
    (r'gho_[A-Za-z0-9]{36}', 'GitHub OAuth Token')
]

findings = []
for root, dirs, files in os.walk(base):
    if '__pycache__' in root or '.pytest_cache' in root:
        continue
    for f in files:
        if f.endswith(('.db', '.pyc', '.hwp')):
            continue
        filepath = os.path.join(root, f)
        relpath = os.path.relpath(filepath, base)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                content = file_obj.read()
                for pat, label in patterns:
                    matches = re.findall(pat, content)
                    if matches:
                        # filter out generic placeholders
                        filtered = [m for m in matches if not isinstance(m, str) or ('your_' not in m.lower() and 'dummy' not in m.lower() and 'test' not in m.lower())]
                        if filtered:
                            findings.append((relpath, label, filtered[:3]))
        except Exception as e:
            print(f'Error reading {relpath}: {e}')

print(f'Security Scan complete. Total suspicious findings: {len(findings)}')
for rel, label, sample in findings:
    print(f'  [{label}] in {rel}: sample={sample}')
