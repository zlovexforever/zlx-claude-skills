#!/usr/bin/env python3
"""
screenshot_pages.py - 将 PDF 指定页面渲染为高清图片

依赖：pymupdf（pip install pymupdf）

用法：
  python screenshot_pages.py <PDF路径> --pages 1,3,5 --output-dir ./output/screenshots --dpi 150

输出：
  ./output/screenshots/page_001.png
  ./output/screenshots/page_003.png
  ...
  并打印 JSON 格式的文件清单到 stdout
"""

import sys
import json
import argparse
from pathlib import Path


def render_pages(pdf_path: str, pages: list[int], output_dir: str, dpi: int) -> list[dict]:
    try:
        import fitz
    except ImportError:
        print("需要安装 pymupdf：pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    total = len(doc)
    results = []

    mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 dpi 是 PDF 基准

    for page_num in pages:
        if page_num < 1 or page_num > total:
            print(f"警告：第 {page_num} 页不存在（共 {total} 页），跳过", file=sys.stderr)
            continue

        page = doc[page_num - 1]  # 0-indexed
        pix = page.get_pixmap(matrix=mat)
        out_path = out_dir / f"page_{page_num:03d}.png"
        pix.save(str(out_path))

        results.append({
            "page": page_num,
            "file": str(out_path),
            "width_px": pix.width,
            "height_px": pix.height
        })
        print(f"  已渲染第 {page_num} 页 → {out_path}", file=sys.stderr)

    doc.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="PDF 页面截图工具")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("--pages", required=True,
                        help="要截图的页码，逗号分隔，如 1,3,5")
    parser.add_argument("--output-dir", default="./output/screenshots",
                        help="截图输出目录（默认 ./output/screenshots）")
    parser.add_argument("--dpi", type=int, default=150,
                        help="渲染分辨率（默认 150 dpi，朋友圈展示用，建议 120-200）")
    args = parser.parse_args()

    if not Path(args.pdf_path).exists():
        print(f"错误：PDF 文件不存在：{args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        pages = [int(p.strip()) for p in args.pages.split(",") if p.strip()]
    except ValueError:
        print("错误：--pages 格式不正确，请用逗号分隔的数字，如 1,3,5", file=sys.stderr)
        sys.exit(1)

    print(f"正在渲染 {len(pages)} 页，DPI={args.dpi}...", file=sys.stderr)
    results = render_pages(args.pdf_path, pages, args.output_dir, args.dpi)

    # stdout 输出 JSON 供调用方解析
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
