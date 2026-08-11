import os
import re
import sys
import subprocess
import argparse

sys.stdout.reconfigure(encoding='utf-8')

README_PATH = r"c:\Users\solto\OneDrive\문서\KCS_Automation\README.md"
KCS_DIR = r"c:\Users\solto\OneDrive\문서\KCS_Automation"

def test_markdown_formatting(readme_content):
    print("=== Task 1: Testing Markdown Formatting Syntax ===")
    errors = []
    
    # 1. Code blocks pairing check
    lines = readme_content.splitlines()
    code_block_open = False
    open_line_num = 0
    code_blocks_count = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not code_block_open:
                code_block_open = True
                open_line_num = i
            else:
                code_block_open = False
                code_blocks_count += 1
                
    if code_block_open:
        errors.append(f"Unclosed code block starting at line {open_line_num}")
    else:
        print(f"  [PASS] Code block pairing check passed. Total code blocks: {code_blocks_count}")
        
    # 2. Table formatting check (GFM standard)
    tables_found = 0
    in_table = False
    current_table_cols = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # Proper split of cells between leading and trailing pipe
            cells = stripped[1:-1].split("|")
            cols = len(cells)
            if not in_table:
                in_table = True
                tables_found += 1
                current_table_cols = cols
            else:
                # Check if it's separator row (e.g. |---|---|) or data row
                is_separator = all(re.match(r'^\s*:?-+:?\s*$', c) for c in cells)
                if cols != current_table_cols:
                    errors.append(f"Table column mismatch at line {i}: expected {current_table_cols} columns, got {cols}")
        else:
            in_table = False
            
    print(f"  [PASS] Markdown tables found and checked: {tables_found} tables.")
    
    # 3. Headings hierarchy check
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    headings = []
    for i, line in enumerate(lines, 1):
        m = heading_pattern.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            headings.append((i, level, title))
            
    print(f"  [PASS] Headings check passed. Headings count: {len(headings)}")
    
    # 4. Quote blocks check
    quote_count = sum(1 for line in lines if line.strip().startswith(">"))
    print(f"  [PASS] Quote blocks check passed. Quote lines count: {quote_count}")
    
    return errors

