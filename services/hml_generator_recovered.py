import xml.etree.ElementTree as ET

def parse_html_to_inline_tokens(soup_node, is_sup=False, is_sub=False):
    import html
    if isinstance(soup_node, str):
        text = html.unescape(soup_node)
        parts = text.split('\n')
        tokens = []
        for i, part in enumerate(parts):
            if part:
                tokens.append({
                    'type': 'text',
                    'text': part,
                    'sup': is_sup,
                    'sub': is_sub
                })
            if i < len(parts) - 1:
                tokens.append({'type': 'linebreak'})
        return tokens

    name = getattr(soup_node, 'name', None)
    if name is None:
        text = html.unescape(str(soup_node))
        parts = text.split('\n')
        tokens = []
        for i, part in enumerate(parts):
            if part:
                tokens.append({
                    'type': 'text',
                    'text': part,
                    'sup': is_sup,
                    'sub': is_sub
                })
            if i < len(parts) - 1:
                tokens.append({'type': 'linebreak'})
        return tokens

    name = name.lower()
    if name in ['br', 'br/']:
        return [{'type': 'linebreak'}]
    elif name == 'sup':
        tokens = []
        for child in getattr(soup_node, 'children', []):
            tokens.extend(parse_html_to_inline_tokens(child, is_sup=True, is_sub=is_sub))
        return tokens
    elif name == 'sub':
        tokens = []
        for child in getattr(soup_node, 'children', []):
            tokens.extend(parse_html_to_inline_tokens(child, is_sup=is_sup, is_sub=True))
        return tokens
    elif name == 'img':
        return [{
            'type': 'image',
            'html': str(soup_node)
        }]
    elif name in ['p', 'div', 'tr', 'td']:
        tokens = []
        sub_tokens = []
        for child in getattr(soup_node, 'children', []):
            sub_tokens.extend(parse_html_to_inline_tokens(child, is_sup, is_sub))
        if sub_tokens:
            tokens.append({'type': 'linebreak'})
            tokens.extend(sub_tokens)
            tokens.append({'type': 'linebreak'})
        return tokens
    else:
        tokens = []
        for child in getattr(soup_node, 'children', []):
            tokens.extend(parse_html_to_inline_tokens(child, is_sup, is_sub))
        return tokens

def clean_and_merge_tokens(tokens):
    merged = []
    for t in tokens:
        if t['type'] == 'text':
            if not t['text']:
                continue
            if merged and merged[-1]['type'] == 'text' and merged[-1]['sup'] == t['sup'] and merged[-1]['sub'] == t['sub']:
                merged[-1]['text'] += t['text']
            else:
                merged.append(t)
        else:
            merged.append(t)
            
    final_tokens = []
    for t in merged:
        if t['type'] == 'linebreak':
            if final_tokens and final_tokens[-1]['type'] == 'linebreak':
                continue
            final_tokens.append(t)
        else:
            final_tokens.append(t)
            
    while final_tokens and final_tokens[0]['type'] == 'linebreak':
        final_tokens.pop(0)
    while final_tokens and final_tokens[-1]['type'] == 'linebreak':
        final_tokens.pop()
        
    return final_tokens

def format_note_tokens(tokens):
    import re
    text_parts = []
    token_indices = []
    
    for t_idx, t in enumerate(tokens):
        if t['type'] == 'text':
            for c_idx, char in enumerate(t['text']):
                token_indices.append((t_idx, c_idx))
            text_parts.append(t['text'])
        else:
            token_indices.append((t_idx, -1))
            text_parts.append(' ')
            
    full_text = "".join(text_parts)
    
    pattern = r'(\d+\)|\(\d+\)|[①-⑮]|(?:기호|참고|주)\])'
    matches = list(re.finditer(pattern, full_text))
    if not matches:
        return tokens
        
    insert_newline_at = set()
    for i in range(1, len(matches)):
        between = full_text[matches[i-1].end():matches[i].start()]
        if between.strip() != "":
            insert_newline_at.add(matches[i].start())
            
    new_tokens = []
    char_idx = 0
    current_text_token = None
    
    for t_idx, t in enumerate(tokens):
        if t['type'] != 'text':
            if current_text_token:
                new_tokens.append(current_text_token)
                current_text_token = None
            new_tokens.append(t)
            char_idx += 1
            continue
            
        for c_idx, char in enumerate(t['text']):
            if char_idx in insert_newline_at:
                if current_text_token:
                    new_tokens.append(current_text_token)
                    current_text_token = None
                new_tokens.append({'type': 'linebreak'})
                
            if current_text_token is not None and (current_text_token['sup'] != t['sup'] or current_text_token['sub'] != t['sub']):
                new_tokens.append(current_text_token)
                current_text_token = None
                
            if current_text_token is None:
                current_text_token = {
                    'type': 'text',
                    'text': '',
                    'sup': t['sup'],
                    'sub': t['sub']
                }
            current_text_token['text'] += char
            char_idx += 1
            
    if current_text_token:
        new_tokens.append(current_text_token)
        
    # Clean up whitespace on start of each line
    cleaned_tokens = []
    line_start = True
    for t in new_tokens:
        if t['type'] == 'linebreak':
            cleaned_tokens.append(t)
            line_start = True
        elif t['type'] == 'text':
            cleaned_text = t['text']
            if line_start:
                cleaned_text = cleaned_text.lstrip()
                line_start = False
            if cleaned_text:
                t['text'] = cleaned_text
                cleaned_tokens.append(t)
        else:
            cleaned_tokens.append(t)
            line_start = False
            
    return cleaned_tokens

