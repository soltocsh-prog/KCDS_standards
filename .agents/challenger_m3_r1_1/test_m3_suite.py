import os
import re
import pytest

README_PATH = r"c:\Users\solto\OneDrive\문서\KCS_Automation\README.md"
BASE_DIR = r"c:\Users\solto\OneDrive\문서\KCS_Automation"

def test_readme_file_exists_and_non_empty():
    assert os.path.exists(README_PATH), f"File {README_PATH} does not exist"
    assert os.path.isfile(README_PATH), f"{README_PATH} is not a file"
    size = os.path.getsize(README_PATH)
    assert size > 0, f"File {README_PATH} is empty (size 0)"
    assert size > 1000, f"File {README_PATH} is unexpectedly small ({size} bytes)"

def test_ascii_tree_completeness_and_validity():
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    tree_match = re.search(r"```\s*\n(KCS_Automation/.*?)\n```", content, re.DOTALL)
    assert tree_match is not None, "ASCII tree code block not found in README.md"

    lines = tree_match.group(1).splitlines()
    assert len(lines) > 10, "Tree block has too few lines"

    # Verify root
    assert lines[0].strip() == "KCS_Automation/"

    stack = [BASE_DIR]
    parsed_paths = []

    for line in lines[1:]:
        code_part = line.split('#')[0]
        if not code_part.strip():
            continue

        m = re.search(r"([├└]──\s*|│\s*)+", code_part)
        assert m is not None, f"Invalid tree formatting on line: {line}"

        prefix = code_part[:m.end()]
        name = code_part[m.end():].strip()
        assert len(name) > 0, f"Empty entry name on line: {line}"

        depth = len(prefix) // 4
        while len(stack) > depth:
            stack.pop()

        parent = stack[-1]
        is_dir = name.endswith('/')
        clean_name = name.rstrip('/')
        full_path = os.path.join(parent, clean_name)
        
        parsed_paths.append((full_path, is_dir, line))
        if is_dir:
            stack.append(full_path)

    assert len(parsed_paths) >= 40, f"Expected at least 40 entries in ASCII tree, found {len(parsed_paths)}"

    missing_items = []
    for full_path, is_dir, orig_line in parsed_paths:
        if not os.path.exists(full_path):
            missing_items.append((full_path, "does not exist", orig_line))
        elif is_dir and not os.path.isdir(full_path):
            missing_items.append((full_path, "is not directory", orig_line))
        elif not is_dir and not os.path.isfile(full_path):
            missing_items.append((full_path, "is not file", orig_line))

    assert not missing_items, f"Missing or invalid paths found in ASCII tree: {missing_items}"

def test_zero_forbidden_strings():
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    forbidden_list = ['Soltovity', 'backend/', 'scratch_']
    found_violations = {}
    for item in forbidden_list:
        count = content.count(item)
        if count > 0:
            found_violations[item] = count

    assert not found_violations, f"Forbidden strings found in README.md: {found_violations}"

def test_origin_note_exists():
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    has_echo = 'echo "# -"' in content
    has_origin_note = '# -' in content and ('GitHub' in content or 'repository' in content or 'initial' in content)
    
    assert has_echo or has_origin_note, "Origin note regarding 'echo \"# -\"' or '# -' is missing from README.md"
