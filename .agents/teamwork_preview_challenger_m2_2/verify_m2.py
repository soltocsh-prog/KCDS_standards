import os
import json
import hashlib
import sys

def run_checks():
    soltovity_dir = r"c:\Users\solto\OneDrive\문서\Soltovity"
    kcs_dir = r"c:\Users\solto\OneDrive\문서\KCS_Automation"

    print("=== STARTING MILSTONE 2 EMPIRICAL STRESS TESTS ===")

    # 1. Directory permissions & accessibility
    dirs_to_check = [
        kcs_dir,
        os.path.join(kcs_dir, "docs"),
        os.path.join(kcs_dir, "docs", "samples")
    ]

    for d in dirs_to_check:
        if not os.path.exists(d):
            print(f"FAIL: Directory does not exist: {d}")
            sys.exit(1)
        if not os.access(d, os.R_OK | os.W_OK | os.X_OK):
            print(f"FAIL: Directory permissions restricted: {d}")
            sys.exit(1)
        print(f"PASS: Directory accessible & valid permissions: {d}")

    # File mapping: (source_rel_path, target_rel_path)
    files_to_check = [
        ("CONTEXT.md", "CONTEXT.md"),
        ("migration_guide.md", "migration_guide.md"),
        (os.path.join(".agents", "ORIGINAL_REQUEST.md"), os.path.join("docs", "REQUIREMENTS.md")),
        ("kcs_142010_api_response.json", os.path.join("docs", "samples", "kcs_142010_api_response.json")),
        ("kcs_14_20_10.json", os.path.join("docs", "samples", "kcs_14_20_10.json")),
    ]

    results = []

    for src_rel, tgt_rel in files_to_check:
        src_path = os.path.join(soltovity_dir, src_rel)
        tgt_path = os.path.join(kcs_dir, tgt_rel)

        print(f"\n--- Checking File: {tgt_rel} ---")
        
        # Existence & readability
        if not os.path.exists(tgt_path):
            print(f"FAIL: Target file missing: {tgt_path}")
            sys.exit(1)
        if not os.access(tgt_path, os.R_OK):
            print(f"FAIL: Target file not readable: {tgt_path}")
            sys.exit(1)

        # Raw Bytes Inspection
        with open(tgt_path, 'rb') as f:
            raw_bytes = f.read()

        file_size = len(raw_bytes)
        print(f"Size: {file_size} bytes")
        if file_size == 0:
            print(f"FAIL: Target file is empty: {tgt_path}")
            sys.exit(1)

        # BOM Check
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            print(f"FAIL: UTF-8 BOM detected in {tgt_path}")
            sys.exit(1)
        else:
            print("BOM Check: PASSED (No BOM)")

        # UTF-8 Strict Decoding Check
        try:
            text_content = raw_bytes.decode('utf-8', errors='strict')
            print("UTF-8 Decoding: PASSED (Strict UTF-8)")
        except UnicodeDecodeError as e:
            print(f"FAIL: UTF-8 decoding error in {tgt_path}: {e}")
            sys.exit(1)

        # Replacement / Corrupt Character Check
        if '\ufffd' in text_content:
            print(f"FAIL: Corrupt character (\\ufffd) found in {tgt_path}")
            sys.exit(1)
        else:
            print("Corrupt Char Check: PASSED (No \\ufffd)")

        # Null Byte Check
        if b'\x00' in raw_bytes:
            print(f"FAIL: Null byte (\\x00) found in {tgt_path}")
            sys.exit(1)
        else:
            print("Null Byte Check: PASSED")

        # Line Ending Stress Test
        has_crlf = b'\r\n' in raw_bytes
        has_bare_lf = False
        # Remove CRLF and check if any single \n remains
        bytes_no_crlf = raw_bytes.replace(b'\r\n', b'')
        if b'\n' in bytes_no_crlf:
            has_bare_lf = True
        has_bare_cr = b'\r' in bytes_no_crlf

        if b'\r\r\n' in raw_bytes:
            print(f"FAIL: Corrupted double-CR line ending (\\r\\r\\n) in {tgt_path}")
            sys.exit(1)

        line_style = []
        if has_crlf: line_style.append("CRLF")
        if has_bare_lf: line_style.append("LF")
        if has_bare_cr: line_style.append("CR")
        print(f"Line Endings Detected: {', '.join(line_style)}")

        # JSON Structural Validation (if applicable)
        if tgt_rel.endswith('.json'):
            try:
                parsed_json = json.loads(text_content)
                print(f"JSON Validation: PASSED (Type: {type(parsed_json).__name__}, keys/elements: {len(parsed_json)})")
            except Exception as e:
                print(f"FAIL: JSON parsing failed for {tgt_path}: {e}")
                sys.exit(1)

        # SHA256 Checksum Match against Source
        with open(src_path, 'rb') as f:
            src_bytes = f.read()

        src_hash = hashlib.sha256(src_bytes).hexdigest()
        tgt_hash = hashlib.sha256(raw_bytes).hexdigest()

        if src_hash != tgt_hash:
            print(f"FAIL: SHA256 mismatch!\n  Source ({src_rel}): {src_hash}\n  Target ({tgt_rel}): {tgt_hash}")
            sys.exit(1)
        else:
            print(f"SHA256 Checksum Match: PASSED ({tgt_hash})")

        results.append({
            "target": tgt_rel,
            "size": file_size,
            "hash": tgt_hash,
            "line_endings": ', '.join(line_style),
            "status": "PASS"
        })

    print("\n=== ALL FILE INTEGRITY STRESS TESTS PASSED SUCCESSFULLY ===")
    return results

if __name__ == "__main__":
    run_checks()