class HmlGenerator:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.tree = ET.parse(template_path)
        self.root = self.tree.getroot()
        
        # 표 테두리를 위한 BORDERFILL 동적 추가 (사방 실선)
        borderfill_list = self.root.find('.//BORDERFILLLIST')
        if borderfill_list is not None:
            count = int(borderfill_list.get('Count', '0'))
            self.table_borderfill_id = str(count + 1)
            borderfill_list.set('Count', self.table_borderfill_id)
            
            bf = ET.SubElement(borderfill_list, 'BORDERFILL', {
                'Id': self.table_borderfill_id, 'ThreeD': 'false', 'Shadow': 'false',
                'CenterLine': '0', 'Slash': '0', 'BackSlash': '0',
                'CrookedSlash': '0', 'CounterSlash': '0', 'CounterBackSlash': '0'
            })
            for border in ['LEFTBORDER', 'RIGHTBORDER', 'TOPBORDER', 'BOTTOMBORDER']:
                ET.SubElement(bf, border, {'Type': 'Solid', 'Width': '0.12mm', 'Color': '0'})
        else:
            self.table_borderfill_id = '1'

        # 위첨자(super) 및 아래첨자(sub)를 위한 CHARSHAPE 동적 복제 및 추가
        charshape_list = self.root.find('.//CHARSHAPELIST')
        if charshape_list is not None:
            import copy
            existing_shapes = list(charshape_list.findall('CHARSHAPE'))
            new_count = len(existing_shapes)
            for cs in existing_shapes:
                old_id = cs.get('Id')
                if old_id is None:
                    continue
                try:
                    old_id_int = int(old_id)
                except ValueError:
                    continue
                
                # 1. 위첨자용 (ID = 원본 + 100)
                super_cs = copy.deepcopy(cs)
                super_cs.set('Id', str(old_id_int + 100))
                relsize = super_cs.find('RELSIZE')
                if relsize is not None:
                    for lang in relsize.attrib:
                        relsize.set(lang, '70')
                charoffset = super_cs.find('CHAROFFSET')
                if charoffset is not None:
                    for lang in charoffset.attrib:
                        charoffset.set(lang, '33')
                charshape_list.append(super_cs)
                new_count += 1
                
                # 2. 아래첨자용 (ID = 원본 + 200)
                sub_cs = copy.deepcopy(cs)
                sub_cs.set('Id', str(old_id_int + 200))
                relsize = sub_cs.find('RELSIZE')
                if relsize is not None:
                    for lang in relsize.attrib:
                        relsize.set(lang, '70')
                charoffset = sub_cs.find('CHAROFFSET')
                if charoffset is not None:
                    for lang in charoffset.attrib:
                        charoffset.set(lang, '-15')
                charshape_list.append(sub_cs)
                new_count += 1
                
            charshape_list.set('Count', str(new_count))

        self.image_cache = {}

    def replace_placeholders(self, code: str, name: str, code_type: str = ""):
        for node in self.root.iter():
            if node.text:
                if '[코드]' in node.text:
                    node.text = node.text.replace('[코드]', code)
