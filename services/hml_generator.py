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

        self.sup_map = {}
        self.sub_map = {}
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
                
                # 1. 위첨자용 (ID = new_count)
                super_cs = copy.deepcopy(cs)
                super_id = str(new_count)
                super_cs.set('Id', super_id)
                self.sup_map[old_id] = super_id
                relsize = super_cs.find('RELSIZE')
                if relsize is not None:
                    for lang in relsize.attrib:
                        relsize.set(lang, '70')
                charoffset = super_cs.find('CHAROFFSET')
                if charoffset is not None:
                    for lang in charoffset.attrib:
                        charoffset.set(lang, '33')
                if super_cs.find('SUPERSCRIPT') is None:
                    ET.SubElement(super_cs, 'SUPERSCRIPT')
                charshape_list.append(super_cs)
                new_count += 1
                
                # 2. 아래첨자용 (ID = new_count)
                sub_cs = copy.deepcopy(cs)
                sub_id = str(new_count)
                sub_cs.set('Id', sub_id)
                self.sub_map[old_id] = sub_id
                relsize = sub_cs.find('RELSIZE')
                if relsize is not None:
                    for lang in relsize.attrib:
                        relsize.set(lang, '70')
                charoffset = sub_cs.find('CHAROFFSET')
                if charoffset is not None:
                    for lang in charoffset.attrib:
                        charoffset.set(lang, '-15')
                if sub_cs.find('SUBSCRIPT') is None:
                    ET.SubElement(sub_cs, 'SUBSCRIPT')
                charshape_list.append(sub_cs)
                new_count += 1
                
            charshape_list.set('Count', str(new_count))

        self.image_cache = {}

    def replace_placeholders(self, code: str, name: str, code_type: str = ""):
        for node in self.root.iter():
            if node.text:
                if '[코드]' in node.text:
                    node.text = node.text.replace('[코드]', code)
                if '[공종]' in node.text:
                    node.text = node.text.replace('[공종]', name)
                if '[문서타입]' in node.text:
                    node.text = node.text.replace('[문서타입]', code_type)
            if node.tail:
                if '[코드]' in node.tail:
                    node.tail = node.tail.replace('[코드]', code)
                if '[공종]' in node.tail:
                    node.tail = node.tail.replace('[공종]', name)
                if '[문서타입]' in node.tail:
                    node.tail = node.tail.replace('[문서타입]', code_type)

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
            if target_p is not None:
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
                        current_block = []
                    blocks.append([child])
                else:
                    current_block.append(child)
            if current_block:
                blocks.append(current_block)
                
            for block_nodes in blocks:
                p = ET.Element('P', {'Style': str(s_info['Id']), 'ParaShape': str(s_info['ParaShape'])})
                
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
                                cur_shape = getattr(self, 'sup_map', {}).get(char_shape, char_shape)
                            elif token['sub']:
                                cur_shape = getattr(self, 'sub_map', {}).get(char_shape, char_shape)
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
                    
                    # Parse cell to inline tokens to preserve formatting like sub/sup
                    tokens = parse_html_to_inline_tokens(cell)
                    tokens = clean_and_merge_tokens(tokens)
                    
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
                    
                    required_height = 282 + 500  # 기본 높이 + 약간의 여백
                    
                    # Detect if note cell
                    raw_text = "".join([t['text'] for t in tokens if t['type'] == 'text'])
                    is_note_cell = False
                    if raw_text:
                        import re
                        stripped_text = raw_text.strip()
                        if re.match(r'^\s*(주|기호|참고)(?:\s*\d*\)|\s*\]|\s*:|\s)', stripped_text):
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
                        style_id = s_info.get('Id', '12')
                        char_shape = s_info.get('CharShape', '7')
                        
                    cell_max_width = (cell_width * cell_info['colspan']) - 1000
                    
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
                            
                    # 만약 텍스트도 없고 이미지도 (초소형이라) 필터링되었다면, PARALIST에는 최소 1개의 P 태그가 필수입니다.
                    if len(list(paralist)) == 0:
                        s_info_base = style_map.get('KCSC_표_본문', {'Id': '11', 'ParaShape': '16', 'CharShape': '2'})
                        p_empty = ET.SubElement(paralist, 'P', {'ParaShape': s_info_base.get('ParaShape', '16'), 'Style': s_info_base.get('Id', '11')})
                        text_empty = ET.SubElement(p_empty, 'TEXT', {'CharShape': s_info_base.get('CharShape', '2')})
                        ET.SubElement(text_empty, 'CHAR')
            
            return table
        except Exception as e:
            print(f"Error building HML table: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_hml_picture(self, html_img_str: str, max_width: int = None, is_table: bool = False):
        import xml.etree.ElementTree as ET
        import re
        import base64
        import io
        
        match = re.search(r"<img([^>]+)>", html_img_str, re.IGNORECASE)
        if not match:
            return None
        img_attrs = match.group(1)
        
        src_match = re.search(r"src=['\"]([^'\"]+)['\"]", img_attrs, re.IGNORECASE)
        if not src_match:
            return None
        src = src_match.group(1)
        
        width_attr_match = re.search(r"width=['\"]?(\d+)['\"]?", img_attrs, re.IGNORECASE)
        height_attr_match = re.search(r"height=['\"]?(\d+)['\"]?", img_attrs, re.IGNORECASE)
        
        # CSS style 속성에서도 width/height를 폴백으로 추출
        if not width_attr_match:
            style_w = re.search(r"style=['\"][^'\"]*width\s*:\s*(\d+)", img_attrs, re.IGNORECASE)
            if style_w:
                width_attr_match = style_w
        if not height_attr_match:
            style_h = re.search(r"style=['\"][^'\"]*height\s*:\s*(\d+)", img_attrs, re.IGNORECASE)
            if style_h:
                height_attr_match = style_h
        
        b64_data = ""
        img_format = "png"
        width_px, height_px = 200, 150
        
        # Base64 데이터 추출
        if src.startswith('data:image/'):
            parts = src.split(';base64,')
            if len(parts) == 2:
                img_format = parts[0].replace('data:image/', '').split(';')[0].lower()
                if img_format == 'jpeg': img_format = 'jpg'
                b64_data = parts[1]
                
                try:
                    from PIL import Image
                    image_bytes = base64.b64decode(b64_data)
                    with Image.open(io.BytesIO(image_bytes)) as img:
                        width_px, height_px = img.size
                except Exception as e:
                    print(f"Error parsing image dimensions: {e}")
        else:
            # 일반 URL인 경우 폴백 로직
            try:
                import urllib.request
                from PIL import Image
                req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    image_bytes = response.read()
                b64_data = base64.b64encode(image_bytes).decode('utf-8')
                with Image.open(io.BytesIO(image_bytes)) as img:
                    width_px, height_px = img.size
                    img_format = img.format.lower() if img.format else "png"
                    if img_format == 'jpeg': img_format = 'jpg'
            except Exception as e:
                print(f"Error fetching image from URL: {e}")
                return None
                
        if not b64_data:
            return None
            
        if width_attr_match and height_attr_match:
            width_px = int(width_attr_match.group(1))
            height_px = int(height_attr_match.group(1))
        elif width_attr_match and not height_attr_match:
            html_w = int(width_attr_match.group(1))
            if width_px > 0:
                height_px = int(height_px * (html_w / width_px))
            width_px = html_w
        elif height_attr_match and not width_attr_match:
            html_h = int(height_attr_match.group(1))
            if height_px > 0:
                width_px = int(width_px * (html_h / height_px))
            height_px = html_h
        
        # 이미지 중복 등록 방지 (캐시 확인)
        if b64_data in self.image_cache:
            bin_id = self.image_cache[b64_data]
        else:
            mapping_table = self.root.find('.//MAPPINGTABLE')
            if mapping_table is None:
                head = self.root.find('.//HEAD')
                if head is None: return None
                mapping_table = ET.SubElement(head, 'MAPPINGTABLE')
                
            bindatalist = mapping_table.find('BINDATALIST')
            if bindatalist is None:
                bindatalist = ET.Element('BINDATALIST', {'Count': '0'})
                mapping_table.insert(0, bindatalist)
                
            count = int(bindatalist.get('Count', '0'))
            bin_id = str(count + 1)
            bindatalist.set('Count', bin_id)
            
            ET.SubElement(bindatalist, 'BINITEM', {
                'BinData': bin_id,
                'Format': img_format,
                'Type': 'Embedding'
            })
            
            tail = self.root.find('.//TAIL')
            if tail is None:
                tail = ET.SubElement(self.root, 'TAIL')
                
            bindatastorage = tail.find('BINDATASTORAGE')
            if bindatastorage is None:
                bindatastorage = ET.Element('BINDATASTORAGE')
                tail.insert(0, bindatastorage)
                
            import base64 as b64_lib
            try:
                data_bytes = b64_lib.b64decode(b64_data)
                size_in_bytes = str(len(data_bytes))
            except Exception:
                size_in_bytes = "0"
                
            bindata_el = ET.SubElement(bindatastorage, 'BINDATA', {
                'Id': bin_id,
                'Size': size_in_bytes,
                'Encoding': 'Base64'
            })
            bindata_el.text = b64_data
            
            # 캐시에 저장
            self.image_cache[b64_data] = bin_id

        
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
    <SHAPECOMMENT>그림입니다.</SHAPECOMMENT>
  </SHAPEOBJECT>
  <SHAPECOMPONENT CurHeight="{cur_height}" CurWidth="{cur_width}" GroupLevel="0" HorzFlip="false" InstID="{comp_inst_id}" OriHeight="{ori_height}" OriWidth="{ori_width}" VertFlip="false" XPos="0" YPos="0">
    <ROTATIONINFO Angle="0" CenterX="{center_x}" CenterY="{center_y}" />
    <RENDERINGINFO>
      <TRANSMATRIX E1="1.00000" E2="0.00000" E3="0.00000" E4="0.00000" E5="1.00000" E6="0.00000" />
      <SCAMATRIX E1="{scale_x}" E2="0.00000" E3="0.00000" E4="0.00000" E5="{scale_y}" E6="0.00000" />
      <ROTMATRIX E1="1.00000" E2="0.00000" E3="0.00000" E4="0.00000" E5="1.00000" E6="0.00000" />
    </RENDERINGINFO>
  </SHAPECOMPONENT>
  <IMAGERECT X0="0" X1="{ori_width}" X2="{ori_width}" X3="0" Y0="0" Y1="0" Y2="{ori_height}" Y3="{ori_height}" />
  <IMAGECLIP Bottom="{ori_height}" Left="0" Right="{ori_width}" Top="0" />
  <INSIDEMARGIN Bottom="0" Left="0" Right="0" Top="0" />
  <IMAGE Alpha="0" BinItem="{bin_id}" Bright="0" Contrast="0" Effect="RealPic" />
  <EFFECTS />
</PICTURE>"""

        picture = ET.fromstring(xml_template)
        return picture


    def _format_table_note_text(self, text: str) -> str:
        import re
        # Clean up existing newlines to make line breaking predictable
        text = re.sub(r'\s*\n\s*', ' ', text)
        
        # Pattern to find note item markers:
        # - \d+\)
        # - \(\d+\)
        # - Circle numbers: [①-⑮]
        # - labels: (기호|참고|주)\]
        pattern = r'(\d+\)|\(\d+\)|[①-⑮]|(?:기호|참고|주)\])'
        
        matches = list(re.finditer(pattern, text))
        if not matches:
            return text

        result = []
        last_end = 0
        
        for i, match in enumerate(matches):
            start, end = match.start(), match.end()
            marker = match.group(1)
            
            between = text[last_end:start]
            
            if i == 0:
                result.append(between)
                result.append(marker)
            else:
                if between.strip() == "":
                    result.append(between)
                    result.append(marker)
                else:
                    rstripped_between = between.rstrip()
                    result.append(rstripped_between)
                    result.append("\n")
                    result.append(marker)
                    
            last_end = end
            
        result.append(text[last_end:])
        
        # Clean up leading/trailing whitespaces on each line
        final_text = "".join(result)
        lines = [line.strip() for line in final_text.split('\n')]
        return "\n".join(lines)

    def save(self, output_path: str):
        import xml.etree.ElementTree as ET
        tree = ET.ElementTree(self.root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
