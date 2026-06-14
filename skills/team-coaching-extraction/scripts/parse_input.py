#!/usr/bin/env python3
"""
团队教练材料多格式解析脚本

支持格式：.txt, .md, .docx, .pdf
输出：统一的结构化文本，便于后续提取分析

用法：
    python parse_input.py <input_path> [options]

参数：
    input_path          输入文件路径或包含材料的目录

选项：
    --output, -o        输出文件路径（默认：parsed_materials.txt）
    --recursive, -r     递归处理子目录（默认：False）
    --encoding          文本文件编码（默认：utf-8）
"""

import argparse
import os
import sys
from pathlib import Path


def parse_txt(file_path: str, encoding: str = "utf-8") -> str:
    """解析纯文本文件（.txt, .md）"""
    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        return f"\n{'='*60}\nFILE: {file_path}\nTYPE: TEXT\n{'='*60}\n\n{content}"
    except UnicodeDecodeError:
        # 尝试其他编码
        for enc in ["gbk", "gb2312", "latin-1"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                return f"\n{'='*60}\nFILE: {file_path}\nTYPE: TEXT (encoding: {enc})\n{'='*60}\n\n{content}"
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法解码文件: {file_path}")


def parse_docx(file_path: str) -> str:
    """解析 Word 文档（.docx）"""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = []
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                paragraphs.append(f"[P{i+1}] {para.text}")
        content = "\n".join(paragraphs)
        return f"\n{'='*60}\nFILE: {file_path}\nTYPE: DOCX\n{'='*60}\n\n{content}"
    except ImportError:
        print("警告：未安装 python-docx，尝试使用替代方法...", file=sys.stderr)
        return parse_docx_alternative(file_path)


def parse_docx_alternative(file_path: str) -> str:
    """使用 zipfile 解析 .docx（无需外部依赖）"""
    import xml.etree.ElementTree as ET
    import zipfile

    try:
        with zipfile.ZipFile(file_path, "r") as z:
            xml_content = z.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        # Word XML命名空间
        ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        paragraphs = []
        for i, para in enumerate(tree.findall(".//w:p", ns)):
            texts = [node.text for node in para.findall(".//w:t", ns) if node.text]
            if texts:
                text = "".join(texts)
                if text.strip():
                    paragraphs.append(f"[P{i+1}] {text}")
        content = "\n".join(paragraphs)
        return f"\n{'='*60}\nFILE: {file_path}\nTYPE: DOCX (alternative parser)\n{'='*60}\n\n{content}"
    except Exception as e:
        raise RuntimeError(f"解析 DOCX 失败: {file_path} - {e}")


def parse_pdf(file_path: str) -> str:
    """解析 PDF 文件"""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(file_path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append(f"--- Page {i+1} ---\n{text.strip()}")
        content = "\n\n".join(pages)
        return f"\n{'='*60}\nFILE: {file_path}\nTYPE: PDF (pages: {len(reader.pages)})\n{'='*60}\n\n{content}"
    except ImportError:
        print("警告：未安装 PyPDF2，尝试使用替代方法...", file=sys.stderr)
        return parse_pdf_alternative(file_path)


def parse_pdf_alternative(file_path: str) -> str:
    """使用 pdfplumber 解析 PDF"""
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append(f"--- Page {i+1} ---\n{text.strip()}")
        content = "\n\n".join(pages)
        return f"\n{'='*60}\nFILE: {file_path}\nTYPE: PDF (pdfplumber)\n{'='*60}\n\n{content}"
    except ImportError:
        raise RuntimeError(
            f"解析 PDF 需要 PyPDF2 或 pdfplumber。请安装其中之一：\n"
            f"  pip install PyPDF2    # 或\n"
            f"  pip install pdfplumber"
        )


def get_parser(file_path: str) -> callable:
    """根据文件扩展名返回对应的解析函数"""
    ext = Path(file_path).suffix.lower()
    parsers = {
        ".txt": parse_txt,
        ".md": parse_txt,
        ".markdown": parse_txt,
        ".docx": parse_docx,
        ".pdf": parse_pdf,
    }
    if ext not in parsers:
        raise ValueError(f"不支持的文件格式: {ext} (文件: {file_path})")
    return parsers[ext]


def collect_files(input_path: str, recursive: bool = False) -> list:
    """收集输入路径下的所有支持文件"""
    path = Path(input_path)
    supported_exts = {".txt", ".md", ".markdown", ".docx", ".pdf"}

    if path.is_file():
        if path.suffix.lower() in supported_exts:
            return [str(path)]
        else:
            raise ValueError(f"不支持的文件格式: {path.suffix}")

    if path.is_dir():
        if recursive:
            files = [
                str(f) for f in path.rglob("*")
                if f.is_file() and f.suffix.lower() in supported_exts
            ]
        else:
            files = [
                str(f) for f in path.iterdir()
                if f.is_file() and f.suffix.lower() in supported_exts
            ]
        files.sort()
        return files

    raise ValueError(f"输入路径不存在: {input_path}")


def main():
    parser = argparse.ArgumentParser(
        description="解析团队教练材料（多格式）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python parse_input.py ./materials/team_docs/
  python parse_input.py ./interview.docx -o output.txt
  python parse_input.py ./mixed_files/ -r -o all_materials.txt
        """
    )
    parser.add_argument("input_path", help="输入文件路径或目录")
    parser.add_argument("-o", "--output", default="parsed_materials.txt",
                        help="输出文件路径 (默认: parsed_materials.txt)")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="递归处理子目录")
    parser.add_argument("--encoding", default="utf-8",
                        help="文本文件编码 (默认: utf-8)")

    args = parser.parse_args()

    # 收集文件
    try:
        files = collect_files(args.input_path, args.recursive)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if not files:
        print("警告: 未找到支持格式的文件", file=sys.stderr)
        sys.exit(0)

    print(f"发现 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f}")

    # 解析所有文件
    parsed_contents = []
    failed_files = []

    for file_path in files:
        try:
            parser_fn = get_parser(file_path)
            if parser_fn == parse_txt:
                content = parser_fn(file_path, args.encoding)
            else:
                content = parser_fn(file_path)
            parsed_contents.append(content)
            print(f"  [OK] {file_path}")
        except Exception as e:
            failed_files.append((file_path, str(e)))
            print(f"  [FAILED] {file_path}: {e}", file=sys.stderr)

    # 写入输出
    header = f"""# 团队教练材料 — 解析结果

> 解析时间: {os.path.basename(__file__)}
> 文件数量: {len(files)}
> 成功: {len(parsed_contents)}
> 失败: {len(failed_files)}

"""

    if failed_files:
        header += "## 解析失败的文件\n\n"
        for fp, err in failed_files:
            header += f"- {fp}: {err}\n"
        header += "\n---\n"

    output_content = header + "\n\n".join(parsed_contents)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"\n解析完成！输出文件: {args.output}")
    print(f"  总计: {len(files)} 个文件")
    print(f"  成功: {len(parsed_contents)} 个")
    print(f"  失败: {len(failed_files)} 个")


if __name__ == "__main__":
    main()