# MISSING LINE 261
# MISSING LINE 262
# MISSING LINE 263
# MISSING LINE 264
# MISSING LINE 265
# MISSING LINE 266
# MISSING LINE 267
# MISSING LINE 268
# MISSING LINE 269
# MISSING LINE 270
# MISSING LINE 271
# MISSING LINE 272
# MISSING LINE 273
# MISSING LINE 274
    def map_kcsc_to_style(self, level: int, label: str) -> str:
        import re
        
        if not hasattr(self, 'current_classification_level'):
            self.current_classification_level = 0
            self.last_item_type = 'classification'
            self.last_list_relative_depth = 1
            
        if level == 0:
            self.current_classification_level = 0
            self.last_item_type = 'classification'
            return "KCSC_대분류_[00 00 00]"
            
        if label == "본문" or not label:
            if self.last_item_type == 'classification':
                return "KCSC_본문1"
            else:
                body_level = self.last_list_relative_depth + 1
                if body_level > 5:
                    body_level = 5
                return f"KCSC_본문{body_level}"
            
        # 기호 형태가 1., 1.1, 1.1.1 과 같이 마침표를 포함한 숫자 패턴인지 확인
        is_classification = bool(re.match(r'^\d+(?:\.\d+)*\.?$', label.strip()))
        
        if is_classification:
            self.current_classification_level = level
            self.last_item_type = 'classification'
            if level == 1:
                return "KCSC_중분류_[1.]"
            elif level == 2:
                return "KCSC_소분류_[1.1]"
            elif level == 3:
                return "KCSC_초소분류_[1.1.1]"
            else:
                return "KCSC_미니분류_[1.1.1.1]"
        else:
            self.last_item_type = 'list'
            # 기호 패턴이 아니면 리스트 적용 (분류 기준 상대 깊이로 매핑)
            relative_depth = level - self.current_classification_level
            if relative_depth < 1:
                relative_depth = 1
                
            self.last_list_relative_depth = relative_depth
                
            list_level = relative_depth + 1
            if list_level > 5:
                list_level = 5
                
            return f"KCSC_리스트{list_level}"

    def insert_content(self, data: list, doc_title: str = None):
        import xml.etree.ElementTree as ET
        import re
        import html
        
        style_map = {}
        for style in self.root.iter('STYLE'):
            name = style.get('Name')
            style_id = style.get('Id')
            para = style.get('ParaShape', '0')
            char_shape = style.get('CharShape', '0')
            if name and style_id:
                style_map[name] = {'Id': style_id, 'ParaShape': para, 'CharShape': char_shape}
                
        target_p = None
        target_parent = None
        
        for parent in self.root.iter():
            for child in parent:
                if child.tag == 'P':
                    full_text = "".join(child.itertext())
                    if '[본문 시작]' in full_text:
                        target_p = child
                        target_parent = parent
                        break
                
        if target_p is None or target_parent is None:
            return
            
        # 본문 시작 텍스트만 비워두어 페이지 구분(Page Break) 유지
        for char in target_p.iter('CHAR'):
            if char.text and '[본문 시작]' in char.text:
                char.text = char.text.replace('[본문 시작]', '')
            if char.tail and '[본문 시작]' in char.tail:
                char.tail = char.tail.replace('[본문 시작]', '')
                
        # [본문 시작]이 있던 문단 '바로 다음'부터 내용 삽입
        p_index = list(target_parent).index(target_p) + 1
        
        # 문서 타이틀이 제공되면 첫 줄에 대분류 스타일로 삽입 (여러 문서 병합용)
        if doc_title:
            s_info = style_map.get("KCSC_대분류_[00 00 00]", {'Id': '0', 'ParaShape': '0', 'CharShape': '0'})
            p = ET.Element('P', {'Style': str(s_info['Id']), 'ParaShape': str(s_info['ParaShape'])})
            text_el = ET.SubElement(p, 'TEXT', {'CharShape': str(s_info['CharShape'])})
            char_el = ET.SubElement(text_el, 'CHAR')
            char_el.text = doc_title
            target_parent.insert(p_index, p)
            p_index += 1
        
        for item in data:
            if item.get("type") == "page_break" or item.get("level") == "page_break":
                s_info = style_map.get("KCSC_본문1", {'Id': '0', 'ParaShape': '0', 'CharShape': '0'})
                p = ET.Element('P', {
                    'Style': str(s_info['Id']), 
                    'ParaShape': str(s_info['ParaShape']),
                    'ColumnBreak': 'false',
                    'PageBreak': 'true'
                })
                text_el = ET.SubElement(p, 'TEXT', {'CharShape': str(s_info['CharShape'])})
                ET.SubElement(text_el, 'CHAR')
                target_parent.insert(p_index, p)
                p_index += 1
                continue
                
            level = item.get('level', 4)
            label = item.get('label', '')
            contents = item.get('contents', '')
            
            if '<table' in contents.lower():
                # 1. 캡션 삽입
                s_info = style_map.get('KCSC_표_캡션', {'Id': '0', 'ParaShape': '0', 'CharShape': '0'})
                p_cap = ET.Element('P', {'Style': str(s_info['Id']), 'ParaShape': str(s_info['ParaShape'])})
                t_cap = ET.SubElement(p_cap, 'TEXT', {'CharShape': str(s_info['CharShape'])})
                c_cap = ET.SubElement(t_cap, 'CHAR')
                c_cap.text = label if label else "표"
                target_parent.insert(p_index, p_cap)
                p_index += 1
                
                # 2. 표 삽입
                table_node = self._create_hml_table(contents, style_map)
                if table_node is not None:
                    # sample_table.hml 원본 구조: <P><TEXT><TABLE>...</TABLE><CHAR/></TEXT></P>
                    p_table = ET.Element('P', {'ParaShape': '12', 'Style': '0'})
                    text_table = ET.SubElement(p_table, 'TEXT', {'CharShape': '0'})
                    text_table.append(table_node)
                    ET.SubElement(text_table, 'CHAR')  # 원본 필수 빈 CHAR 태그
                    target_parent.insert(p_index, p_table)
                    p_index += 1
                continue
                
            # HTML 파싱을 통한 본문 및 인라인 이미지 처리
            from bs4 import BeautifulSoup
            import html
            soup = BeautifulSoup(contents, 'html.parser')
            
            style_name = self.map_kcsc_to_style(level, label)
            s_info = style_map.get(style_name, {'Id': '0', 'ParaShape': '0', 'CharShape': '0'})
            
            # 블록 레벨 태그를 만나면 문단을 분리하기 위한 그룹핑
            blocks = []
            current_block = []
            for child in soup.children:
                if getattr(child, 'name', None) in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']:
                    if current_block:
                        blocks.append(current_block)
