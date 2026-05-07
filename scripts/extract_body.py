"""
Extract body text paragraphs from a .docx thesis file.
Skips: headings, TOC, captions, images, keywords, references, acknowledgements, cover pages.
Output: JSON array of {index, style, text} for paragraphs that need rewriting.
"""
import json, sys
from docx import Document
from docx.oxml.ns import qn


def extract_body_paragraphs(docx_path: str, output_path: str) -> list[dict]:
    doc = Document(docx_path)

    # Styles to skip entirely
    skip_styles = {'Heading 1', 'Heading 2', 'Heading 3', 'Caption',
                   'toc 1', 'toc 2', 'toc 3', 'TOC Heading'}

    # Paragraph index ranges to skip (cover pages, TOC)
    skip_ranges = [(0, 60), (61, 105)]  # cover + TOC — adjust per document

    # Paragraphs judged by content patterns
    ref_start = -1
    ack_start = -1

    body_paragraphs = []

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue

        # Detect "参考文献" heading to mark reference section start
        if para.style.name == 'Heading 1' and ('参考' in text or '文献' in text):
            ref_start = i
            continue
        # Detect "致谢" heading
        if para.style.name == 'Heading 1' and ('致谢' in text or '谢' in text):
            ack_start = i
            continue

        # Skip by style
        if para.style.name in skip_styles:
            continue

        # Skip by range
        skip = False
        for start, end in skip_ranges:
            if start <= i <= end:
                skip = True
                break
        if skip:
            continue

        # Skip keywords
        if text.startswith('关键词') or text.startswith('Key words') or text.startswith('Keywords'):
            continue

        # Skip references (after 参考文献 heading until end or 致谢)
        if ref_start > 0 and i > ref_start:
            if ack_start > 0 and i >= ack_start:
                pass  # fall through to body check
            else:
                continue

        # Skip acknowledgements
        if ack_start > 0 and i >= ack_start:
            continue

        # Skip image-only paragraphs
        has_image = False
        for run in para.runs:
            drawings = run._element.findall('.//' + qn('w:drawing'))
            if drawings:
                has_image = True
                break
        if has_image and len(text) < 5:
            continue

        body_paragraphs.append({
            'index': i,
            'style': para.style.name,
            'text': text
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(body_paragraphs, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(body_paragraphs)} body paragraphs -> {output_path}")
    return body_paragraphs


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_body.py <input.docx> <output.json>")
        sys.exit(1)
    extract_body_paragraphs(sys.argv[1], sys.argv[2])
