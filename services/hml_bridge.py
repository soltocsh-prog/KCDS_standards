import os
from services.hml_generator import HmlGenerator

class HmlOrchestrationBridge:
    def __init__(self, template_path: str, use_jinja: bool = False):
        self.template_path = template_path
        self.use_jinja = use_jinja

    def generate_hml(self, merged_document: list, output_path: str):
        """
        Takes the merged KCS document array from DocumentOrchestrator,
        generates individual HML contents for each, extracts their Section 2,
        and merges them into a single HWPML document with separate <SECTION> elements.
        """
        if self.use_jinja:
            from services.jinja2_generator.jinja2_hml_generator import Jinja2HmlGenerator
            generator = Jinja2HmlGenerator(self.template_path)
            # Jinja2 렌더러에 맞게 데이터 전달 (임시 stub 호출)
            if hasattr(generator, "generate"):
                generator.generate(merged_document, output_path)
            return

        # Filter out page breaks to get KCS document dictionaries
        docs = [doc for doc in merged_document if doc.get("type") != "page_break"]
        if not docs:
            return

        # 1. Create generators for each KCS document
        generators = []
        for doc in docs:
            gen = HmlGenerator(self.template_path)
            raw_code = doc.get("code", "")
            name = doc.get("name", "")
            
            # Replace placeholders in the entire tree for this document
            gen.replace_placeholders(code=raw_code, name=name, code_type="KCS")
            
            # Build flat items for this specific document
            doc_title = f"KCS {raw_code} {name}"
            flat_items = [
                {
                    "level": 0,
                    "label": "",
                    "contents": doc_title
                }
            ]
            for sec in doc.get("content_sections", []):
                flat_items.append({
                    "level": sec.get("level", 4),
                    "label": sec.get("label", ""),
                    "contents": sec.get("content", "")
                })
                
            # Insert content into Section 2 of this generator
            gen.insert_content(flat_items)
            generators.append(gen)

        # 2. Merge Section 2 from subsequent documents into the first document's BODY
        primary_gen = generators[0]
        primary_body = primary_gen.root.find('.//BODY')
        
        import xml.etree.ElementTree as ET
        primary_mapping = primary_gen.root.find('.//MAPPINGTABLE')
        if primary_mapping is None:
            head = primary_gen.root.find('.//HEAD')
            primary_mapping = ET.SubElement(head, 'MAPPINGTABLE')
            
        primary_bindatalist = primary_gen.root.find('.//BINDATALIST')
        if primary_bindatalist is None:
            primary_bindatalist = ET.Element('BINDATALIST', {'Count': '0'})
            primary_mapping.insert(0, primary_bindatalist)

        primary_tail = primary_gen.root.find('.//TAIL')
        if primary_tail is None:
            primary_tail = ET.SubElement(primary_gen.root, 'TAIL')
            
        primary_bindatastorage = primary_gen.root.find('.//BINDATASTORAGE')
        if primary_bindatastorage is None:
            primary_bindatastorage = ET.Element('BINDATASTORAGE')
            primary_tail.insert(0, primary_bindatastorage)
            
        for idx, next_gen in enumerate(generators[1:], start=3):
            next_sections = next_gen.root.findall('.//SECTION')
            if len(next_sections) >= 3:
                sec2 = next_sections[2]
                sec2.set('Id', str(idx))
                
                next_bindatalist = next_gen.root.find('.//BINDATALIST')
                next_bindatastorage = next_gen.root.find('.//BINDATASTORAGE')
                
                if next_bindatalist is not None and next_bindatastorage is not None:
                    id_mapping = {}
                    for binitem in next_bindatalist.findall('BINITEM'):
                        old_id = binitem.get('BinData')
                        
                        primary_count = int(primary_bindatalist.get('Count', '0'))
                        new_id = str(primary_count + 1)
                        primary_bindatalist.set('Count', new_id)
                        
                        # Ensure we duplicate the element if we modify and append it
                        import copy
                        new_binitem = copy.deepcopy(binitem)
                        new_binitem.set('BinData', new_id)
                        primary_bindatalist.append(new_binitem)
                        
                        bindata = next_bindatastorage.find(f"BINDATA[@Id='{old_id}']")
                        if bindata is not None:
                            new_bindata = copy.deepcopy(bindata)
                            new_bindata.set('Id', new_id)
                            primary_bindatastorage.append(new_bindata)
                            
                        id_mapping[old_id] = new_id
                        
                    for image in sec2.findall('.//IMAGE'):
                        old_id = image.get('BinItem')
                        if old_id in id_mapping:
                            image.set('BinItem', id_mapping[old_id])
                
                primary_body.append(sec2)

        # 3. Clean up the empty starting paragraph in all KCS body sections (Section 2 and onwards)
        def clean_section_start(section):
            p_elements = section.findall('P')
            if len(p_elements) < 2:
                return
            first_p = p_elements[0]
            second_p = p_elements[1]
            first_text = first_p.find('TEXT')
            second_text = second_p.find('TEXT')
            if first_text is not None and second_text is not None:
                to_move = []
                for child in first_text:
                    if child.tag != 'CHAR':
                        to_move.append(child)
                for child in reversed(to_move):
                    first_text.remove(child)
                    second_text.insert(0, child)
                section.remove(first_p)

        all_sections = primary_gen.root.findall('.//SECTION')
        # Clean Section 2 and any newly appended sections
        for s in all_sections[2:]:
            clean_section_start(s)

        # 4. Dynamically disable PageBreakBefore on the title style (KCSC_대분류_[00 00 00])
        # so that the title paragraphs at the start of each section do not trigger an extra blank page
        for style in primary_gen.root.iter('STYLE'):
            if style.get('Name') == 'KCSC_대분류_[00 00 00]':
                para_shape_id = style.get('ParaShape')
                if para_shape_id:
                    for ps in primary_gen.root.findall('.//PARASHAPE'):
                        if ps.get('Id') == para_shape_id:
                            ps.set('PageBreakBefore', 'false')

        # 5. Update the total section count (SecCnt) in the HEAD tag
        head = primary_gen.root.find('.//HEAD')
        if head is not None:
            head.set('SecCnt', str(2 + len(docs)))

        # 6. Save the merged HML document
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        primary_gen.save(output_path)

