import sys
import os
from pypdf import PdfReader, PdfWriter


def parse_page_ranges(page_ranges_str):
    """
    يحول سلسلة مثل "1,3,5-7" إلى قائمة أرقام صفحات (0-based)
    """
    pages = set()
    for part in page_ranges_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.update(range(int(start)-1, int(end)))
        else:
            pages.add(int(part)-1)
    return sorted(pages)


def extract_pages(input_pdf, page_ranges):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page_num in page_ranges:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    return writer


def delete_pages(input_pdf, pages_to_delete):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    pages_to_delete = set(pages_to_delete)
    for i in range(total_pages):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])
    return writer


def merge_pdfs(pdfs_with_pages, output_pdf):
    writer = PdfWriter()
    for pdf_path, page_ranges in pdfs_with_pages:
        reader = PdfReader(pdf_path)
        for page_num in page_ranges:
            if 0 <= page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    print(f"تم إنشاء الملف: {output_pdf}")


def main():
    print("برنامج فصل ودمج صفحات PDF")
    print("----------------------------------")
    print("اختر العملية:")
    print("1. استخراج صفحات من ملف PDF")
    print("2. حذف صفحات من ملف PDF")
    print("3. دمج صفحات من عدة ملفات PDF")
    choice = input("أدخل رقم العملية: ").strip()

    if choice == '1':
        pdf_path = input("أدخل مسار ملف PDF: ").strip()
        page_ranges_str = input("أدخل أرقام الصفحات المطلوبة (مثال: 1,3,5-7): ").strip()
        output_path = input("أدخل اسم ملف الإخراج: ").strip()
        page_ranges = parse_page_ranges(page_ranges_str)
        writer = extract_pages(pdf_path, page_ranges)
        with open(output_path, 'wb') as f:
            writer.write(f)
        print(f"تم استخراج الصفحات إلى: {output_path}")

    elif choice == '2':
        pdf_path = input("أدخل مسار ملف PDF: ").strip()
        page_ranges_str = input("أدخل أرقام الصفحات التي تريد حذفها (مثال: 2,4,6-8): ").strip()
        output_path = input("أدخل اسم ملف الإخراج: ").strip()
        pages_to_delete = parse_page_ranges(page_ranges_str)
        writer = delete_pages(pdf_path, pages_to_delete)
        with open(output_path, 'wb') as f:
            writer.write(f)
        print(f"تم حذف الصفحات وحفظ الملف في: {output_path}")

    elif choice == '3':
        pdfs_with_pages = []
        while True:
            pdf_path = input("أدخل مسار ملف PDF (أو اتركه فارغًا للانتهاء): ").strip()
            if not pdf_path:
                break
            page_ranges_str = input("أدخل أرقام الصفحات المطلوبة من هذا الملف (مثال: 1,3,5-7): ").strip()
            page_ranges = parse_page_ranges(page_ranges_str)
            pdfs_with_pages.append((pdf_path, page_ranges))
        output_path = input("أدخل اسم ملف الإخراج: ").strip()
        merge_pdfs(pdfs_with_pages, output_path)
    else:
        print("خيار غير صحيح!")

if __name__ == "__main__":
    main() 