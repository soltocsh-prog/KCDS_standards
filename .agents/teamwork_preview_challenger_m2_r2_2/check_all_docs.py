import os

def check_folder_docs(folder, label):
    print(f"=== Scanning docs in {label}: {folder} ===")
    boms = []
    decode_errs = []
    checked = []
    
    for root, dirs, files in os.walk(folder):
        if '.git' in root or '.agents' in root or '__pycache__' in root or '.pytest_cache' in root:
            continue
        for f in files:
            if f.endswith(('.md', '.json', '.txt', '.py', '.bat')):
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, folder)
                with open(fp, 'rb') as file_obj:
                    content = file_obj.read()
                checked.append(rel)
                if content.startswith(b'\xef\xbb\xbf'):
                    boms.append(rel)
                try:
                    content.decode('utf-8')
                except Exception as e:
                    decode_errs.append((rel, str(e)))
                    
    print(f"Total text/doc files checked: {len(checked)}")
    print(f"BOM count: {len(boms)}")
    if boms:
        print(f"  Files with BOM: {boms}")
    print(f"Decode error count: {len(decode_errs)}")
    if decode_errs:
        for r, err in decode_errs:
            print(f"  {r}: {err}")

check_folder_docs(r"c:\Users\solto\OneDrive\문서\KCS_Automation", "KCS_Automation")
check_folder_docs(r"c:\Users\solto\OneDrive\문서\Soltovity", "Soltovity")
