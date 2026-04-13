#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
作品报告生成脚本 - 使用ElementTree精确操作XML
"""

import os
import sys
import subprocess
from xml.etree import ElementTree as ET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, 'C:/Users/22721/.claude/skills/docx')

from config import PROJECT_NAME, FILL_DATE, CONTENT, REPLACEMENTS

TEMPLATE_PATH = os.path.join(REPORT_DIR, 'backup/report-backup1.docx')
UNPACKED_DIR = os.path.join(SCRIPT_DIR, 'unpacked')
OUTPUT_PATH = os.path.join(REPORT_DIR, 'report.docx')

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def encode(text):
    return ''.join(f'&#{ord(c)};' if ord(c) > 127 else c for c in text)


def decode_entity(text):
    import re
    def replace(m):
        return chr(int(m.group(1)))
    return re.sub(r'&#(\d+);', replace, text)


def register_namespaces():
    """注册所有命名空间"""
    ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    ET.register_namespace('w14', 'http://schemas.microsoft.com/office/word/2010/wordml')
    ET.register_namespace('wp', 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
    ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    ET.register_namespace('mc', 'http://schemas.openxmlformats.org/markup-compatibility/2006')


def get_para_text(para):
    """获取段落文本"""
    texts = []
    for t in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text:
            texts.append(t.text)
    return decode_entity(''.join(texts))


def create_content_paragraph(text, chapter_num=None):
    """创建内容段落（支持二级/三级标题，正文首行缩进两字符，列表项和参考文献顶格，图片说明居中）"""
    import re
    paragraphs = []
    lines = text.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        w_p = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
        w_pPr = ET.SubElement(w_p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
        w_pStyle = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pStyle')

        # 检测二级标题：短行（<=20字符）、不以句号逗号等结尾、不是纯数字
        is_heading = (
            len(stripped) <= 20 and
            not stripped.endswith(('。', '，', '、', '；', '：', '！', '？', '.', ',', ';', ':', '!', '?')) and
            not stripped.isdigit() and
            len(stripped) >= 2  # 至少2个字符
        )

        # 检测列表项：以（数字）开头
        is_list_item = re.match(r'^（[0-9]+）', stripped) is not None

        # 检测参考文献：以[数字]开头
        is_reference = re.match(r'^\[[0-9]+\]', stripped) is not None

        # 检测图片说明：以【图开头（必须先于标题检测）
        is_figure = re.match(r'^【图[0-9]+-[0-9]+', stripped) is not None

        # 注意：图片说明检测必须先于标题检测，否则短图片说明会被误判为标题
        if is_figure:
            # 图片说明：居中显示，5号宋体
            w_pStyle.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'a0')
            # 设置居中对齐
            w_jc = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}jc')
            w_jc.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'center')
            # 取消首行缩进
            w_ind = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine', '0')
            # 设置段前段后间距
            w_spacing = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}spacing')
            w_spacing.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}before', '100')
            w_spacing.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}after', '100')
        elif is_heading:
            w_pStyle.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '2')
        elif is_reference:
            # 参考文献：顶格、5号楷体、1倍行距
            w_pStyle.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'a0')
            w_ind = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine', '0')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLineChars', '0')
            # 设置行距为单倍行距
            w_spacing = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}spacing')
            w_spacing.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}line', '240')
            w_spacing.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lineRule', 'auto')
        elif is_list_item:
            # 列表项使用正文样式但明确设置缩进为0（顶格）
            w_pStyle.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'a0')
            w_ind = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine', '0')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLineChars', '0')
        else:
            # 正文样式，首行缩进两字符
            w_pStyle.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'a0')
            w_ind = ET.SubElement(w_pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ind')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLine', '480')
            w_ind.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}firstLineChars', '200')

        w_r = ET.SubElement(w_p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
        w_rPr = ET.SubElement(w_r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
        w_rFonts = ET.SubElement(w_rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
        w_rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hint', 'eastAsia')

        # 参考文献使用楷体5号
        if is_reference:
            w_rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii', '楷体')
            w_rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi', '楷体')
            w_rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia', '楷体')
            # 5号字 = 10.5磅 = 21 half-points
            w_sz = ET.SubElement(w_rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz')
            w_sz.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '21')
            w_szCs = ET.SubElement(w_rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}szCs')
            w_szCs.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '21')

        # 图片说明使用5号宋体
        if is_figure:
            # 5号字 = 10.5磅 = 21 half-points
            w_sz = ET.SubElement(w_rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz')
            w_sz.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '21')
            w_szCs = ET.SubElement(w_rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}szCs')
            w_szCs.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '21')

        w_t = ET.SubElement(w_r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
        # 图片说明去掉【】括号
        if is_figure:
            # 去掉首尾的【和】
            w_t.text = re.sub(r'^【(.+)】$', r'\1', stripped)
        else:
            w_t.text = stripped
        paragraphs.append(w_p)
    return paragraphs


def unpack_template():
    print("解包模板...")
    result = subprocess.run([
        'python', 'C:/Users/22721/.claude/skills/docx/ooxml/scripts/unpack.py',
        TEMPLATE_PATH, UNPACKED_DIR
    ], capture_output=True, text=True)
    return result.returncode == 0


def pack_document():
    print("打包文档...")
    result = subprocess.run([
        'python', 'C:/Users/22721/.claude/skills/docx/ooxml/scripts/pack.py',
        UNPACKED_DIR, OUTPUT_PATH
    ], capture_output=True, text=True)
    return result.returncode == 0


def process_document():
    print("处理文档...")
    register_namespaces()

    xml_path = os.path.join(UNPACKED_DIR, 'word/document.xml')
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 1. 修改封面
    print("  修改封面...")
    for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text and '　' in t.text and len(t.text) > 30:  # 全角空格重复多次
            if PROJECT_NAME not in t.text:
                t.text = t.text.replace('　' * 19, PROJECT_NAME, 1)
                print("    [OK] 填写作品名称")
                break

    for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text and '　' in t.text and len(t.text) > 30:
            t.text = t.text.replace('　' * 19, FILL_DATE, 1)
            print("    [OK] 填写日期")
            break

    # 2. 替换章节内容
    print("  替换章节内容...")
    body = root.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
    replaced = 0

    for keyword, content_key in REPLACEMENTS:
        for para in list(body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')):
            text = get_para_text(para)
            if keyword in text:
                # 找到父元素
                parent = None
                for p in root.iter():
                    if para in list(p):
                        parent = p
                        break

                if parent is not None:
                    # 创建新段落列表
                    new_paras = create_content_paragraph(CONTENT[content_key])
                    # 找到位置并替换
                    idx = list(parent).index(para)
                    parent.remove(para)
                    # 插入多个段落
                    for i, new_para in enumerate(new_paras):
                        parent.insert(idx + i, new_para)
                    replaced += 1
                    print(f"    [OK] 替换: {keyword[:10]}...")

                    # 第6章特殊处理：删除后续的空二级标题
                    if content_key == 'chapter_6':
                        empty_headings_ch6 = ['作品特色与创新', '应用推广', '作品展望']
                        deleted_count = 0
                        # 检查后续段落
                        for j in range(idx + len(new_paras), min(idx + len(new_paras) + 10, len(list(parent)))):
                            sibling = list(parent)[j] if j < len(list(parent)) else None
                            if sibling is not None:
                                sibling_text = get_para_text(sibling)
                                if sibling_text in empty_headings_ch6 or (len(sibling_text) <= 12 and sibling_text in empty_headings_ch6):
                                    parent.remove(sibling)
                                    deleted_count += 1
                                    print(f"    [DEL-CH6] 删除空标题: {sibling_text}")
                        if deleted_count > 0:
                            print(f"    [CH6] 共删除 {deleted_count} 个模板空标题")
                    break

    print(f"  共替换 {replaced} 个段落")

    # 3. 删除示例段落
    print("  删除示例段落...")
    deleted = 0
    example_keywords = [
        '二级标题示例', '三级标题示例', '正文示例',
        '所有图片必须有', '所有表格必须有',
        '图 1  图文说明', '表 1  表格说明', '以上所有示例',
        # 第6章残留的模板标题
        '作品特色与创新',
    ]
    # 第6章模板预设的空二级标题（完全匹配删除）
    empty_headings = ['作品特色与创新', '应用推广', '作品展望']

    # 收集要删除的段落
    to_delete = []
    for para in list(body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')):
        text = get_para_text(para)
        # 检查包含关键词
        for kw in example_keywords:
            if kw in text:
                to_delete.append(para)
                print(f"    [DEL] 标记删除: {kw}")
                break
        else:
            # 检查完全匹配的空标题（模板中的空标题）
            if len(text) <= 12 and text in empty_headings:
                to_delete.append(para)
                print(f"    [DEL] 标记删除空标题: {text}")

    # 删除段落
    for para in to_delete:
        for parent in root.iter():
            if para in list(parent):
                parent.remove(para)
                deleted += 1
                break

    print(f"  共删除 {deleted} 个示例段落")

    # 4. 删除示例表格
    print("  删除示例表格...")
    tbl_deleted = 0
    for tbl in list(body.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl')):
        # 检查表格内容是否为示例
        first_row_text = []
        for cell in tbl.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc'):
            cell_texts = []
            for t in cell.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    cell_texts.append(t.text)
            first_row_text.append(''.join(cell_texts))

        # 示例表格特征：首行包含"首列"或"内容"
        is_example = any('首列' in t or '内容' in t or '索引' in t for t in first_row_text)
        if is_example:
            body.remove(tbl)
            tbl_deleted += 1
            print(f"    [DEL] 删除示例表格")

    print(f"  共删除 {tbl_deleted} 个示例表格")

    # 5. 删除示例图片（已禁用：新模板已处理好图片）
    print("  检查示例图片...")
    img_deleted = 0
    # 新模板（backup/report-backup1.docx）已包含正确的截图，不再需要删除示例图片

    print(f"  无需删除示例图片")

    # 保存
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)


def main():
    print("=" * 50)
    print("作品报告生成器")
    print("=" * 50)

    if os.path.exists(UNPACKED_DIR):
        import shutil
        shutil.rmtree(UNPACKED_DIR)

    if not unpack_template():
        print("解包失败!")
        return 1

    process_document()

    if not pack_document():
        print("打包失败!")
        return 1

    print("=" * 50)
    print(f"完成! 输出文件: {OUTPUT_PATH}")
    print("=" * 50)
    return 0


if __name__ == '__main__':
    sys.exit(main())