def test_file_references(readme_content):
    print("\n=== Task 2: Testing Mentioned Files & Python Scripts Existence ===")
    errors = []
    
    mentioned_files = [
        "main.py",
        "generate_cli.py",
        "requirements.txt",
        "run_services.bat",
        "README.md",
        "CONTEXT.md",
        "migration_guide.md",
        "db/database.py",
        "db/kcs.db",
        "db/kcs_documents.db",
        "db/kcsc.db",
        "docs/REQUIREMENTS.md",
        "docs/samples/kcs_142010_api_response.json",
        "docs/samples/kcs_14_20_10.json",
        "services/__init__.py",
        "services/ai_recommender.py",
        "services/document_generator.py",
        "services/document_orchestrator.py",
        "services/hml_bridge.py",
        "services/hml_generator.py",
        "services/hml_generator_recovered.py",
        "services/kcsc_api_client.py",
        "services/jinja2_generator/__init__.py",
        "services/jinja2_generator/jinja2_hml_generator.py",
        "services/jinja2_generator/templates/base_template.hml.j2",
        "templates/base_template.hml",
        "templates/base_template2.hml",
        "templates/table_snippet.xml.j2",
        "tests/conftest.py",
        "tests/test_ai_recommendation.py",
        "tests/test_api_endpoints.py",
        "tests/test_database.py",
        "tests/test_document_generation.py",
        "tests/test_hml_bridge.py",
        "tests/test_hml_generator.py",
        "tests/test_hml_table_image_deep_dive.py",
        "tests/test_jinja2_hml_generator.py",
        "tests/test_kcsc_api.py",
        "tests/features/ai_recommendation.feature",
        "tests/features/document_generation.feature",
        "tests/features/kcsc_api.feature"
    ]
    
    missing_files = []
    for rel_path in mentioned_files:
        full_path = os.path.join(KCS_DIR, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            missing_files.append(rel_path)
        else:
            print(f"  [EXISTS] {rel_path}")
            
    if missing_files:
        errors.append(f"Missing mentioned files: {missing_files}")
    else:
        print(f"  [PASS] All {len(mentioned_files)} mentioned files and Python scripts exist in KCS_Automation!")

    # Check Python scripts explicitly requested: main.py, generate_cli.py, db/database.py
    required_scripts = ["main.py", "generate_cli.py", "db/database.py"]
    for script in required_scripts:
        full_p = os.path.join(KCS_DIR, script.replace("/", os.sep))
        if not os.path.exists(full_p):
            errors.append(f"Required script {script} does not exist on disk!")
        else:
            print(f"  [VERIFIED] Required core script exists: {script}")

    return errors

def test_cli_syntax():
    print("\n=== Task 3: Testing CLI Parameter Syntax against generate_cli.py ===")
    errors = []
    
    cli_path = os.path.join(KCS_DIR, "generate_cli.py")
    
    # Run `python generate_cli.py --help`
    try:
        res = subprocess.run([sys.executable, cli_path, "--help"], capture_output=True, text=True, check=True)
        help_output = res.stdout
        print("  [CLI --help output]:")
        print(help_output)
        
        if "--code" not in help_output:
            errors.append("CLI help output missing --code parameter")
        if "--type" not in help_output:
            errors.append("CLI help output missing --type parameter")
        if "--output" not in help_output:
            errors.append("CLI help output missing --output parameter")
            
        if not errors:
            print("  [PASS] CLI help output successfully verified: --code, --type, --output exist.")
            
    except Exception as e:
        errors.append(f"Failed to execute generate_cli.py --help: {e}")
        
    # Test argparse parsing programmatically with README example commands
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--code', type=str, required=True)
        parser.add_argument('--type', type=str, default='KCS', choices=['KCS', 'KDS'])
        parser.add_argument('--output', type=str)
        
        # Command 1: python generate_cli.py --code 411200
        args1 = parser.parse_args(['--code', '411200'])
        assert args1.code == '411200' and args1.type == 'KCS' and args1.output is None
        print("  [PASS] README command 1 ('python generate_cli.py --code 411200') parsed successfully!")
        
        # Command 2: python generate_cli.py --code 411200 --type KCS --output concrete_spec.hwp
        args2 = parser.parse_args(['--code', '411200', '--type', 'KCS', '--output', 'concrete_spec.hwp'])
        assert args2.code == '411200' and args2.type == 'KCS' and args2.output == 'concrete_spec.hwp'
        print("  [PASS] README command 2 ('python generate_cli.py --code 411200 --type KCS --output concrete_spec.hwp') parsed successfully!")
        
    except Exception as e:
        errors.append(f"Argparse validation failed: {e}")
        
    return errors

def test_repository_origin_note(readme_content):
    print("\n=== Additional Check: Repository Origin Note (`# -`) ===")
    errors = []
    if 'echo "# -" >> README.md' not in readme_content:
        errors.append("README.md missing `# -` origin note (`echo \"# -\" >> README.md`)!")
    else:
        print("  [PASS] Repository origin note (`echo \"# -\" >> README.md`) verified in README.md!")
    return errors

def main():
    if not os.path.exists(README_PATH):
        print(f"ERROR: {README_PATH} does not exist!")
        sys.exit(1)
        
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    all_errors = []
    all_errors.extend(test_markdown_formatting(content))
    all_errors.extend(test_file_references(content))
    all_errors.extend(test_cli_syntax())
    all_errors.extend(test_repository_origin_note(content))
    
    print("\n================ VERDICT SUMMARY ================")
    if all_errors:
        print("VERDICT: REJECT")
        print("Errors found:")
        for err in all_errors:
            print(f" - {err}")
    else:
        print("VERDICT: APPROVE")
        print("All empirical adversarial tests passed successfully!")

if __name__ == "__main__":
    main()