# MISSING LINE 431
# MISSING LINE 432
# MISSING LINE 433
# MISSING LINE 434
# MISSING LINE 435
# MISSING LINE 436
# MISSING LINE 437
# MISSING LINE 438
# MISSING LINE 439
                
                # Build inline tokens for the block nodes
                raw_tokens = []
                for node in block_nodes:
                    if isinstance(node, str):
                        unescaped = html.unescape(node).replace('\n', ' ')
                        if unescaped:
                            raw_tokens.append({'type': 'text', 'text': unescaped, 'sup': False, 'sub': False})
                    else:
                        raw_tokens.extend(parse_html_to_inline_tokens(node))
                        
                tokens = clean_and_merge_tokens(raw_tokens)
                
                text_el = None
                char_shape = str(s_info['CharShape'])
                
                for idx, token in enumerate(tokens):
                    if token['type'] == 'text':
                        cur_shape = char_shape
                        try:
                            if token['sup']:
                                cur_shape = str(int(char_shape) + 100)
                            elif token['sub']:
                                cur_shape = str(int(char_shape) + 200)
                        except ValueError:
                            pass
                        text_el = ET.SubElement(p, 'TEXT', {'CharShape': cur_shape})
                        char_el = ET.SubElement(text_el, 'CHAR')
                        char_el.text = token['text']
                    elif token['type'] == 'image':
                        pic_node = self._create_hml_picture(token['html'], max_width=40000, is_table=False)
                        if pic_node is not None:
                            if text_el is None:
                                text_el = ET.SubElement(p, 'TEXT', {'CharShape': char_shape})
                            text_el.append(pic_node)
                            
                            has_next_text = (idx + 1 < len(tokens)) and (tokens[idx + 1]['type'] == 'text')
                            if not has_next_text:
                                ET.SubElement(text_el, 'CHAR')
                            
                # Only insert if there's content inside P
                if len(list(p)) > 0:
                    target_parent.insert(p_index, p)
                    p_index += 1

    def _create_hml_table(self, html_table_str: str, style_map: dict):
        from bs4 import BeautifulSoup
        import xml.etree.ElementTree as ET
        import random
        
        try:
            soup = BeautifulSoup(html_table_str, 'lxml')
            table_html = soup.find('table')
            if not table_html: return None
            
            rows = []
            for child in table_html.children:
                if child.name == 'tr':
                    rows.append(child)
                elif child.name in ['tbody', 'thead', 'tfoot']:
                    for subchild in child.children:
                        if subchild.name == 'tr':
                            rows.append(subchild)
            
            row_count = len(rows)
            if row_count == 0: return None
            
            # 2D Grid Tracking: 병합 셀 좌표 추적
            grid = {}
            max_col = 0
            cell_data = []
            
            for r_idx, row in enumerate(rows):
                c_idx = 0
                cells = [child for child in row.children if child.name in ['td', 'th']]
                for cell in cells:
                    while grid.get((r_idx, c_idx), False):
                        c_idx += 1
                    
                    colspan = int(cell.get('colspan', 1))
                    rowspan = int(cell.get('rowspan', 1))
                    
                    cell_data.append({
                        'row': r_idx,
                        'col': c_idx,
                        'colspan': colspan,
                        'rowspan': rowspan,
                        'tokens': tokens
                    })
                    
                    for i in range(rowspan):
                        for j in range(colspan):
                            grid[(r_idx + i, c_idx + j)] = True
                    c_idx += colspan
                    max_col = max(max_col, c_idx)
            
            col_count = max_col if max_col > 0 else 1
            cell_width = 42520 // col_count
            
            row_cells_list = [[] for _ in range(row_count)]
            for data in cell_data:
                row_cells_list[data['row']].append(data)
            
            # sample_table.hml 원본과 100% 동일한 구조로 프로그래밍 조립
            table = ET.Element('TABLE', {
                'BorderFill': self.table_borderfill_id,
                'CellSpacing': '0',
                'ColCount': str(col_count),
                'PageBreak': 'Cell',
                'RepeatHeader': 'true',
                'RowCount': str(row_count)
            })
            
            table_id = str(random.randint(100000000, 2000000000))
            shapeobj = ET.SubElement(table, 'SHAPEOBJECT', {
                'InstId': table_id,
                'Lock': 'false',
                'NumberingType': 'Table',
                'TextWrap': 'TopAndBottom',
                'ZOrder': '0'
            })
            ET.SubElement(shapeobj, 'SIZE', {
                'Height': str(282 * row_count),
                'HeightRelTo': 'Absolute',
                'Protect': 'false',
                'Width': '42520',
                'WidthRelTo': 'Absolute'
            })
            ET.SubElement(shapeobj, 'POSITION', {
                'AffectLSpacing': 'false',
                'AllowOverlap': 'false',
                'FlowWithText': 'true',
                'HoldAnchorAndSO': 'false',
                'HorzAlign': 'Left',
                'HorzOffset': '0',
                'HorzRelTo': 'Column',
                'TreatAsChar': 'false',
                'VertAlign': 'Top',
                'VertOffset': '0',
                'VertRelTo': 'Para'
            })
            ET.SubElement(shapeobj, 'OUTSIDEMARGIN', {
                'Bottom': '1417', 'Left': '283', 'Right': '283', 'Top': '0'
            })
            ET.SubElement(table, 'INSIDEMARGIN', {
                'Bottom': '141', 'Left': '510', 'Right': '510', 'Top': '141'
            })
            
            # ROW/CELL 조립
            row_cells = {r: [] for r in range(row_count)}
            for data in cell_data:
                row_cells[data['row']].append(data)
            
            for r_idx in range(row_count):
                hml_row = ET.SubElement(table, 'ROW')
                for cell_info in sorted(row_cells.get(r_idx, []), key=lambda x: x['col']):
                    hml_cell = ET.SubElement(hml_row, 'CELL', {
                        'BorderFill': self.table_borderfill_id,
                        'ColAddr': str(cell_info['col']),
                        'ColSpan': str(cell_info['colspan']),
                        'Dirty': 'false',
                        'Editable': 'false',
                        'HasMargin': 'false',
                        'Header': 'false',
                        'Height': '282',
                        'Protect': 'false',
                        'RowAddr': str(cell_info['row']),
                        'RowSpan': str(cell_info['rowspan']),
                        'Width': str(cell_width * cell_info['colspan'])
                    })
                    paralist = ET.SubElement(hml_cell, 'PARALIST', {
                        'LineWrap': 'Break',
                        'LinkListID': '0',
                        'LinkListIDNext': '0',
                        'TextDirection': '0',
                        'VertAlign': 'Center'
                    })
                    
                    tokens = cell_info.get('tokens', [])
                    
                    })
                    
                    tokens = cell_info.get('tokens', [])
                    
                    required_height = 282 + 500  # 기본 높이 + 약간의 여백
                    
                    # Detect if note cell
                    raw_text = "".join([t['text'] for t in tokens if t['type'] == 'text'])
                    is_note_cell = False
                    if raw_text:
                        import re
                        stripped_text = raw_text.strip()
                        if re.match(r'^\s*(주|기호|참고)\s*\]', stripped_text):
                            is_note_cell = True
                            
                    if is_note_cell:
                        tokens = format_note_tokens(tokens)
                    
                    s_info_base = style_map.get('KCSC_표_본문', {'Id': '11', 'ParaShape': '16', 'CharShape': '2'})
                    para_shape = s_info_base.get('ParaShape', '16')
                    style_id = s_info_base.get('Id', '11')
                    char_shape = s_info_base.get('CharShape', '2')
                    
                    if is_note_cell:
                        s_info = style_map.get('KCSC_주기', {'Id': '12', 'ParaShape': '6', 'CharShape': '7'})
                        para_shape = s_info.get('ParaShape', '6')
                    
                    if tokens:
                        if is_note_cell:
                            # Group tokens by linebreaks for multiple P paragraphs in notes
                            lines_tokens = []
                            current_line = []
                            for token in tokens:
                                if token['type'] == 'linebreak':
                                    if current_line:
                                        lines_tokens.append(current_line)
                                        current_line = []
                                else:
                                    current_line.append(token)
                            if current_line:
                                        current_line = []
                                else:
                                    current_line.append(token)
                            if current_line:
                                lines_tokens.append(current_line)
                                
                            for line_tokens in lines_tokens:
                                has_text = any(t['type'] == 'text' and t['text'].strip() for t in line_tokens)
                                if not has_text:
                                    continue
                                    
                                p_elem = ET.SubElement(paralist, 'P', {'ParaShape': para_shape, 'Style': style_id})
                                text_el = None
                                required_height += 282
                                
                                for idx_tok, token in enumerate(line_tokens):
                                    if token['type'] == 'text':
                                        cur_shape = char_shape
                                        try:
                                            if token['sup']:
                                        try:
                                            if token['sup']:
                                                cur_shape = getattr(self, 'sup_map', {}).get(char_shape, char_shape)
                                            elif token['sub']:
                                                cur_shape = getattr(self, 'sub_map', {}).get(char_shape, char_shape)
                                        except ValueError:
                                            pass
                                        text_el = ET.SubElement(p_elem, 'TEXT', {'CharShape': cur_shape})
                                        char_el = ET.SubElement(text_el, 'CHAR')
                                        char_el.text = token['text']
                                    elif token['type'] == 'image':
                                        pic_node = self._create_hml_picture(token['html'], max_width=cell_max_width, is_table=True)
                                        if pic_node is not None:
                                            if text_el is None:
                                                text_el = ET.SubElement(p_elem, 'TEXT', {'CharShape': char_shape})
                                            text_el.append(pic_node)
                                            # 그림 뒤에 앵커
                                            has_next_text = (idx_tok + 1 < len(line_tokens)) and (line_tokens[idx_tok + 1]['type'] == 'text')
                                            if not has_next_text:
                                                ET.SubElement(text_el, 'CHAR')
                                            required_height += int(pic_node.get('Height', '0')) + 500
                        else:
                            # 일반 데이터 셀: P 태그 생성
                            p_elem = ET.SubElement(paralist, 'P', {'ParaShape': para_shape, 'Style': style_id})
                            text_el = None
                            
                            for idx_tok, token in enumerate(tokens):
                                if token['type'] == 'linebreak':
                                    if text_el is None:
                                        text_el = ET.SubElement(p_elem, 'TEXT', {'CharShape': char_shape})
                                    ET.SubElement(text_el, 'CHAR', {'Type': 'LineBreak'})
                                    required_height += 282
                                elif token['type'] == 'text':
                                    cur_shape = char_shape
                                    try:
                                        if token['sup']:
                                            cur_shape = getattr(self, 'sup_map', {}).get(char_shape, char_shape)
                                        elif token['sub']:
                                            cur_shape = getattr(self, 'sub_map', {}).get(char_shape, char_shape)
                                    except ValueError:
                                        pass
                                    text_el = ET.SubElement(p_elem, 'TEXT', {'CharShape': cur_shape})
                                    char_el = ET.SubElement(text_el, 'CHAR')
                                    char_el.text = token['text']
                                    # 첫번째 텍스트 라인 높이 누적
                                    if required_height == 282 + 500:
                                        required_height += 282
                                elif token['type'] == 'image':
                                    pic_node = self._create_hml_picture(token['html'], max_width=cell_max_width, is_table=True)
                                    if pic_node is not None:
                                        if text_el is None:
                                            text_el = ET.SubElement(p_elem, 'TEXT', {'CharShape': char_shape})
                                        text_el.append(pic_node)
                                        
                                        has_next_text = (idx_tok + 1 < len(tokens)) and (tokens[idx_tok + 1]['type'] == 'text')
                                        if not has_next_text:
                                            ET.SubElement(text_el, 'CHAR')
                                        required_height += int(pic_node.get('Height', '0')) + 500
                                        
                    # 계산된 넉넉한 높이를 최종적으로 셀에 덮어씌웁니다.
                    hml_cell.set('Height', str(required_height))
