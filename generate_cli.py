import os
import sys
import json
import urllib.request
import argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from services.hml_generator import HmlGenerator

def fetch_data(code_type, code):
    # Determine the URL based on type
    url = f"https://kcsc.re.kr/OpenApi/CodeViewer/{code_type}/{code}?key=4MLIHAe8PvbVp3r9S5LH_5KiKp-oPA5bXdhWmCRJoQ8"
    print(f"Fetching from API: {url}")
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            json_str = response.read().decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        print(f"Error fetching API: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate HWP document for KCS/KDS code.")
    parser.add_argument('--code', type=str, required=True, help="The code number (e.g., 411200)")
    parser.add_argument('--type', type=str, default='KCS', choices=['KCS', 'KDS'], help="The document type (KCS or KDS)")
    parser.add_argument('--output', type=str, help="Custom output filename")
    
    args = parser.parse_args()
    
    api_response = fetch_data(args.type, args.code)
    
    if not api_response:
        print("API response is empty or failed.")
        return
        
    doc_data = api_response[0]
    
    code_type = doc_data.get('codeType', args.type)
    raw_code = doc_data.get('code', args.code)
    
    # format code: e.g. 411200 -> 41 12 00
    if len(raw_code) == 6:
        formatted_code = f"{raw_code[:2]} {raw_code[2:4]} {raw_code[4:]}"
    else:
        formatted_code = raw_code
        
    name = doc_data.get('name', '')
    content_list = doc_data.get('list', [])
    
    doc_title = f"{code_type} {formatted_code} {name}"
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'base_template2.hml')
    generator = HmlGenerator(template_path)
    
    print(f"Processing: {code_type} {formatted_code} / {name}")
    generator.replace_placeholders(formatted_code, name, code_type)
    
    print(f"Inserting content... ({len(content_list)} items)")
    generator.insert_content(content_list, doc_title=doc_title)
    
    output_filename = args.output if args.output else f"output_{args.code}.hwp"
    output_path = os.path.join(os.path.dirname(__file__), 'output', output_filename)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    generator.save(output_path)
    print(f"Document generation complete! Saved to: {output_path}")

if __name__ == '__main__':
    main()