# MISSING LINE 741
# MISSING LINE 742
# MISSING LINE 743
# MISSING LINE 744
# MISSING LINE 745
# MISSING LINE 746
# MISSING LINE 747
# MISSING LINE 748
# MISSING LINE 749
# MISSING LINE 750
# MISSING LINE 751
# MISSING LINE 752
# MISSING LINE 753
# MISSING LINE 754
# MISSING LINE 755
# MISSING LINE 756
# MISSING LINE 757
# MISSING LINE 758
# MISSING LINE 759
# MISSING LINE 760
# MISSING LINE 761
# MISSING LINE 762
# MISSING LINE 763
# MISSING LINE 764
# MISSING LINE 765
# MISSING LINE 766
# MISSING LINE 767
# MISSING LINE 768
# MISSING LINE 769
# MISSING LINE 770
# MISSING LINE 771
# MISSING LINE 772
# MISSING LINE 773
# MISSING LINE 774
# MISSING LINE 775
# MISSING LINE 776
# MISSING LINE 777
# MISSING LINE 778
# MISSING LINE 779
# MISSING LINE 780
# MISSING LINE 781
# MISSING LINE 782
# MISSING LINE 783
# MISSING LINE 784
# MISSING LINE 785
# MISSING LINE 786
# MISSING LINE 787
# MISSING LINE 788
# MISSING LINE 789
# MISSING LINE 790
# MISSING LINE 791
# MISSING LINE 792
# MISSING LINE 793
# MISSING LINE 794
# MISSING LINE 795
# MISSING LINE 796
# MISSING LINE 797
# MISSING LINE 798
# MISSING LINE 799
# MISSING LINE 800
# MISSING LINE 801
# MISSING LINE 802
# MISSING LINE 803
# MISSING LINE 804
# MISSING LINE 805
# MISSING LINE 806
# MISSING LINE 807
# MISSING LINE 808
# MISSING LINE 809
# MISSING LINE 810
# MISSING LINE 811
# MISSING LINE 812
# MISSING LINE 813
# MISSING LINE 814
# MISSING LINE 815
# MISSING LINE 816
# MISSING LINE 817
# MISSING LINE 818
# MISSING LINE 819
# MISSING LINE 820
# MISSING LINE 821
# MISSING LINE 822
# MISSING LINE 823
# MISSING LINE 824
# MISSING LINE 825
# MISSING LINE 826
# MISSING LINE 827
# MISSING LINE 828
# MISSING LINE 829
# MISSING LINE 830
# MISSING LINE 831
# MISSING LINE 832
# MISSING LINE 833
# MISSING LINE 834
# MISSING LINE 835
# MISSING LINE 836
# MISSING LINE 837
# MISSING LINE 838
# MISSING LINE 839
# MISSING LINE 840
# MISSING LINE 841
# MISSING LINE 842
# MISSING LINE 843
# MISSING LINE 844
# MISSING LINE 845
# MISSING LINE 846
# MISSING LINE 847
# MISSING LINE 848
# MISSING LINE 849
# MISSING LINE 850
# MISSING LINE 851
# MISSING LINE 852
# MISSING LINE 853
# MISSING LINE 854
# MISSING LINE 855
# MISSING LINE 856
# MISSING LINE 857
# MISSING LINE 858
# MISSING LINE 859
# MISSING LINE 860
# MISSING LINE 861
# MISSING LINE 862
# MISSING LINE 863
# MISSING LINE 864
# MISSING LINE 865
# MISSING LINE 866
# MISSING LINE 867
# MISSING LINE 868
# MISSING LINE 869
# MISSING LINE 870
# MISSING LINE 871
# MISSING LINE 872
# MISSING LINE 873
# MISSING LINE 874
# MISSING LINE 875
# MISSING LINE 876
# MISSING LINE 877
# MISSING LINE 878
# MISSING LINE 879
# MISSING LINE 880
# MISSING LINE 881
# MISSING LINE 882
# MISSING LINE 883
# MISSING LINE 884
# MISSING LINE 885
# MISSING LINE 886
# MISSING LINE 887
# MISSING LINE 888
# MISSING LINE 889
        # 픽셀 -> HWP 단위 환산 (1 픽셀 ≒ 75 Unit)
        hwp_width_int = int(width_px * 75)
        hwp_height_int = int(height_px * 75)
        
        # 셀 폭을 넘어가면 원본 비율 유지하며 축소
        if max_width is not None and hwp_width_int > max_width:
            ratio = max_width / hwp_width_int
            hwp_width_int = max_width
            hwp_height_int = round(hwp_height_int * ratio)
            
        # 세로 높이도 페이지 한계를 넘어가면 비율 유지하며 2차 축소
        max_height = 55000
        if hwp_height_int > max_height:
            ratio = max_height / hwp_height_int
            hwp_height_int = max_height
            hwp_width_int = round(hwp_width_int * ratio)
            
        hwp_width = str(hwp_width_int)
        hwp_height = str(hwp_height_int)
        
        # 렌더링에 필요한 각종 고유 ID 생성 (InstId 등)
        import random
        inst_id = str(random.randint(100000000, 2000000000))
        comp_inst_id = str(random.randint(10000000, 99999999))
        
        # 원본 크기 및 현재 크기 계산
        ori_width = int(width_px * 75)
        ori_height = int(height_px * 75)
        cur_width = hwp_width_int
        cur_height = hwp_height_int
        
        center_x = cur_width // 2
        center_y = cur_height // 2
        
        # 스케일 비율 계산 (소수점 5자리까지 포맷팅)
        scale_x_val = cur_width / ori_width if ori_width > 0 else 1.0
        scale_y_val = cur_height / ori_height if ori_height > 0 else 1.0
        scale_x = f"{scale_x_val:.5f}"
        scale_y = f"{scale_y_val:.5f}"
        
        # 표 내부 그림과 본문 그림에 따른 분기 속성 설정
        if is_table:
            # 표 내부 그림: 글자처럼 취급 (안정성 증대 및 뷰어 팅김 방지)
            treat_as_char = "true"
            flow_with_text = "false"
            width_rel_to = "Absolute"
            height_rel_to = "Absolute"
            horz_align = "Center"
        else:
            # 본문 그림: 안전한 기존 스펙 및 글자처럼 취급
            treat_as_char = "true"
            flow_with_text = "false"
            width_rel_to = "Absolute"
            height_rel_to = "Absolute"
            horz_align = "Left"
            
        xml_template = f"""<PICTURE Reverse="false" Width="{cur_width}" Height="{cur_height}">
  <SHAPEOBJECT InstId="{inst_id}" Lock="false" NumberingType="Figure" TextWrap="TopAndBottom" ZOrder="1">
    <SIZE Height="{cur_height}" HeightRelTo="{height_rel_to}" Protect="false" Width="{cur_width}" WidthRelTo="{width_rel_to}" />
    <POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="{flow_with_text}" HoldAnchorAndSO="false" HorzAlign="{horz_align}" HorzOffset="0" HorzRelTo="Column" TreatAsChar="{treat_as_char}" VertAlign="Top" VertOffset="0" VertRelTo="Para" />
    <OUTSIDEMARGIN Bottom="0" Left="0" Right="0" Top="0" />
# MISSING LINE 951
# MISSING LINE 952
# MISSING LINE 953
# MISSING LINE 954
# MISSING LINE 955
# MISSING LINE 956
# MISSING LINE 957
# MISSING LINE 958
# MISSING LINE 959
# MISSING LINE 960
# MISSING LINE 961
# MISSING LINE 962
# MISSING LINE 963
# MISSING LINE 964
# MISSING LINE 965
# MISSING LINE 966
# MISSING LINE 967
# MISSING LINE 968
# MISSING LINE 969
# MISSING LINE 970
# MISSING LINE 971
# MISSING LINE 972
# MISSING LINE 973
# MISSING LINE 974
# MISSING LINE 975
# MISSING LINE 976
# MISSING LINE 977
# MISSING LINE 978
# MISSING LINE 979
# MISSING LINE 980
# MISSING LINE 981
# MISSING LINE 982
# MISSING LINE 983
# MISSING LINE 984
# MISSING LINE 985
# MISSING LINE 986
# MISSING LINE 987
# MISSING LINE 988
# MISSING LINE 989
# MISSING LINE 990
# MISSING LINE 991
# MISSING LINE 992
# MISSING LINE 993
# MISSING LINE 994
# MISSING LINE 995
# MISSING LINE 996
# MISSING LINE 997
# MISSING LINE 998
# MISSING LINE 999
# MISSING LINE 1000
# MISSING LINE 1001
# MISSING LINE 1002
# MISSING LINE 1003
# MISSING LINE 1004
# MISSING LINE 1005
# MISSING LINE 1006
# MISSING LINE 1007
# MISSING LINE 1008
# MISSING LINE 1009
# MISSING LINE 1010
# MISSING LINE 1011
# MISSING LINE 1012
# MISSING LINE 1013
# MISSING LINE 1014
# MISSING LINE 1015
# MISSING LINE 1016
# MISSING LINE 1017
# MISSING LINE 1018
# MISSING LINE 1019
# MISSING LINE 1020
# MISSING LINE 1021
# MISSING LINE 1022
# MISSING LINE 1023